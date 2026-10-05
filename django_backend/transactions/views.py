from decimal import Decimal, InvalidOperation

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


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_pending_transaction(request):
    card_id = request.data.get("card_id")
    amount = request.data.get("amount")

    if not card_id:
        return Response(
            {"error": "card_id is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

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