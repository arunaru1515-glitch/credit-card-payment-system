from django.db import models
from accounts.models import User, Card


class Transaction(models.Model):

    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="transactions"
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
        default="PENDING"
    )

    failure_reason = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    transaction_date = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Transaction #{self.id} - {self.status}"