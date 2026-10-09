import csv
from decimal import Decimal, InvalidOperation
from io import BytesIO, StringIO
import time

from django.core.paginator import Paginator, EmptyPage
from django.db import connection
from django.db.models import Sum, Count, Avg, Q
from django.db.models.functions import Coalesce
from django.http import FileResponse, HttpResponse
from django.utils import timezone

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import Card, User
from accounts.audit import record_audit_log

from .models import Transaction, FraudLog, APIMetricLog
from .serializers import (
    TransactionSerializer,
    FraudLogSerializer,
    APIMetricLogSerializer,
)
from .email_service import (
    send_transaction_alert,
    send_low_credit_alert,
    send_fraud_alert_email,
)
from .fraud_service import (
    evaluate_transaction_fraud,
    record_fraud_log,
    extract_request_metadata,
)


# ============================================================
# TRANSACTION HISTORY WITH ADVANCED SEARCH & PAGINATION
# ============================================================

class TransactionHistoryView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        show_all = self.request.query_params.get("all") == "true"
        target_user_id = self.request.query_params.get("user_id")

        # Staff can inspect all transactions or filter by user
        if (
            self.request.user.is_admin_role
            or self.request.user.is_support_role
            or self.request.user.is_read_only_role
        ) and (show_all or target_user_id):
            if target_user_id:
                queryset = Transaction.objects.filter(user_id=target_user_id)
            else:
                queryset = Transaction.objects.all()
        else:
            queryset = Transaction.objects.filter(
                user=self.request.user
            )

        queryset = queryset.select_related("card", "user")

        # 1. Status Filter
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter.upper())

        # 2. Category Filter
        category_filter = self.request.query_params.get("category")
        if category_filter:
            queryset = queryset.filter(category__iexact=category_filter)

        # 3. Fraud Status Filter
        fraud_filter = self.request.query_params.get("fraud_status")
        if fraud_filter:
            queryset = queryset.filter(fraud_status__iexact=fraud_filter)

        # 4. Amount Range Filter
        min_amount = self.request.query_params.get("min_amount")
        if min_amount:
            try:
                queryset = queryset.filter(amount__gte=Decimal(str(min_amount)))
            except (InvalidOperation, ValueError):
                pass

        max_amount = self.request.query_params.get("max_amount")
        if max_amount:
            try:
                queryset = queryset.filter(amount__lte=Decimal(str(max_amount)))
            except (InvalidOperation, ValueError):
                pass

        # 5. Exact Date Filter
        date = self.request.query_params.get("date")
        if date:
            queryset = queryset.filter(transaction_date__date=date)

        # 6. Date Range Filters (start_date / date_from, end_date / date_to)
        start_date = self.request.query_params.get("start_date") or self.request.query_params.get("date_from")
        if start_date:
            queryset = queryset.filter(transaction_date__date__gte=start_date)

        end_date = self.request.query_params.get("end_date") or self.request.query_params.get("date_to")
        if end_date:
            queryset = queryset.filter(transaction_date__date__lte=end_date)

        # 7. Card Number / Masked / Search Filter
        card_search = (
            self.request.query_params.get("search")
            or self.request.query_params.get("card_number")
            or self.request.query_params.get("masked_card")
        )
        if card_search:
            card_search = card_search.strip()
            queryset = queryset.filter(
                Q(card__masked_card_number__icontains=card_search)
                | Q(card__last_four_digits=card_search)
            )

        # 8. Server-Side Sorting
        ordering = self.request.query_params.get("sort_by") or self.request.query_params.get("ordering") or "-transaction_date"
        allowed_orderings = {
            "date_asc": "transaction_date",
            "date_desc": "-transaction_date",
            "transaction_date": "transaction_date",
            "-transaction_date": "-transaction_date",
            "amount_asc": "amount",
            "amount_desc": "-amount",
            "amount": "amount",
            "-amount": "-amount",
            "status": "status",
            "-status": "-status",
        }
        order_field = allowed_orderings.get(ordering, "-transaction_date")
        queryset = queryset.order_by(order_field)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        page_number = request.query_params.get("page")
        page_size_param = request.query_params.get("page_size")

        # If pagination parameters are explicitly requested, return paginated structure
        if page_number or page_size_param:
            try:
                page_size = int(page_size_param or 10)
                if page_size < 1 or page_size > 100:
                    page_size = 10
            except ValueError:
                page_size = 10

            paginator = Paginator(queryset, page_size)
            try:
                page_obj = paginator.page(int(page_number or 1))
            except (EmptyPage, ValueError):
                page_obj = paginator.page(1)

            serializer = self.get_serializer(page_obj.object_list, many=True)
            return Response({
                "count": paginator.count,
                "total_pages": paginator.num_pages,
                "current_page": page_obj.number,
                "page_size": page_size,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
                "results": serializer.data,
            })

        # Default flat list for backward compatibility with existing tests
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# ============================================================
# CREATE PENDING TRANSACTION (WITH FRAUD EVALUATION)
# ============================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_pending_transaction(request):
    # RBAC check: Read-Only role cannot initiate transactions
    if getattr(request.user, "role", None) == "READ_ONLY":
        return Response(
            {
                "error": "Read-Only role cannot initiate transactions"
            },
            status=status.HTTP_403_FORBIDDEN
        )

    card_id = request.data.get("card_id")
    amount = request.data.get("amount")
    category = request.data.get("category", "General")

    # --------------------------------------------------------
    # VALIDATE CARD ID
    # --------------------------------------------------------
    if not card_id:
        return Response(
            {
                "error": "card_id is required"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # --------------------------------------------------------
    # VALIDATE AMOUNT
    # --------------------------------------------------------
    if amount is None:
        return Response(
            {
                "error": "amount is required"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        amount = Decimal(str(amount))
    except (InvalidOperation, TypeError, ValueError):
        return Response(
            {
                "error": "Invalid amount"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if amount <= 0:
        return Response(
            {
                "error": "Amount must be greater than 0"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # --------------------------------------------------------
    # GET USER'S CARD
    # --------------------------------------------------------
    try:
        if request.user.is_admin_role:
            card = Card.objects.get(id=card_id)
        else:
            card = Card.objects.get(
                id=card_id,
                user=request.user
            )
    except Card.DoesNotExist:
        return Response(
            {
                "error": "Card not found"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    # --------------------------------------------------------
    # CHECK BLOCKED CARD
    # --------------------------------------------------------
    if card.is_blocked:
        return Response(
            {
                "error": "This card is blocked",
                "card_id": card.id,
                "card_status": "BLOCKED",
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # --------------------------------------------------------
    # CHECK CREDIT LIMIT
    # --------------------------------------------------------
    if card.card_type == "credit":
        card_spent = Transaction.objects.filter(
            card=card,
            status="SUCCESS"
        ).aggregate(
            total=Coalesce(
                Sum("amount"),
                Decimal("0.00")
            )
        )["total"]

        available_credit = card.credit_limit - card_spent

        if amount > available_credit:
            return Response(
                {
                    "error": "Credit limit exceeded",
                    "card_id": card.id,
                    "card_limit": card.credit_limit,
                    "amount_already_spent": card_spent,
                    "available_credit": max(
                        Decimal("0.00"),
                        available_credit
                    ),
                    "requested_amount": amount
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    # --------------------------------------------------------
    # EXTRACT METADATA (IP, LOCATION, DEVICE)
    # --------------------------------------------------------
    meta = extract_request_metadata(request)
    ip_address = meta.get("ip_address")
    location = meta.get("location") or "Unknown"
    device_info = meta.get("device_info") or "Web"

    # Normalize category
    valid_categories = dict(Transaction.CATEGORY_CHOICES).keys()
    if category not in valid_categories:
        category = "General"

    # --------------------------------------------------------
    # FRAUD DETECTION EVALUATION
    # --------------------------------------------------------
    fraud_eval = evaluate_transaction_fraud(
        user=request.user,
        amount=amount,
        card=card,
        ip_address=ip_address,
        location=location,
        device_info=device_info,
    )

    fraud_status = fraud_eval["fraud_status"]

    # --------------------------------------------------------
    # CREATE PENDING TRANSACTION
    # --------------------------------------------------------
    transaction = Transaction.objects.create(
        user=request.user,
        card=card,
        amount=amount,
        category=category,
        fraud_status=fraud_status,
        ip_address=ip_address,
        location=location,
        device_info=device_info,
        status="PENDING"
    )

    # --------------------------------------------------------
    # LOG FRAUD & TRIGGER ALERT EMAIL IF FLAGGED
    # --------------------------------------------------------
    if fraud_eval["is_flagged"]:
        fraud_log = record_fraud_log(
            user=request.user,
            transaction=transaction,
            card=card,
            amount=amount,
            risk_level=fraud_eval["risk_level"],
            rule_triggered="; ".join(fraud_eval["rules_triggered"]),
            description=" | ".join(fraud_eval["descriptions"]),
            ip_address=ip_address,
            location=location,
            device_info=device_info,
        )
        send_fraud_alert_email(transaction, fraud_log)

    return Response(
        {
            "message": "Pending transaction created",
            "transaction": TransactionSerializer(
                transaction
            ).data
        },
        status=status.HTTP_201_CREATED
    )


# ============================================================
# UPDATE TRANSACTION STATUS
# ============================================================

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_transaction_status(request, transaction_id):
    # RBAC check: Read-Only role cannot update transactions
    if getattr(request.user, "role", None) == "READ_ONLY":
        return Response(
            {
                "error": "Read-Only role cannot update transactions"
            },
            status=status.HTTP_403_FORBIDDEN
        )

    new_status = request.data.get("status")
    failure_reason = request.data.get("failure_reason")

    # --------------------------------------------------------
    # VALIDATE STATUS
    # --------------------------------------------------------
    if new_status not in ["SUCCESS", "FAILED"]:
        return Response(
            {
                "error": "Status must be SUCCESS or FAILED"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # --------------------------------------------------------
    # VALIDATE FAILURE REASON
    # --------------------------------------------------------
    if new_status == "FAILED" and not failure_reason:
        return Response(
            {
                "error": (
                    "failure_reason is required "
                    "when status is FAILED"
                )
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # --------------------------------------------------------
    # GET TRANSACTION
    # --------------------------------------------------------
    try:
        if request.user.is_admin_role:
            transaction = Transaction.objects.get(
                id=transaction_id
            )
        else:
            transaction = Transaction.objects.get(
                id=transaction_id,
                user=request.user
            )
    except Transaction.DoesNotExist:
        return Response(
            {
                "error": "Transaction not found"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    # --------------------------------------------------------
    # CHECK BLOCKED CARD
    # --------------------------------------------------------
    if (
        new_status == "SUCCESS"
        and transaction.card
        and transaction.card.is_blocked
    ):
        return Response(
            {
                "error": (
                    "Transaction cannot be completed "
                    "because the card is blocked"
                ),
                "card_id": transaction.card.id,
                "card_status": "BLOCKED",
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # --------------------------------------------------------
    # UPDATE TRANSACTION
    # --------------------------------------------------------
    transaction.status = new_status

    if new_status == "FAILED":
        transaction.failure_reason = failure_reason
    else:
        transaction.failure_reason = None

    transaction.save(
        update_fields=[
            "status",
            "failure_reason"
        ]
    )

    # --------------------------------------------------------
    # HIGH-VALUE TRANSACTION EMAIL ALERT
    # --------------------------------------------------------
    if (
        new_status == "SUCCESS"
        and transaction.amount > Decimal("5000.00")
    ):
        send_transaction_alert(transaction)

    # --------------------------------------------------------
    # LOW AVAILABLE CREDIT EMAIL ALERT
    # --------------------------------------------------------
    if (
        new_status == "SUCCESS"
        and transaction.card
        and transaction.card.card_type == "credit"
    ):
        card = transaction.card
        card_spent = Transaction.objects.filter(
            card=card,
            status="SUCCESS"
        ).aggregate(
            total=Coalesce(
                Sum("amount"),
                Decimal("0.00")
            )
        )["total"]

        available_credit = card.credit_limit - card_spent

        send_low_credit_alert(
            transaction=transaction,
            available_credit=available_credit,
            credit_limit=card.credit_limit,
        )

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------
    return Response(
        {
            "message": "Transaction status updated successfully",
            "transaction": TransactionSerializer(
                transaction
            ).data
        },
        status=status.HTTP_200_OK
    )


# ============================================================
# DASHBOARD SUMMARY
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    user = request.user
    show_all = request.query_params.get("all") == "true"

    if (
        user.is_admin_role
        or user.is_support_role
        or user.is_read_only_role
    ) and show_all:
        transactions = Transaction.objects.all()
        credit_cards = Card.objects.filter(card_type="credit")
    else:
        transactions = Transaction.objects.filter(user=user)
        credit_cards = Card.objects.filter(user=user, card_type="credit")

    total_transactions = transactions.count()

    total_amount_spent = transactions.filter(
        status="SUCCESS"
    ).aggregate(
        total=Coalesce(
            Sum("amount"),
            Decimal("0.00")
        )
    )["total"]

    current_time = timezone.now()

    current_month_spending = transactions.filter(
        status="SUCCESS",
        transaction_date__year=current_time.year,
        transaction_date__month=current_time.month
    ).aggregate(
        total=Coalesce(
            Sum("amount"),
            Decimal("0.00")
        )
    )["total"]

    available_credit_limit = Decimal("0.00")

    for card in credit_cards:
        card_spent = transactions.filter(
            card=card,
            status="SUCCESS"
        ).aggregate(
            total=Coalesce(
                Sum("amount"),
                Decimal("0.00")
            )
        )["total"]

        card_available_credit = card.credit_limit - card_spent
        available_credit_limit += max(
            Decimal("0.00"),
            card_available_credit
        )

    last_5_transactions = (
        transactions
        .select_related("card")
        .order_by("-transaction_date")[:5]
    )

    recent_transactions = []
    for transaction in last_5_transactions:
        recent_transactions.append(
            {
                "amount": transaction.amount,
                "masked_card_number": (
                    transaction.card.masked_card_number
                    if transaction.card
                    else None
                ),
                "date": transaction.transaction_date,
                "status": transaction.status,
                "category": transaction.category,
                "fraud_status": transaction.fraud_status,
            }
        )

    return Response(
        {
            "total_transactions": total_transactions,
            "total_amount_spent": total_amount_spent,
            "current_month_spending": current_month_spending,
            "available_credit_limit": available_credit_limit,
            "last_5_transactions": recent_transactions,
        },
        status=status.HTTP_200_OK
    )


# ============================================================
# CARD USAGE ANALYTICS API (MONTHLY SPEND, CATEGORY, UTILIZATION)
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def card_usage_analytics(request):
    """
    Returns card usage analytics:
    1. Monthly spending summary for the year
    2. Category-wise expense breakdown
    3. Credit utilization percentage and per-card breakdown
    4. Overall KPIs
    """
    user = request.user
    show_all = request.query_params.get("all") == "true"
    target_user_id = request.query_params.get("user_id")

    # Staff role checks
    is_staff = user.is_admin_role or user.is_support_role or user.is_read_only_role
    if is_staff and (show_all or target_user_id):
        if target_user_id:
            tx_qs = Transaction.objects.filter(user_id=target_user_id)
            cards_qs = Card.objects.filter(user_id=target_user_id)
        else:
            tx_qs = Transaction.objects.all()
            cards_qs = Card.objects.all()
    else:
        tx_qs = Transaction.objects.filter(user=user)
        cards_qs = Card.objects.filter(user=user)

    now = timezone.now()
    try:
        year = int(request.query_params.get("year", now.year))
    except (ValueError, TypeError):
        year = now.year

    successful_tx = tx_qs.filter(status="SUCCESS")

    # 1. Monthly spending summary
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly_spending = []

    year_tx = successful_tx.filter(transaction_date__year=year)
    for month_num in range(1, 13):
        month_qs = year_tx.filter(transaction_date__month=month_num)
        month_total = month_qs.aggregate(total=Coalesce(Sum("amount"), Decimal("0.00")))["total"]
        month_count = month_qs.count()
        monthly_spending.append({
            "month": month_num,
            "month_name": month_names[month_num - 1],
            "total_amount": float(month_total),
            "count": month_count,
        })

    # 2. Category-wise expense data
    total_spent = successful_tx.aggregate(total=Coalesce(Sum("amount"), Decimal("0.00")))["total"]
    category_data = (
        successful_tx.values("category")
        .annotate(
            total_amount=Coalesce(Sum("amount"), Decimal("0.00")),
            count=Count("id")
        )
        .order_by("-total_amount")
    )

    category_expenses = []
    for item in category_data:
        cat_total = item["total_amount"]
        pct = (float(cat_total) / float(total_spent) * 100) if total_spent > 0 else 0.0
        category_expenses.append({
            "category": item["category"],
            "total_amount": float(cat_total),
            "count": item["count"],
            "percentage": round(pct, 2),
        })

    # If no transactions yet, provide category list with zeroes
    if not category_expenses:
        for cat_name, _ in Transaction.CATEGORY_CHOICES[:4]:
            category_expenses.append({
                "category": cat_name,
                "total_amount": 0.0,
                "count": 0,
                "percentage": 0.0,
            })

    # 3. Credit utilization percentage
    credit_cards = cards_qs.filter(card_type="credit")
    total_credit_limit = credit_cards.aggregate(total=Coalesce(Sum("credit_limit"), Decimal("0.00")))["total"]

    cards_breakdown = []
    total_credit_spent = Decimal("0.00")

    for card in credit_cards:
        card_spent = Transaction.objects.filter(
            card=card,
            status="SUCCESS"
        ).aggregate(total=Coalesce(Sum("amount"), Decimal("0.00")))["total"]

        total_credit_spent += card_spent
        available_credit = max(Decimal("0.00"), card.credit_limit - card_spent)
        card_utilization = (float(card_spent) / float(card.credit_limit) * 100) if card.credit_limit > 0 else 0.0

        cards_breakdown.append({
            "card_id": card.id,
            "masked_card_number": card.masked_card_number,
            "last_four_digits": card.last_four_digits,
            "credit_limit": float(card.credit_limit),
            "total_spent": float(card_spent),
            "available_credit": float(available_credit),
            "utilization_percentage": round(min(card_utilization, 100.0), 2),
            "is_blocked": card.is_blocked,
        })

    overall_utilization = (
        float(total_credit_spent) / float(total_credit_limit) * 100
        if total_credit_limit > 0
        else 0.0
    )

    # 4. Overall KPIs
    total_tx_count = tx_qs.count()
    successful_tx_count = successful_tx.count()
    failed_tx_count = tx_qs.filter(status="FAILED").count()
    avg_tx_amount = successful_tx.aggregate(avg=Coalesce(Avg("amount"), Decimal("0.00")))["avg"]

    return Response({
        "year": year,
        "monthly_spending": monthly_spending,
        "category_expenses": category_expenses,
        "credit_utilization": {
            "total_credit_limit": float(total_credit_limit),
            "total_credit_spent": float(total_credit_spent),
            "available_credit": float(max(Decimal("0.00"), total_credit_limit - total_credit_spent)),
            "utilization_percentage": round(min(overall_utilization, 100.0), 2),
            "cards_breakdown": cards_breakdown,
        },
        "overall_summary": {
            "total_spent": float(total_spent),
            "total_transactions": total_tx_count,
            "successful_transactions": successful_tx_count,
            "failed_transactions": failed_tx_count,
            "average_transaction_amount": float(avg_tx_amount),
        }
    }, status=status.HTTP_200_OK)


# ============================================================
# FRAUD LOG MANAGEMENT APIS (ADMIN & SUPPORT)
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_fraud_logs(request):
    """
    Admin, Support, and Read-Only can inspect fraud detection logs.
    Regular customers are denied.
    """
    if not (
        request.user.is_admin_role
        or request.user.is_support_role
        or request.user.is_read_only_role
    ):
        return Response(
            {"error": "Permission denied. Staff role required to view fraud logs."},
            status=status.HTTP_403_FORBIDDEN
        )

    queryset = FraudLog.objects.all().select_related("user", "card", "reviewed_by")

    status_filter = request.query_params.get("status")
    if status_filter:
        queryset = queryset.filter(status=status_filter.upper())

    risk_filter = request.query_params.get("risk_level")
    if risk_filter:
        queryset = queryset.filter(risk_level=risk_filter.upper())

    user_id = request.query_params.get("user_id")
    if user_id:
        queryset = queryset.filter(user_id=user_id)

    serializer = FraudLogSerializer(queryset[:100], many=True)
    return Response({
        "total_count": queryset.count(),
        "fraud_logs": serializer.data,
    }, status=status.HTTP_200_OK)


@api_view(["PATCH", "POST"])
@permission_classes([IsAuthenticated])
def review_fraud_log(request, log_id):
    """
    Admin and Support can review and resolve a fraud alert.
    """
    if not (request.user.is_admin_role or request.user.is_support_role):
        return Response(
            {"error": "Permission denied. Admin or Support role required."},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        fraud_log = FraudLog.objects.get(id=log_id)
    except FraudLog.DoesNotExist:
        return Response(
            {"error": "Fraud log entry not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    new_status = request.data.get("status")
    valid_statuses = dict(FraudLog.STATUS_CHOICES).keys()
    if new_status not in valid_statuses:
        return Response(
            {"error": f"Invalid status. Must be one of: {list(valid_statuses)}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    old_status = fraud_log.status
    fraud_log.status = new_status
    fraud_log.reviewed_by = request.user
    fraud_log.reviewed_at = timezone.now()
    fraud_log.save(update_fields=["status", "reviewed_by", "reviewed_at"])

    # Audit log
    record_audit_log(
        action="USER_STATUS_UPDATE",
        target_type="FraudLog",
        target_id=str(fraud_log.id),
        actor=request.user,
        description=f"FraudLog #{fraud_log.id} status updated from {old_status} to {new_status} by {request.user.username}",
        old_value={"status": old_status},
        new_value={"status": new_status},
        request=request,
    )

    return Response({
        "message": "Fraud log status updated successfully",
        "fraud_log": FraudLogSerializer(fraud_log).data
    }, status=status.HTTP_200_OK)


# ============================================================
# SYSTEM HEALTH & MONITORING API
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def system_health_metrics(request):
    """
    Returns live system health indicators:
    - API response time stats
    - Error and failure rates
    - Database latency & status
    - System summary counters
    """
    if not (
        request.user.is_admin_role
        or request.user.is_support_role
        or request.user.is_read_only_role
    ):
        return Response(
            {"error": "Permission denied. Staff role required to view health info."},
            status=status.HTTP_403_FORBIDDEN
        )

    # 1. Database Connectivity & Latency
    db_status = "HEALTHY"
    db_latency_ms = 0.0
    try:
        t0 = time.time()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_latency_ms = round((time.time() - t0) * 1000, 2)
    except Exception as e:
        db_status = f"ERROR: {e}"

    # 2. Metric Logs Aggregation
    recent_metrics = APIMetricLog.objects.all()
    total_requests = recent_metrics.count()

    if total_requests > 0:
        avg_resp_time = recent_metrics.aggregate(avg=Avg("response_time_ms"))["avg"] or 0.0
        avg_resp_time = round(float(avg_resp_time), 2)

        error_requests = recent_metrics.filter(status_code__gte=400).count()
        error_rate = round((error_requests / total_requests) * 100, 2)
        slow_requests = recent_metrics.filter(response_time_ms__gte=500).count()

        status_2xx = recent_metrics.filter(status_code__gte=200, status_code__lt=300).count()
        status_4xx = recent_metrics.filter(status_code__gte=400, status_code__lt=500).count()
        status_5xx = recent_metrics.filter(status_code__gte=500).count()
    else:
        avg_resp_time = 0.0
        error_rate = 0.0
        slow_requests = 0
        status_2xx = 0
        status_4xx = 0
        status_5xx = 0

    # 3. Overall Counters
    total_users = User.objects.count()
    total_cards = Card.objects.count()
    total_tx = Transaction.objects.count()
    total_fraud_logs = FraudLog.objects.count()
    pending_fraud_reviews = FraudLog.objects.filter(status="UNDER_REVIEW").count()

    # 4. Recent Requests Sample
    recent_logs = recent_metrics[:15]
    recent_logs_serialized = APIMetricLogSerializer(recent_logs, many=True).data

    return Response({
        "status": "HEALTHY" if db_status == "HEALTHY" else "DEGRADED",
        "timestamp": timezone.now().isoformat(),
        "database": {
            "status": db_status,
            "latency_ms": db_latency_ms,
        },
        "performance": {
            "total_requests": total_requests,
            "avg_response_time_ms": avg_resp_time,
            "error_rate_percentage": error_rate,
            "slow_requests_count": slow_requests,
            "status_distribution": {
                "2xx": status_2xx,
                "4xx": status_4xx,
                "5xx": status_5xx,
            }
        },
        "system_overview": {
            "total_users": total_users,
            "total_cards": total_cards,
            "total_transactions": total_tx,
            "total_fraud_alerts": total_fraud_logs,
            "pending_fraud_reviews": pending_fraud_reviews,
        },
        "recent_api_calls": recent_logs_serialized,
    }, status=status.HTTP_200_OK)


# ============================================================
# EXPORT: ANALYTICS SUMMARY TO CSV
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def export_analytics_csv(request):
    """
    Exports analytics summary (monthly spend, categories, utilization) to CSV.
    """
    user = request.user
    show_all = request.query_params.get("all") == "true"
    is_staff = user.is_admin_role or user.is_support_role or user.is_read_only_role

    if is_staff and show_all:
        tx_qs = Transaction.objects.filter(status="SUCCESS")
        cards_qs = Card.objects.filter(card_type="credit")
    else:
        tx_qs = Transaction.objects.filter(user=user, status="SUCCESS")
        cards_qs = Card.objects.filter(user=user, card_type="credit")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="analytics_summary.csv"'

    writer = csv.writer(response)

    # Section 1: Executive Header
    writer.writerow(["CARDPAY ANALYTICS SUMMARY REPORT"])
    writer.writerow(["Generated At", timezone.now().strftime("%Y-%m-%d %H:%M:%S")])
    writer.writerow(["User", user.username if not show_all else "All Users (System-wide)"])
    writer.writerow([])

    # Section 2: Monthly Spending
    writer.writerow(["--- MONTHLY SPENDING SUMMARY ---"])
    writer.writerow(["Month", "Total Amount (INR)", "Transaction Count"])
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    curr_year = timezone.now().year
    for m in range(1, 13):
        m_qs = tx_qs.filter(transaction_date__year=curr_year, transaction_date__month=m)
        m_total = m_qs.aggregate(total=Coalesce(Sum("amount"), Decimal("0.00")))["total"]
        writer.writerow([month_names[m - 1], f"{m_total:.2f}", m_qs.count()])
    writer.writerow([])

    # Section 3: Category Breakdown
    writer.writerow(["--- CATEGORY-WISE EXPENSE DATA ---"])
    writer.writerow(["Category", "Total Amount (INR)", "Transaction Count"])
    cat_data = tx_qs.values("category").annotate(
        total=Coalesce(Sum("amount"), Decimal("0.00")),
        count=Count("id")
    ).order_by("-total")
    for row in cat_data:
        writer.writerow([row["category"], f"{row['total']:.2f}", row["count"]])
    writer.writerow([])

    # Section 4: Credit Utilization
    writer.writerow(["--- CREDIT UTILIZATION SUMMARY ---"])
    writer.writerow(["Card Number", "Credit Limit", "Amount Spent", "Available Credit", "Utilization %"])
    for card in cards_qs:
        spent = Transaction.objects.filter(card=card, status="SUCCESS").aggregate(
            total=Coalesce(Sum("amount"), Decimal("0.00"))
        )["total"]
        avail = max(Decimal("0.00"), card.credit_limit - spent)
        util_pct = (float(spent) / float(card.credit_limit) * 100) if card.credit_limit > 0 else 0.0
        writer.writerow([
            card.masked_card_number,
            f"{card.credit_limit:.2f}",
            f"{spent:.2f}",
            f"{avail:.2f}",
            f"{util_pct:.2f}%"
        ])

    return response


# ============================================================
# EXPORT: ANALYTICS SUMMARY TO PDF
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def export_analytics_pdf(request):
    """
    Generates an executive ReportLab PDF report containing:
    - Monthly spending breakdown
    - Category-wise expenses
    - Credit utilization summary
    """
    user = request.user
    show_all = request.query_params.get("all") == "true"
    is_staff = user.is_admin_role or user.is_support_role or user.is_read_only_role

    if is_staff and show_all:
        tx_qs = Transaction.objects.filter(status="SUCCESS")
        cards_qs = Card.objects.filter(card_type="credit")
    else:
        tx_qs = Transaction.objects.filter(user=user, status="SUCCESS")
        cards_qs = Card.objects.filter(user=user, card_type="credit")

    curr_year = timezone.now().year
    total_spent = tx_qs.aggregate(total=Coalesce(Sum("amount"), Decimal("0.00")))["total"]

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "AnalyticsTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=18,
        leading=22,
        spaceAfter=6,
    )

    subtitle_style = ParagraphStyle(
        "AnalyticsSubtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        textColor=colors.grey,
        spaceAfter=16,
    )

    heading_style = ParagraphStyle(
        "AnalyticsHeading",
        parent=styles["Heading2"],
        fontSize=11,
        leading=14,
        spaceBefore=8,
        spaceAfter=6,
    )

    normal_style = ParagraphStyle(
        "AnalyticsNormal",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
    )

    story = []

    # Title & Subtitle
    story.append(Paragraph("CARDPAY - ANALYTICS REPORT", title_style))
    story.append(Paragraph(
        f"Generated on {timezone.now().strftime('%d %B %Y')} | Account: {user.username if not show_all else 'System Overview'}",
        subtitle_style
    ))

    # Executive Overview Table
    overview_data = [
        [Paragraph("<b>Total Spending</b>", normal_style), f"Rs. {total_spent:,.2f}"],
        [Paragraph("<b>Total Successful Transactions</b>", normal_style), str(tx_qs.count())],
        [Paragraph("<b>Active Credit Cards</b>", normal_style), str(cards_qs.count())],
    ]
    overview_table = Table(overview_data, colWidths=[200, 290])
    overview_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#e2e8f0")),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(overview_table)
    story.append(Spacer(1, 14))

    # Category Breakdown Table
    story.append(Paragraph("Category-Wise Expense Breakdown", heading_style))
    cat_rows = [["Category", "Total Spent", "Transactions", "Share %"]]
    cat_data = tx_qs.values("category").annotate(
        total=Coalesce(Sum("amount"), Decimal("0.00")),
        count=Count("id")
    ).order_by("-total")

    for c in cat_data:
        pct = (float(c["total"]) / float(total_spent) * 100) if total_spent > 0 else 0.0
        cat_rows.append([
            c["category"],
            f"Rs. {c['total']:,.2f}",
            str(c["count"]),
            f"{pct:.1f}%",
        ])

    if len(cat_rows) == 1:
        cat_rows.append(["No expenses recorded", "Rs. 0.00", "0", "0%"])

    cat_table = Table(cat_rows, colWidths=[160, 130, 100, 100])
    cat_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(cat_table)
    story.append(Spacer(1, 14))

    # Credit Utilization Table
    story.append(Paragraph("Credit Card Utilization Summary", heading_style))
    util_rows = [["Card", "Credit Limit", "Amount Spent", "Available", "Utilization"]]
    for card in cards_qs:
        spent = Transaction.objects.filter(card=card, status="SUCCESS").aggregate(
            total=Coalesce(Sum("amount"), Decimal("0.00"))
        )["total"]
        avail = max(Decimal("0.00"), card.credit_limit - spent)
        util_pct = (float(spent) / float(card.credit_limit) * 100) if card.credit_limit > 0 else 0.0
        util_rows.append([
            card.masked_card_number,
            f"Rs. {card.credit_limit:,.2f}",
            f"Rs. {spent:,.2f}",
            f"Rs. {avail:,.2f}",
            f"{util_pct:.1f}%",
        ])

    if len(util_rows) == 1:
        util_rows.append(["No credit cards found", "-", "-", "-", "-"])

    util_table = Table(util_rows, colWidths=[140, 95, 95, 95, 65])
    util_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(util_table)

    doc.build(story)
    buffer.seek(0)

    return FileResponse(
        buffer,
        as_attachment=True,
        filename=f"analytics_summary_{curr_year}.pdf",
        content_type="application/pdf",
    )


# ============================================================
# EXPORT: FILTERED TRANSACTIONS TO CSV
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def export_transactions_csv_api(request):
    """
    Exports filtered transactions directly to CSV for the authenticated user / admin.
    """
    view = TransactionHistoryView()
    view.request = request
    queryset = view.get_queryset()

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="transactions_export.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "Transaction ID",
        "User",
        "Card",
        "Amount (INR)",
        "Status",
        "Category",
        "Fraud Status",
        "IP Address",
        "Location",
        "Date",
    ])

    for tx in queryset:
        card_num = tx.card.masked_card_number if tx.card else "N/A"
        writer.writerow([
            tx.id,
            tx.user.username,
            card_num,
            f"{tx.amount:.2f}",
            tx.status,
            tx.category,
            tx.fraud_status,
            tx.ip_address or "-",
            tx.location or "-",
            tx.transaction_date.strftime("%Y-%m-%d %H:%M:%S"),
        ])

    return response


# ============================================================
# MONTHLY STATEMENT PDF (PRESERVED)
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def monthly_statement(request):
    user = request.user
    current_time = timezone.now()

    try:
        year = int(request.query_params.get("year", current_time.year))
        month = int(request.query_params.get("month", current_time.month))
    except (TypeError, ValueError):
        return Response(
            {"error": "Year and month must be valid numbers"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if month < 1 or month > 12:
        return Response(
            {"error": "Month must be between 1 and 12"},
            status=status.HTTP_400_BAD_REQUEST
        )

    transactions = (
        Transaction.objects.filter(
            user=user,
            transaction_date__year=year,
            transaction_date__month=month
        )
        .select_related("card")
        .order_by("-transaction_date")
    )

    total_spending = transactions.filter(
        status="SUCCESS"
    ).aggregate(
        total=Coalesce(Sum("amount"), Decimal("0.00"))
    )["total"]

    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "StatementTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        leading=24,
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        "StatementSubtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        textColor=colors.grey,
        spaceAfter=20,
    )

    heading_style = ParagraphStyle(
        "StatementHeading",
        parent=styles["Heading2"],
        fontSize=12,
        leading=15,
        spaceBefore=10,
        spaceAfter=8,
    )

    normal_style = ParagraphStyle(
        "StatementNormal",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
    )

    story = []

    story.append(Paragraph("CREDIT CARD PAYMENT SYSTEM", title_style))
    story.append(Paragraph(f"Monthly Statement - {month:02d}/{year}", subtitle_style))

    story.append(Paragraph("Account Summary", heading_style))

    customer_data = [
        [Paragraph("<b>Customer</b>", normal_style), Paragraph(user.get_full_name() or user.username, normal_style)],
        [Paragraph("<b>Email</b>", normal_style), Paragraph(user.email, normal_style)],
        [Paragraph("<b>Statement Period</b>", normal_style), Paragraph(f"{month:02d}/{year}", normal_style)],
        [Paragraph("<b>Total Spending</b>", normal_style), Paragraph(f"Rs. {total_spending:,.2f}", normal_style)],
    ]

    customer_table = Table(customer_data, colWidths=[140, 350])
    customer_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#e2e8f0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(customer_table)
    story.append(Spacer(1, 18))

    story.append(Paragraph("Transaction Details", heading_style))
    transaction_data = [["ID", "Date", "Card", "Amount", "Status"]]

    for transaction in transactions:
        masked_card = transaction.card.masked_card_number if transaction.card else "N/A"
        transaction_data.append([
            str(transaction.id),
            transaction.transaction_date.strftime("%d-%m-%Y"),
            masked_card,
            f"Rs. {transaction.amount:,.2f}",
            transaction.status,
        ])

    if len(transaction_data) == 1:
        transaction_data.append(["-", "-", "-", "No transactions", "-"])

    transaction_table = Table(transaction_data, colWidths=[40, 75, 150, 90, 75], repeatRows=1)
    transaction_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(transaction_table)
    story.append(Spacer(1, 18))

    successful_count = transactions.filter(status="SUCCESS").count()
    failed_count = transactions.filter(status="FAILED").count()
    pending_count = transactions.filter(status="PENDING").count()

    story.append(Paragraph("Statement Summary", heading_style))
    summary_data = [
        ["Successful Transactions", str(successful_count)],
        ["Failed Transactions", str(failed_count)],
        ["Pending Transactions", str(pending_count)],
        ["Total Spending", f"Rs. {total_spending:,.2f}"],
    ]
    summary_table = Table(summary_data, colWidths=[250, 240])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("PADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 20))

    story.append(Paragraph("This is a system-generated monthly statement. Card numbers are masked for security.", subtitle_style))

    document.build(story)
    buffer.seek(0)
    filename = f"monthly_statement_{year}_{month:02d}.pdf"

    return FileResponse(
        buffer,
        as_attachment=True,
        filename=filename,
        content_type="application/pdf",
    )