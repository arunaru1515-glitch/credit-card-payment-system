from .models import AuditLog


def get_client_ip(request):
    """Extract client IP address from request."""
    if not request:
        return None
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def record_audit_log(
    action: str,
    target_type: str = "Card",
    target_id=None,
    actor=None,
    description: str = None,
    old_value=None,
    new_value=None,
    request=None
):
    """
    Utility to record an audit log entry for administrative or security actions.
    """
    ip_address = get_client_ip(request) if request else None

    if actor is None and request and getattr(request, "user", None) and request.user.is_authenticated:
        actor = request.user

    return AuditLog.objects.create(
        actor=actor,
        action=action,
        target_type=target_type,
        target_id=str(target_id) if target_id is not None else None,
        description=description,
        old_value=old_value,
        new_value=new_value,
        ip_address=ip_address,
    )
