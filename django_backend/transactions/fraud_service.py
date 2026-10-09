from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from .models import Transaction, FraudLog


HIGH_VALUE_THRESHOLD = Decimal("10000.00")
BURST_WINDOW_MINUTES = 10
BURST_AMOUNT_LIMIT = Decimal("25000.00")
LOCATION_WINDOW_MINUTES = 15
VELOCITY_WINDOW_MINUTES = 2
VELOCITY_COUNT_THRESHOLD = 3


def extract_request_metadata(request):
    """
    Extracts IP address, device user-agent, and location (if header present) from request.
    """
    if not request:
        return {
            "ip_address": None,
            "device_info": "Web",
            "location": "Unknown",
        }

    # IP Address
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")

    # Device / User-Agent
    device_info = request.META.get("HTTP_USER_AGENT", "Web")
    if device_info and len(device_info) > 250:
        device_info = device_info[:250]

    # Location (Check custom headers e.g. X-User-Location or GeoIP headers)
    location = (
        request.data.get("location")
        if hasattr(request, "data") and isinstance(request.data, dict) and request.data.get("location")
        else request.META.get("HTTP_X_USER_LOCATION", "Unknown")
    )

    return {
        "ip_address": ip,
        "device_info": device_info or "Web",
        "location": location or "Unknown",
    }


