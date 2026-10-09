from rest_framework import serializers
from .models import Transaction, FraudLog, APIMetricLog


class TransactionSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source="user.username", read_only=True)
    card_masked_number = serializers.SerializerMethodField()
    card_type = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            "id",
            "user",
            "user_username",
            "card",
            "card_masked_number",
            "card_type",
            "amount",
            "status",
            "category",
            "fraud_status",
            "ip_address",
            "location",
            "device_info",
            "failure_reason",
            "transaction_date",
        ]
        read_only_fields = [
            "id",
            "user",
            "transaction_date",
            "failure_reason",
        ]

    def get_card_masked_number(self, obj):
        if obj.card:
            return obj.card.masked_card_number
        return None

    def get_card_type(self, obj):
        if obj.card:
            return obj.card.card_type
        return None


class FraudLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)
    card_masked_number = serializers.SerializerMethodField()
    reviewed_by_username = serializers.CharField(source="reviewed_by.username", read_only=True)

    class Meta:
        model = FraudLog
        fields = [
            "id",
            "transaction",
            "user",
            "username",
            "user_email",
            "card",
            "card_masked_number",
            "amount",
            "risk_level",
            "rule_triggered",
            "description",
            "ip_address",
            "location",
            "device_info",
            "status",
            "reviewed_by",
            "reviewed_by_username",
            "reviewed_at",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "transaction",
            "created_at",
        ]

    def get_card_masked_number(self, obj):
        if obj.card:
            return obj.card.masked_card_number
        return None


class APIMetricLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = APIMetricLog
        fields = [
            "id",
            "endpoint",
            "method",
            "status_code",
            "response_time_ms",
            "user",
            "username",
            "ip_address",
            "error_message",
            "timestamp",
        ]
        read_only_fields = ["id", "timestamp"]