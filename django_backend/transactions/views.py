from decimal import Decimal, InvalidOperation

from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import Card
from .models import Transaction
from .serializers import TransactionSerializer


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
            {"error": "card_id is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # --------------------------------------------------------
    # VALIDATE AMOUNT
    # --------------------------------------------------------

    if amount is None:
        return Response(
            {"error": "amount is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        amount = Decimal(str(amount))
    except (InvalidOperation, TypeError, ValueError):
        return Response(
            {"error": "Invalid amount"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if amount <= 0:
        return Response(
            {"error": "Amount must be greater than 0"},
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
            {"error": "Card not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # --------------------------------------------------------
    # CHECK CREDIT LIMIT
    # --------------------------------------------------------
    #
    # Only credit cards have a credit limit.
    # The calculation is done for THIS CARD only.
    #
    # Successful transactions on other cards are ignored.
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
            "transaction": TransactionSerializer(transaction).data
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

    if new_status not in ["SUCCESS", "FAILED"]:
        return Response(
            {
                "error": "Status must be SUCCESS or FAILED"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if new_status == "FAILED" and not failure_reason:
        return Response(
            {
                "error": "failure_reason is required when status is FAILED"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        transaction = Transaction.objects.get(
            id=transaction_id,
            user=request.user
        )
    except Transaction.DoesNotExist:
        return Response(
            {"error": "Transaction not found"},
            status=status.HTTP_404_NOT_FOUND
        )

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

    return Response(
        {
            "message": "Transaction status updated successfully",
            "transaction": TransactionSerializer(transaction).data
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
    #
    # Calculate credit availability separately for each
    # credit card.
    #
    # The dashboard value is the total available credit
    # across the user's credit cards.
    #
    # Payment validation itself remains card-specific.
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