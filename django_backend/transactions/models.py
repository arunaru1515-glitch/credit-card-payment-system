from django.db import models
from accounts.models import User, Card


class Transaction(models.Model):

    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    )

    CATEGORY_CHOICES = (
        ("Groceries", "Groceries"),
        ("Shopping", "Shopping"),
        ("Dining", "Dining"),
        ("Utilities", "Utilities"),
        ("Travel", "Travel"),
        ("Entertainment", "Entertainment"),
        ("Healthcare", "Healthcare"),
        ("General", "General"),
    )

    FRAUD_STATUS_CHOICES = (
        ("CLEAN", "Clean"),
        ("SUSPICIOUS", "Suspicious"),
        ("FLAGGED", "Flagged"),
        ("BLOCKED", "Blocked"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="transactions",
        db_index=True
    )

    card = models.ForeignKey(
        Card,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="PENDING",
        db_index=True
    )

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default="General",
        db_index=True
    )

    fraud_status = models.CharField(
        max_length=20,
        choices=FRAUD_STATUS_CHOICES,
        default="CLEAN",
        db_index=True
    )

    ip_address = models.CharField(
        max_length=45,
        blank=True,
        null=True
    )

    location = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default="Unknown"
    )

    device_info = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        default="Web"
    )

    failure_reason = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    transaction_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ["-transaction_date"]
        indexes = [
            models.Index(fields=["user", "-transaction_date"]),
            models.Index(fields=["status", "-transaction_date"]),
            models.Index(fields=["category", "-transaction_date"]),
            models.Index(fields=["fraud_status"]),
        ]

    def __str__(self):
        return f"Transaction #{self.id} - {self.status} [{self.fraud_status}]"


class FraudLog(models.Model):
    RISK_CHOICES = (
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
    )

    STATUS_CHOICES = (
        ("UNDER_REVIEW", "Under Review"),
        ("CONFIRMED", "Confirmed Fraud"),
        ("FALSE_POSITIVE", "False Positive"),
        ("RESOLVED", "Resolved"),
    )

    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fraud_logs"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="fraud_logs"
    )
    card = models.ForeignKey(
        Card,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fraud_logs"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    risk_level = models.CharField(
        max_length=20,
        choices=RISK_CHOICES,
        default="MEDIUM"
    )
    rule_triggered = models.CharField(
        max_length=255
    )
    description = models.TextField(
        blank=True,
        null=True
    )
    ip_address = models.CharField(
        max_length=45,
        blank=True,
        null=True
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default="Unknown"
    )
    device_info = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        default="Web"
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="UNDER_REVIEW"
    )
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_fraud_logs"
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"FraudLog #{self.id} - {self.rule_triggered} ({self.risk_level}) [{self.status}]"


class APIMetricLog(models.Model):
    endpoint = models.CharField(
        max_length=255,
        db_index=True
    )
    method = models.CharField(
        max_length=10
    )
    status_code = models.IntegerField(
        db_index=True
    )
    response_time_ms = models.FloatField()
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="api_metric_logs"
    )
    ip_address = models.CharField(
        max_length=45,
        blank=True,
        null=True
    )
    error_message = models.TextField(
        blank=True,
        null=True
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"[{self.method}] {self.endpoint} - {self.status_code} ({self.response_time_ms:.1f}ms)"