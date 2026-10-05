from rest_framework import serializers
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction

        fields = [
            "id",
            "user",
            "card",
            "amount",
            "status",
            "failure_reason",
            "transaction_date",
        ]

        read_only_fields = [
            "id",
            "user",
            "transaction_date",
            "failure_reason",
        ]