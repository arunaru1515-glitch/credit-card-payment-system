from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_ADMIN = 'ADMIN'
    ROLE_SUPPORT = 'SUPPORT'
    ROLE_READ_ONLY = 'READ_ONLY'
    ROLE_CUSTOMER = 'CUSTOMER'

    ROLE_CHOICES = (
        (ROLE_ADMIN, 'Admin'),
        (ROLE_SUPPORT, 'Support'),
        (ROLE_READ_ONLY, 'Read-Only'),
        (ROLE_CUSTOMER, 'Customer'),
    )

    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_CUSTOMER
    )

    @property
    def is_admin_role(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser

    @property
    def is_support_role(self):
        return self.role in [self.ROLE_ADMIN, self.ROLE_SUPPORT] or self.is_superuser

    @property
    def is_read_only_role(self):
        return self.role in [self.ROLE_ADMIN, self.ROLE_SUPPORT, self.ROLE_READ_ONLY] or self.is_superuser

    def __str__(self):
        return f"{self.username} ({self.role})"


class Card(models.Model):
    CARD_TYPES = (
        ('credit', 'Credit Card'),
        ('debit', 'Debit Card'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cards'
    )

    card_type = models.CharField(
        max_length=10,
        choices=CARD_TYPES
    )

    masked_card_number = models.CharField(
        max_length=19
    )

    last_four_digits = models.CharField(
        max_length=4
    )

    credit_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=100000.00
    )

    is_blocked = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        status = "Blocked" if self.is_blocked else "Active"

        return (
            f"{self.card_type} - "
            f"**** {self.last_four_digits} - "
            f"{status}"
        )


class AuditLog(models.Model):
    ACTION_CHOICES = (
        ('CARD_BLOCK', 'Card Blocked'),
        ('CARD_UNBLOCK', 'Card Unblocked'),
        ('CREDIT_LIMIT_UPDATE', 'Credit Limit Updated'),
        ('ROLE_UPDATE', 'User Role Updated'),
        ('USER_STATUS_UPDATE', 'User Status Updated'),
    )

    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES
    )
    target_type = models.CharField(
        max_length=50,
        default='Card'
    )
    target_id = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )
    description = models.TextField(
        blank=True,
        null=True
    )
    old_value = models.JSONField(
        blank=True,
        null=True
    )
    new_value = models.JSONField(
        blank=True,
        null=True
    )
    ip_address = models.CharField(
        max_length=45,
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        actor_name = self.actor.username if self.actor else "System"
        return f"[{self.created_at.strftime('%Y-%m-%d %H:%M:%S')}] {actor_name} -> {self.action} on {self.target_type}#{self.target_id}"