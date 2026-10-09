from threading import Thread
from django.conf import settings
from django.core.mail import send_mail


def _send_email_async(subject, message, recipient):
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=True,
        )
    except Exception as e:
        print("EMAIL ERROR:", e)


def send_card_blocked_email(card):
    """
    Sends an email notification when a card is blocked.
    """
    user = card.user
    if not user or not user.email:
        print("BLOCK EMAIL SKIPPED: User email not available")
        return

    subject = "Credit Card Alert - Card Blocked"
    message = f"""Dear {user.username},

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
    Thread(
        target=_send_email_async,
        args=(subject, message, user.email),
        daemon=True,
    ).start()
