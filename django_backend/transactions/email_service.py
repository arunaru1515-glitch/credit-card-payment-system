from decimal import Decimal
from threading import Thread

from django.conf import settings
from django.core.mail import send_mail


# ============================================================
# COMMON EMAIL SENDER
# ============================================================

def _send_email(subject, message, recipient):
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


# ============================================================
# HIGH-VALUE TRANSACTION EMAIL ALERT
# ============================================================

def send_transaction_alert(transaction):
    """
    Sends an email alert when a successful transaction
    exceeds Rs. 5,000.
    """

    user = transaction.user

    if not user or not user.email:
        print("EMAIL SKIPPED: User email not available")
        return

    if transaction.amount <= Decimal("5000.00"):
        return

    card_number = "N/A"

    if transaction.card:
        card_number = transaction.card.masked_card_number

    subject = "Credit Card Payment Alert - High Value Transaction"

    message = f"""
Dear {user.username},

A high-value transaction has been detected on your
Credit Card Payment System account.

Transaction Details
-------------------
Transaction ID: {transaction.id}
Amount: Rs. {transaction.amount:,.2f}
Card: {card_number}
Status: {transaction.status}

This transaction exceeds the high-value transaction
alert threshold of Rs. 5,000.

If you did not authorize this transaction, please
contact the administrator immediately.

Regards,
Credit Card Payment System
"""

    email_thread = Thread(
        target=_send_email,
        args=(
            subject,
            message,
            user.email,
        ),
        daemon=True,
    )

    email_thread.start()

    print(
        f"HIGH VALUE EMAIL TRIGGERED "
        f"FOR TRANSACTION {transaction.id}"
    )


# ============================================================
# LOW AVAILABLE CREDIT EMAIL ALERT
# ============================================================

def send_low_credit_alert(
    transaction,
    available_credit,
    credit_limit,
):
    """
    Sends an email when the available credit falls
    below 10% of the total credit limit.
    """

    user = transaction.user

    if not user or not user.email:
        print(
            "LOW CREDIT EMAIL SKIPPED: "
            "User email not available"
        )
        return

    if not transaction.card:
        return

    if credit_limit <= Decimal("0.00"):
        return

    # 10% of the total credit limit
    threshold = credit_limit * Decimal("0.10")

    if available_credit >= threshold:
        return

    card_number = transaction.card.masked_card_number

    subject = "Credit Card Alert - Low Available Credit"

    message = f"""
Dear {user.username},

Your available credit limit has fallen below 10% of
your credit card's total credit limit.

Card Details
------------
Card: {card_number}
Credit Limit: Rs. {credit_limit:,.2f}
Available Credit: Rs. {available_credit:,.2f}
Transaction Amount: Rs. {transaction.amount:,.2f}

The available credit is now below the 10% alert threshold.

Please review your recent transactions and available credit.

Regards,
Credit Card Payment System
"""

    email_thread = Thread(
        target=_send_email,
        args=(
            subject,
            message,
            user.email,
        ),
        daemon=True,
    )

    email_thread.start()

    print(
        f"LOW CREDIT EMAIL TRIGGERED "
        f"FOR TRANSACTION {transaction.id}"
    )


# ============================================================
# FRAUD ALERT EMAIL
# ============================================================

def send_fraud_alert_email(transaction, fraud_log):
    """
    Triggers an immediate email alert when a transaction is flagged
    by rule-based fraud detection.
    """
    user = transaction.user if transaction else getattr(fraud_log, "user", None)

    if not user or not user.email:
        print("FRAUD ALERT SKIPPED: User email not available")
        return

    card_number = "N/A"
    if transaction and transaction.card:
        card_number = transaction.card.masked_card_number
    elif fraud_log and fraud_log.card:
        card_number = fraud_log.card.masked_card_number

    tx_id = transaction.id if transaction else (fraud_log.transaction_id or "N/A")
    amount = transaction.amount if transaction else fraud_log.amount
    risk = fraud_log.risk_level if fraud_log else "HIGH"
    rule = fraud_log.rule_triggered if fraud_log else "Suspicious Activity"
    desc = fraud_log.description if fraud_log else "Potential unauthorized activity"

    subject = f"URGENT: Security Alert - Suspicious Activity Detected on Card {card_number}"

    message = f"""
Dear {user.username},

Our automated fraud detection system has identified suspicious activity on your account.

Alert Summary
-------------
Risk Level: {risk}
Rule Triggered: {rule}
Transaction ID: {tx_id}
Card: {card_number}
Amount: Rs. {amount:,.2f}
Location: {getattr(fraud_log, 'location', 'Unknown')}
IP Address: {getattr(fraud_log, 'ip_address', 'N/A')}
Details: {desc}

Action Taken:
This transaction has been placed on {risk} risk monitoring and recorded in the audit log for review.

What should you do?
If you did not authorize this transaction, please log in immediately to block this card and report this activity to our fraud prevention team.

Regards,
CardPay Fraud Prevention Team
"""

    email_thread = Thread(
        target=_send_email,
        args=(
            subject,
            message,
            user.email,
        ),
        daemon=True,
    )
    email_thread.start()

    print(f"FRAUD ALERT EMAIL TRIGGERED FOR TRANSACTION {tx_id} (Risk: {risk})")