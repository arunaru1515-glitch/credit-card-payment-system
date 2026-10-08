from decimal import Decimal, InvalidOperation
from io import BytesIO

from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.http import FileResponse
from django.utils import timezone

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
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

from accounts.models import Card

from .models import Transaction
from .serializers import TransactionSerializer
from .email_service import (
    send_transaction_alert,
    send_low_credit_alert,
)


# ============================================================
# TRANSACTION HISTORY
# ============================================================

class TransactionHistoryView(generics.ListAPIView):

    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        queryset = Transaction.objects.filter(
            user=self.request.user
        ).order_by("-transaction_date")

        status_filter = self.request.query_params.get("status")

        if status_filter:
            queryset = queryset.filter(
                status=status_filter.upper()
            )

        min_amount = self.request.query_params.get("min_amount")

        if min_amount:
            queryset = queryset.filter(
                amount__gte=min_amount
            )

        max_amount = self.request.query_params.get("max_amount")

        if max_amount:
            queryset = queryset.filter(
                amount__lte=max_amount
            )

        date = self.request.query_params.get("date")

        if date:
            queryset = queryset.filter(
                transaction_date__date=date
            )

        return queryset


# ============================================================
# CREATE PENDING TRANSACTION
# ============================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_pending_transaction(request):

    card_id = request.data.get("card_id")
    amount = request.data.get("amount")

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
            user=request.user,
            card=card,
            status="SUCCESS"
        ).aggregate(
            total=Coalesce(
                Sum("amount"),
                Decimal("0.00")
            )
        )["total"]

        available_credit = (
            card.credit_limit - card_spent
        )

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
    # CREATE PENDING TRANSACTION
    # --------------------------------------------------------

    transaction = Transaction.objects.create(
        user=request.user,
        card=card,
        amount=amount,
        status="PENDING"
    )

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
            user=request.user,
            card=card,
            status="SUCCESS"
        ).aggregate(
            total=Coalesce(
                Sum("amount"),
                Decimal("0.00")
            )
        )["total"]

        available_credit = (
            card.credit_limit - card_spent
        )

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

    # --------------------------------------------------------
    # ALL USER TRANSACTIONS
    # --------------------------------------------------------

    transactions = Transaction.objects.filter(
        user=user
    )

    # --------------------------------------------------------
    # 1. TOTAL TRANSACTIONS
    # --------------------------------------------------------

    total_transactions = transactions.count()

    # --------------------------------------------------------
    # 2. TOTAL AMOUNT SPENT
    # --------------------------------------------------------

    total_amount_spent = transactions.filter(
        status="SUCCESS"
    ).aggregate(
        total=Coalesce(
            Sum("amount"),
            Decimal("0.00")
        )
    )["total"]

    # --------------------------------------------------------
    # 3. CURRENT MONTH SPENDING
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # 4. AVAILABLE CREDIT LIMIT
    # --------------------------------------------------------

    credit_cards = Card.objects.filter(
        user=user,
        card_type="credit"
    )

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

        card_available_credit = (
            card.credit_limit - card_spent
        )

        available_credit_limit += max(
            Decimal("0.00"),
            card_available_credit
        )

    # --------------------------------------------------------
    # 5. LAST 5 TRANSACTIONS
    # --------------------------------------------------------

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
            }
        )

    # --------------------------------------------------------
    # FINAL RESPONSE
    # --------------------------------------------------------

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
# MONTHLY STATEMENT PDF
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def monthly_statement(request):

    user = request.user

    # --------------------------------------------------------
    # GET MONTH AND YEAR
    # --------------------------------------------------------

    current_time = timezone.now()

    try:

        year = int(
            request.query_params.get(
                "year",
                current_time.year
            )
        )

        month = int(
            request.query_params.get(
                "month",
                current_time.month
            )
        )

    except (TypeError, ValueError):

        return Response(
            {
                "error": "Year and month must be valid numbers"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if month < 1 or month > 12:

        return Response(
            {
                "error": "Month must be between 1 and 12"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # --------------------------------------------------------
    # GET USER TRANSACTIONS FOR SELECTED MONTH
    # --------------------------------------------------------

    transactions = (
        Transaction.objects
        .filter(
            user=user,
            transaction_date__year=year,
            transaction_date__month=month
        )
        .select_related("card")
        .order_by("-transaction_date")
    )

    # --------------------------------------------------------
    # TOTAL SPENDING
    # --------------------------------------------------------

    total_spending = transactions.filter(
        status="SUCCESS"
    ).aggregate(
        total=Coalesce(
            Sum("amount"),
            Decimal("0.00")
        )
    )["total"]

    # --------------------------------------------------------
    # CREATE PDF IN MEMORY
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "CREDIT CARD PAYMENT SYSTEM",
            title_style
        )
    )

    story.append(
        Paragraph(
            f"Monthly Statement - {month:02d}/{year}",
            subtitle_style
        )
    )

    # --------------------------------------------------------
    # ACCOUNT SUMMARY
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Account Summary",
            heading_style
        )
    )

    customer_data = [
        [
            Paragraph("<b>Customer</b>", normal_style),
            Paragraph(
                user.get_full_name() or user.username,
                normal_style
            ),
        ],
        [
            Paragraph("<b>Email</b>", normal_style),
            Paragraph(user.email, normal_style),
        ],
        [
            Paragraph("<b>Statement Period</b>", normal_style),
            Paragraph(
                f"{month:02d}/{year}",
                normal_style
            ),
        ],
        [
            Paragraph("<b>Total Spending</b>", normal_style),
            Paragraph(
                f"Rs. {total_spending:,.2f}",
                normal_style
            ),
        ],
    ]

    customer_table = Table(
        customer_data,
        colWidths=[140, 350],
    )

    customer_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#f1f5f9"),
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    colors.HexColor("#cbd5e1"),
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.3,
                    colors.HexColor("#e2e8f0"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    story.append(customer_table)
    story.append(Spacer(1, 18))

    # --------------------------------------------------------
    # TRANSACTION DETAILS
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Transaction Details",
            heading_style
        )
    )

    transaction_data = [
        [
            "ID",
            "Date",
            "Card",
            "Amount",
            "Status",
        ]
    ]

    for transaction in transactions:

        masked_card = (
            transaction.card.masked_card_number
            if transaction.card
            else "N/A"
        )

        transaction_data.append(
            [
                str(transaction.id),
                transaction.transaction_date.strftime(
                    "%d-%m-%Y"
                ),
                masked_card,
                f"Rs. {transaction.amount:,.2f}",
                transaction.status,
            ]
        )

    if len(transaction_data) == 1:

        transaction_data.append(
            [
                "-",
                "-",
                "-",
                "No transactions",
                "-"
            ]
        )

    transaction_table = Table(
        transaction_data,
        colWidths=[
            40,
            75,
            150,
            90,
            75,
        ],
        repeatRows=1,
    )

    transaction_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#1e293b"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#cbd5e1"),
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor("#f8fafc"),
                    ],
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER",
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    story.append(transaction_table)
    story.append(Spacer(1, 18))

    # --------------------------------------------------------
    # STATEMENT SUMMARY
    # --------------------------------------------------------

    successful_count = transactions.filter(
        status="SUCCESS"
    ).count()

    failed_count = transactions.filter(
        status="FAILED"
    ).count()

    pending_count = transactions.filter(
        status="PENDING"
    ).count()

    story.append(
        Paragraph(
            "Statement Summary",
            heading_style
        )
    )

    summary_data = [
        [
            "Successful Transactions",
            str(successful_count)
        ],
        [
            "Failed Transactions",
            str(failed_count)
        ],
        [
            "Pending Transactions",
            str(pending_count)
        ],
        [
            "Total Spending",
            f"Rs. {total_spending:,.2f}"
        ],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[250, 240],
    )

    summary_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#f1f5f9"),
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#cbd5e1"),
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold",
                ),
                (
                    "ALIGN",
                    (1, 0),
                    (1, -1),
                    "RIGHT",
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    story.append(summary_table)
    story.append(Spacer(1, 20))

    # --------------------------------------------------------
    # FOOTER NOTE
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "This is a system-generated monthly statement. "
            "Card numbers are masked for security.",
            subtitle_style
        )
    )

    # --------------------------------------------------------
    # BUILD PDF
    # --------------------------------------------------------

    document.build(story)

    buffer.seek(0)

    filename = (
        f"monthly_statement_{year}_{month:02d}.pdf"
    )

    return FileResponse(
        buffer,
        as_attachment=True,
        filename=filename,
        content_type="application/pdf",
    )