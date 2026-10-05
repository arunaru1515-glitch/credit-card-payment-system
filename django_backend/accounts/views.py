from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    CardSerializer
)

from .models import Card


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

        serializer.save()

        return Response(
            {
                "message": "User registered successfully",
                "user": serializer.data
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
                "access": str(refresh.access_token)
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
            "username": request.user.username
        },
        status=status.HTTP_200_OK
    )


# =========================================================
# MODULE 2 - ADD CARD
# =========================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_card(request):

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

    # Store only masked number and last 4 digits
    card = Card.objects.create(
        user=request.user,
        card_type=card_type,
        masked_card_number=masked_card_number,
        last_four_digits=last_four_digits
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

    try:

        card = Card.objects.get(
            id=card_id,
            user=request.user
        )

        card.delete()

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