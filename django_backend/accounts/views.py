from decimal import Decimal, InvalidOperation

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    CardSerializer,
    AuditLogSerializer,
    UserSerializer,
)

from .models import Card, User, AuditLog
from .audit import record_audit_log
from .email_service import send_card_blocked_email


# =========================================================
# MODULE 1 - USER REGISTRATION
# =========================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):

    serializer = UserRegistrationSerializer(
        data=request.data
    )

    if serializer.is_valid():

        user = serializer.save()

        return Response(
            {
                "message": "User registered successfully",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                }
            },
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# =========================================================
# MODULE 1 - USER LOGIN
# =========================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):

    serializer = UserLoginSerializer(
        data=request.data
    )

    if serializer.is_valid():

        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Login successful",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "role": user.role,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                }
            },
            status=status.HTTP_200_OK
        )

    return Response(
        serializer.errors,
        status=status.HTTP_401_UNAUTHORIZED
    )


# =========================================================
# MODULE 1 - USER LOGOUT
# =========================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):

    try:

        refresh_token = request.data.get('refresh')

        if not refresh_token:

            return Response(
                {
                    "error": "Refresh token is required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        token = RefreshToken(refresh_token)

        token.blacklist()

        return Response(
            {
                "message": "Logout successful"
            },
            status=status.HTTP_200_OK
        )

    except Exception:

        return Response(
            {
                "error": "Invalid or expired refresh token"
            },
            status=status.HTTP_400_BAD_REQUEST
        )


# =========================================================
# MODULE 1 - PROTECTED PROFILE
# =========================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_profile(request):

    return Response(
        {
            "message": "You are authenticated",
            "username": request.user.username,
            "email": request.user.email,
            "role": getattr(request.user, "role", "CUSTOMER"),
            "is_staff": request.user.is_staff,
            "is_superuser": request.user.is_superuser,
        },
        status=status.HTTP_200_OK
    )


# =========================================================
# MODULE 2 - ADD CARD
# =========================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_card(request):

    # RBAC check: Read-Only role cannot add cards
    if getattr(request.user, "role", None) == User.ROLE_READ_ONLY:
        return Response(
            {
                "error": "Read-Only role cannot add cards"
            },
            status=status.HTTP_403_FORBIDDEN
        )

    card_number = request.data.get('card_number')
    card_type = request.data.get('card_type')

    # Check card number
    if not card_number:

        return Response(
            {
                "error": "Card number is required"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check card type
    if card_type not in ['credit', 'debit']:

        return Response(
            {
                "error": "Card type must be credit or debit"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Convert card number to string
    card_number = str(card_number)

    # Remove spaces
    card_number = card_number.replace(" ", "")

    # Check digits
    if not card_number.isdigit():

        return Response(
            {
                "error": "Card number must contain only digits"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check card number length
    if len(card_number) < 13 or len(card_number) > 19:

        return Response(
            {
                "error": "Invalid card number"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get last 4 digits
    last_four_digits = card_number[-4:]

    # Create masked card number
    masked_card_number = "**** **** **** " + last_four_digits

    # Credit limit rules
    if card_type == 'credit':
        credit_limit = 100000.00
    else:
        credit_limit = 0.00

    # Create card
    card = Card.objects.create(
        user=request.user,
        card_type=card_type,
        masked_card_number=masked_card_number,
        last_four_digits=last_four_digits,
        credit_limit=credit_limit
    )

    return Response(
        {
            "message": "Card added successfully",
            "card": CardSerializer(card).data
        },
        status=status.HTTP_201_CREATED
    )


# =========================================================
# MODULE 2 - VIEW SAVED CARDS
# =========================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_cards(request):

    show_all = request.query_params.get("all") == "true"
    user_id = request.query_params.get("user_id")

    # Staff / elevated roles can list all cards when requested
    if (
        request.user.is_admin_role
        or request.user.is_support_role
        or request.user.is_read_only_role
    ) and (show_all or user_id):
        if user_id:
            cards = Card.objects.filter(user_id=user_id).select_related("user")
        else:
            cards = Card.objects.all().select_related("user")
    else:
        cards = Card.objects.filter(
            user=request.user
        )

    serializer = CardSerializer(
        cards,
        many=True
    )

    return Response(
        {
            "message": "Cards retrieved successfully",
            "cards": serializer.data
        },
        status=status.HTTP_200_OK
    )


# =========================================================
# MODULE 2 - DELETE CARD
# =========================================================

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_card(request, card_id):

    # Read-Only role cannot delete
    if getattr(request.user, "role", None) == User.ROLE_READ_ONLY:
        return Response(
            {
                "error": "Read-Only role cannot delete cards"
            },
            status=status.HTTP_403_FORBIDDEN
        )

    # Support role cannot delete cards
    if getattr(request.user, "role", None) == User.ROLE_SUPPORT:
        return Response(
            {
                "error": "Support role cannot delete cards. Admin permission required."
            },
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        # Admin can delete any card; Customer can only delete their own
        if request.user.is_admin_role:
            card = Card.objects.get(id=card_id)
        else:
            card = Card.objects.get(
                id=card_id,
                user=request.user
            )

        old_data = {
            "card_id": card.id,
            "masked_card_number": card.masked_card_number,
            "owner": card.user.username,
        }

        card.delete()

        # Audit log when admin deletes
        if request.user.is_admin_role:
            record_audit_log(
                action="CARD_DELETE",
                target_type="Card",
                target_id=card_id,
                actor=request.user,
                description=f"Card {old_data['masked_card_number']} deleted by admin {request.user.username}",
                old_value=old_data,
                request=request,
            )

        return Response(
            {
                "message": "Card deleted successfully"
            },
            status=status.HTTP_200_OK
        )

    except Card.DoesNotExist:

        return Response(
            {
                "error": "Card not found"
            },
            status=status.HTTP_404_NOT_FOUND
        )


# =========================================================
# RBAC ADMIN ACTIONS - CARD BLOCK
# =========================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def block_card(request, card_id):
    """
    Admin and Support roles can block a card.
    Audit log is created and alert email is triggered.
    """
    if not (request.user.is_admin_role or request.user.is_support_role):
        return Response(
            {
                "error": "Permission denied. Admin or Support role required to block cards."
            },
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        card = Card.objects.get(id=card_id)
    except Card.DoesNotExist:
        return Response(
            {"error": "Card not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    was_blocked = card.is_blocked
    card.is_blocked = True
    card.save(update_fields=['is_blocked'])

    reason = request.data.get("reason", "Administrative block")

    # Audit log
    record_audit_log(
        action="CARD_BLOCK",
        target_type="Card",
        target_id=str(card.id),
        actor=request.user,
        description=f"Card {card.masked_card_number} blocked by {request.user.username} ({request.user.role}): {reason}",
        old_value={"is_blocked": was_blocked},
        new_value={"is_blocked": True, "reason": reason},
        request=request,
    )

    if not was_blocked:
        send_card_blocked_email(card)

    return Response(
        {
            "message": "Card blocked successfully",
            "card": CardSerializer(card).data
        },
        status=status.HTTP_200_OK
    )


# =========================================================
# RBAC ADMIN ACTIONS - CARD UNBLOCK
# =========================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unblock_card(request, card_id):
    """
    Admin and Support roles can unblock a card.
    Audit log is created.
    """
    if not (request.user.is_admin_role or request.user.is_support_role):
        return Response(
            {
                "error": "Permission denied. Admin or Support role required to unblock cards."
            },
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        card = Card.objects.get(id=card_id)
    except Card.DoesNotExist:
        return Response(
            {"error": "Card not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    was_blocked = card.is_blocked
    card.is_blocked = False
    card.save(update_fields=['is_blocked'])

    reason = request.data.get("reason", "Administrative unblock")

    # Audit log
    record_audit_log(
        action="CARD_UNBLOCK",
        target_type="Card",
        target_id=str(card.id),
        actor=request.user,
        description=f"Card {card.masked_card_number} unblocked by {request.user.username} ({request.user.role}): {reason}",
        old_value={"is_blocked": was_blocked},
        new_value={"is_blocked": False, "reason": reason},
        request=request,
    )

    return Response(
        {
            "message": "Card unblocked successfully",
            "card": CardSerializer(card).data
        },
        status=status.HTTP_200_OK
    )


# =========================================================
# RBAC ADMIN ACTIONS - CREDIT LIMIT UPDATE
# =========================================================

@api_view(['PATCH', 'POST'])
@permission_classes([IsAuthenticated])
def update_credit_limit(request, card_id):
    """
    ONLY Admin role can update credit limit.
    Support, Read-Only, and Customer are denied.
    Audit log is created.
    """
    if not request.user.is_admin_role:
        return Response(
            {
                "error": "Permission denied. Only Admin role can update credit limits."
            },
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        card = Card.objects.get(id=card_id)
    except Card.DoesNotExist:
        return Response(
            {"error": "Card not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if card.card_type != 'credit':
        return Response(
            {"error": "Credit limit can only be set for credit cards."},
            status=status.HTTP_400_BAD_REQUEST
        )

    new_limit = request.data.get("credit_limit")
    if new_limit is None:
        return Response(
            {"error": "credit_limit is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        new_limit_decimal = Decimal(str(new_limit))
        if new_limit_decimal <= Decimal("0.00"):
            raise ValueError()
    except (InvalidOperation, ValueError, TypeError):
        return Response(
            {"error": "credit_limit must be a valid positive number"},
            status=status.HTTP_400_BAD_REQUEST
        )

    old_limit = card.credit_limit
    card.credit_limit = new_limit_decimal
    card.save(update_fields=['credit_limit'])

    reason = request.data.get("reason", "Administrative credit limit update")

    old_limit_str = f"{Decimal(str(old_limit)):.2f}"
    new_limit_str = f"{Decimal(str(new_limit_decimal)):.2f}"

    # Record Audit Log
    record_audit_log(
        action="CREDIT_LIMIT_UPDATE",
        target_type="Card",
        target_id=str(card.id),
        actor=request.user,
        description=f"Credit limit updated from ₹{old_limit_str} to ₹{new_limit_str} by {request.user.username}",
        old_value={"credit_limit": old_limit_str},
        new_value={"credit_limit": new_limit_str, "reason": reason},
        request=request,
    )

    return Response(
        {
            "message": "Credit limit updated successfully",
            "card": CardSerializer(card).data
        },
        status=status.HTTP_200_OK
    )


# =========================================================
# RBAC ADMIN ACTIONS - AUDIT LOGS
# =========================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_audit_logs(request):
    """
    Admin, Support, and Read-Only can inspect audit logs.
    Regular customers are forbidden.
    """
    if not (
        request.user.is_admin_role
        or request.user.is_support_role
        or request.user.is_read_only_role
    ):
        return Response(
            {
                "error": "Permission denied. Staff role required to view audit logs."
            },
            status=status.HTTP_403_FORBIDDEN
        )

    queryset = AuditLog.objects.all().select_related("actor")

    action = request.query_params.get("action")
    if action:
        queryset = queryset.filter(action=action)

    target_type = request.query_params.get("target_type")
    if target_type:
        queryset = queryset.filter(target_type=target_type)

    actor_username = request.query_params.get("actor")
    if actor_username:
        queryset = queryset.filter(actor__username=actor_username)

    serializer = AuditLogSerializer(queryset[:100], many=True)

    return Response(
        {
            "total_count": queryset.count(),
            "audit_logs": serializer.data
        },
        status=status.HTTP_200_OK
    )


# =========================================================
# RBAC ADMIN ACTIONS - USER & ROLE MANAGEMENT
# =========================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_users(request):
    """
    Admin and Support can view user list.
    """
    if not (request.user.is_admin_role or request.user.is_support_role):
        return Response(
            {"error": "Permission denied. Admin or Support role required."},
            status=status.HTTP_403_FORBIDDEN
        )

    users = User.objects.all().order_by("-date_joined")
    serializer = UserSerializer(users, many=True)
    return Response(
        {"users": serializer.data},
        status=status.HTTP_200_OK
    )


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_user_role(request, user_id):
    """
    Only Admin can assign or modify user roles.
    """
    if not request.user.is_admin_role:
        return Response(
            {"error": "Permission denied. Only Admin can update user roles."},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    new_role = request.data.get("role")
    valid_roles = dict(User.ROLE_CHOICES).keys()

    if new_role not in valid_roles:
        return Response(
            {"error": f"Invalid role. Must be one of: {list(valid_roles)}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    old_role = user.role
    user.role = new_role
    user.save(update_fields=['role'])

    record_audit_log(
        action="ROLE_UPDATE",
        target_type="User",
        target_id=str(user.id),
        actor=request.user,
        description=f"User {user.username} role changed from {old_role} to {new_role}",
        old_value={"role": old_role},
        new_value={"role": new_role},
        request=request,
    )

    return Response(
        {
            "message": "User role updated successfully",
            "user": UserSerializer(user).data
        },
        status=status.HTTP_200_OK
    )