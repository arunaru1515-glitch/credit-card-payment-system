from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username


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

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.card_type} - **** {self.last_four_digits}"