def evaluate_transaction_fraud(
    user,
    amount: Decimal,
    card=None,
    ip_address=None,
    location=None,
    device_info=None,
):
    """
    Rule-based fraud detection engine:
    1. Multiple high-value transactions in short time (>= ₹10,000 in 10 minutes or burst > ₹25,000).
    2. Rapid transactions from different locations / devices / IPs (within 15 minutes).
    3. Velocity surge (>= 3 transactions within 2 minutes).

    Returns:
    {
        "is_flagged": bool,
        "fraud_status": "FLAGGED" | "SUSPICIOUS" | "CLEAN",
        "risk_level": "HIGH" | "MEDIUM" | "LOW",
        "rules_triggered": list[str],
        "descriptions": list[str],
    }
    """
    now = timezone.now()
    rules_triggered = []
    descriptions = []
    risk_level = "LOW"

    try:
        amount_decimal = Decimal(str(amount))
    except Exception:
        amount_decimal = Decimal("0.00")

    # ------------------------------------------------------------------
    # RULE 1: MULTIPLE HIGH-VALUE TRANSACTIONS IN SHORT TIME
    # ------------------------------------------------------------------
    burst_start_time = now - timedelta(minutes=BURST_WINDOW_MINUTES)
    recent_transactions_in_burst = Transaction.objects.filter(
        user=user,
        transaction_date__gte=burst_start_time,
    ).exclude(status="FAILED")

    if amount_decimal >= HIGH_VALUE_THRESHOLD:
        high_value_count = recent_transactions_in_burst.filter(
            amount__gte=HIGH_VALUE_THRESHOLD
        ).count()

        if high_value_count >= 1:
            rules_triggered.append("Multiple high-value transactions in short time")
            descriptions.append(
                f"User initiated {high_value_count + 1} high-value transactions (>= ₹{HIGH_VALUE_THRESHOLD:,.2f}) "
                f"within {BURST_WINDOW_MINUTES} minutes."
            )
            risk_level = "HIGH"

    # Total burst amount threshold
    burst_total = sum(
        (t.amount for t in recent_transactions_in_burst), Decimal("0.00")
    ) + amount_decimal
    if burst_total >= BURST_AMOUNT_LIMIT:
        rule_name = "Cumulative high spending burst"
        if rule_name not in rules_triggered:
            rules_triggered.append(rule_name)
            descriptions.append(
                f"Cumulative spending reached ₹{burst_total:,.2f} within {BURST_WINDOW_MINUTES} minutes "
                f"(Threshold: ₹{BURST_AMOUNT_LIMIT:,.2f})."
            )
            if risk_level != "HIGH":
                risk_level = "HIGH"

    # ------------------------------------------------------------------
    # RULE 2: RAPID TRANSACTIONS FROM DIFFERENT LOCATIONS / DEVICES
    # ------------------------------------------------------------------
    loc_window_start = now - timedelta(minutes=LOCATION_WINDOW_MINUTES)
    recent_tx = Transaction.objects.filter(
        user=user,
        transaction_date__gte=loc_window_start,
    ).order_by("-transaction_date").first()

    if recent_tx:
        # Check Location difference
        curr_loc = location or "Unknown"
        prev_loc = recent_tx.location or "Unknown"
        if (
            curr_loc != "Unknown"
            and prev_loc != "Unknown"
            and curr_loc.lower() != prev_loc.lower()
        ):
            rules_triggered.append("Rapid transactions from different locations")
            time_diff = int((now - recent_tx.transaction_date).total_seconds() / 60)
            descriptions.append(
                f"Location changed from '{prev_loc}' to '{curr_loc}' within {time_diff} minutes."
            )
            risk_level = "HIGH"

        # Check Device / User-Agent difference
        curr_device = device_info or "Web"
        prev_device = recent_tx.device_info or "Web"
        if (
            curr_device != "Web"
            and prev_device != "Web"
            and curr_device != prev_device
        ):
            rules_triggered.append("Rapid transactions from different devices")
            time_diff = int((now - recent_tx.transaction_date).total_seconds() / 60)
            descriptions.append(
                f"Different device detected within {time_diff} minutes."
            )
            if risk_level != "HIGH":
                risk_level = "MEDIUM"

        # Check IP Address difference
        if ip_address and recent_tx.ip_address and ip_address != recent_tx.ip_address:
            rule_name = "Rapid transactions from different IP addresses"
            if rule_name not in rules_triggered:
                rules_triggered.append(rule_name)
                descriptions.append(
                    f"IP changed from {recent_tx.ip_address} to {ip_address} within {LOCATION_WINDOW_MINUTES} minutes."
                )
                if risk_level == "LOW":
                    risk_level = "MEDIUM"

    # ------------------------------------------------------------------
    # RULE 3: TRANSACTION VELOCITY SURGE
    # ------------------------------------------------------------------
    velocity_window_start = now - timedelta(minutes=VELOCITY_WINDOW_MINUTES)
    recent_velocity_count = Transaction.objects.filter(
        user=user,
        transaction_date__gte=velocity_window_start,
    ).count()

    if recent_velocity_count >= VELOCITY_COUNT_THRESHOLD:
        rule_name = "High transaction velocity surge"
        if rule_name not in rules_triggered:
            rules_triggered.append(rule_name)
            descriptions.append(
                f"High velocity: {recent_velocity_count + 1} transactions requested within {VELOCITY_WINDOW_MINUTES} minutes."
            )
            risk_level = "HIGH"

    # ------------------------------------------------------------------
    # CONSOLIDATED DECISION
    # ------------------------------------------------------------------
    if not rules_triggered:
        return {
            "is_flagged": False,
            "fraud_status": "CLEAN",
            "risk_level": "LOW",
            "rules_triggered": [],
            "descriptions": [],
        }

    fraud_status = "FLAGGED" if risk_level == "HIGH" else "SUSPICIOUS"

    return {
        "is_flagged": True,
        "fraud_status": fraud_status,
        "risk_level": risk_level,
        "rules_triggered": rules_triggered,
        "descriptions": descriptions,
    }


def record_fraud_log(
    user,
    transaction=None,
    card=None,
    amount=None,
    risk_level="MEDIUM",
    rule_triggered="",
    description="",
    ip_address=None,
    location="Unknown",
    device_info="Web",
):
    """
    Records an entry in FraudLog for admin/compliance review.
    """
    amt = amount if amount is not None else (transaction.amount if transaction else Decimal("0.00"))
    return FraudLog.objects.create(
        user=user,
        transaction=transaction,
        card=card or (transaction.card if transaction else None),
        amount=amt,
        risk_level=risk_level,
        rule_triggered=rule_triggered,
        description=description,
        ip_address=ip_address,
        location=location or "Unknown",
        device_info=device_info or "Web",
        status="UNDER_REVIEW",
    )
