from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Card, AuditLog
from .email_service import send_card_blocked_email
from .audit import record_audit_log


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "role",
        "is_staff",
        "is_active",
        "date_joined",
    )
    list_filter = (
        "role",
        "is_staff",
        "is_superuser",
        "is_active",
    )
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Role & Permissions", {"fields": ("role",)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Role & Permissions", {"fields": ("role",)}),
    )

    def save_model(self, request, obj, form, change):
        old_role = None
        if change:
            old_user = User.objects.get(pk=obj.pk)
            old_role = old_user.role

        super().save_model(request, obj, form, change)

        if change and old_role and old_role != obj.role:
            record_audit_log(
                action="ROLE_UPDATE",
                target_type="User",
                target_id=str(obj.pk),
                actor=request.user,
                description=f"User {obj.username} role changed from {old_role} to {obj.role}",
                old_value={"role": old_role},
                new_value={"role": obj.role},
                request=request,
            )


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
        old_limit = None

        if change:
            old_card = Card.objects.get(pk=obj.pk)
            was_blocked = old_card.is_blocked
            old_limit = old_card.credit_limit

        super().save_model(request, obj, form, change)

        # Audit log for block/unblock
        if change and was_blocked != obj.is_blocked:
            action = "CARD_BLOCK" if obj.is_blocked else "CARD_UNBLOCK"
            record_audit_log(
                action=action,
                target_type="Card",
                target_id=str(obj.pk),
                actor=request.user,
                description=f"Card {obj.masked_card_number} was {'blocked' if obj.is_blocked else 'unblocked'} via Django Admin",
                old_value={"is_blocked": was_blocked},
                new_value={"is_blocked": obj.is_blocked},
                request=request,
            )

        # Audit log for credit limit update
        if change and old_limit is not None and old_limit != obj.credit_limit:
            record_audit_log(
                action="CREDIT_LIMIT_UPDATE",
                target_type="Card",
                target_id=str(obj.pk),
                actor=request.user,
                description=f"Credit limit updated from {old_limit} to {obj.credit_limit} via Django Admin",
                old_value={"credit_limit": str(old_limit)},
                new_value={"credit_limit": str(obj.credit_limit)},
                request=request,
            )

        if not was_blocked and obj.is_blocked:
            send_card_blocked_email(obj)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
        "actor",
        "action",
        "target_type",
        "target_id",
        "ip_address",
    )
    list_filter = (
        "action",
        "target_type",
        "created_at",
    )
    search_fields = (
        "actor__username",
        "target_id",
        "description",
        "ip_address",
    )
    readonly_fields = (
        "actor",
        "action",
        "target_type",
        "target_id",
        "description",
        "old_value",
        "new_value",
        "ip_address",
        "created_at",
    )
    ordering = (
        "-created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False