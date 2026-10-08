from threading import Thread

from django.contrib import admin
from django.conf import settings
from django.core.mail import send_mail

from .models import User, Card


admin.site.register(User)


def send_card_blocked_email(card):
    user = card.user

    if not user or not user.email:
        print("BLOCK EMAIL SKIPPED: User email not available")
        return

    subject = "Credit Card Alert - Card Blocked"

    message = f"""
Dear {user.username},

Your credit card has been blocked by the administrator.

Card Details
------------
Card: {card.masked_card_number}
Card Type: {card.get_card_type_display()}
Last Four Digits: {card.last_four_digits}
Status: BLOCKED

You will not be able to use this card for transactions while it is blocked.

If you believe this was done incorrectly, please contact the administrator.

Regards,
Credit Card Payment System
"""

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=True,
        )

        print(
            f"CARD BLOCK EMAIL TRIGGERED FOR CARD {card.id}"
        )

    except Exception as e:
        print("BLOCK EMAIL ERROR:", e)


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "card_type",
        "masked_card_number",
        "last_four_digits",
        "credit_limit",
        "is_blocked",
        "created_at",
    )

    list_filter = (
        "card_type",
        "is_blocked",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "masked_card_number",
        "last_four_digits",
    )

    list_editable = (
        "credit_limit",
        "is_blocked",
    )

    readonly_fields = (
        "created_at",
    )

    ordering = (
        "-created_at",
    )

    def save_model(self, request, obj, form, change):

        was_blocked = False

        if change:
            old_card = Card.objects.get(pk=obj.pk)
            was_blocked = old_card.is_blocked

        super().save_model(request, obj, form, change)

        if not was_blocked and obj.is_blocked:
            email_thread = Thread(
                target=send_card_blocked_email,
                args=(obj,),
                daemon=True,
            )
            email_thread.start()