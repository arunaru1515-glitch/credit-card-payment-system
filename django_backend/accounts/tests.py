from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Card


User = get_user_model()


class AuthenticationTests(TestCase):
    """
    Tests for Module 1:
    User Registration
    User Login
    JWT Authentication
    Logout
    Protected Profile
    """

    def setUp(self):
        self.client = APIClient()

        self.username = "testuser"
        self.email = "testuser@example.com"
        self.password = "Test@12345"

        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password
        )

    # ==================================================
    # USER REGISTRATION
    # ==================================================

    def test_user_registration_success(self):
        response = self.client.post(
            "/api/register/",
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "NewUser@12345"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 201)

        self.assertEqual(
            response.data["message"],
            "User registered successfully"
        )

        self.assertTrue(
            User.objects.filter(
                username="newuser"
            ).exists()
        )

    def test_user_registration_invalid_data(self):
        response = self.client.post(
            "/api/register/",
            {
                "username": "",
                "email": "invalid-email",
                "password": ""
            },
            format="json"
        )

        self.assertEqual(response.status_code, 400)

    # ==================================================
    # USER LOGIN
    # ==================================================

    def test_user_login_success(self):
        response = self.client.post(
            "/api/login/",
            {
                "username": self.username,
                "password": self.password
            },
            format="json"
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.data["message"],
            "Login successful"
        )

        self.assertIn("refresh", response.data)
        self.assertIn("access", response.data)

    def test_user_login_invalid_password(self):
        response = self.client.post(
            "/api/login/",
            {
                "username": self.username,
                "password": "WrongPassword@123"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 401)

    # ==================================================
    # PROTECTED PROFILE
    # ==================================================

    def test_protected_profile_requires_authentication(self):
        response = self.client.get(
            "/api/profile/"
        )

        self.assertEqual(response.status_code, 401)

    def test_protected_profile_authenticated(self):
        refresh = RefreshToken.for_user(self.user)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
        )

        response = self.client.get(
            "/api/profile/"
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.data["username"],
            self.username
        )

        self.assertEqual(
            response.data["message"],
            "You are authenticated"
        )

    # ==================================================
    # USER LOGOUT
    # ==================================================

    def test_user_logout_success(self):
        refresh = RefreshToken.for_user(self.user)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
        )

        response = self.client.post(
            "/api/logout/",
            {
                "refresh": str(refresh)
            },
            format="json"
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.data["message"],
            "Logout successful"
        )

    def test_user_logout_without_refresh_token(self):
        refresh = RefreshToken.for_user(self.user)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
        )

        response = self.client.post(
            "/api/logout/",
            {},
            format="json"
        )

        self.assertEqual(response.status_code, 400)

        self.assertEqual(
            response.data["error"],
            "Refresh token is required"
        )


class CardManagementTests(TestCase):
    """
    Tests for Module 2:
    Add Card
    View Saved Cards
    Delete Card
    Card Validation
    Card Security
    """

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="carduser",
            email="carduser@example.com",
            password="Card@12345"
        )

        self.other_user = User.objects.create_user(
            username="otheruser",
            email="otheruser@example.com",
            password="Other@12345"
        )

        self.client.force_authenticate(
            user=self.user
        )

    # ==================================================
    # ADD CARD
    # ==================================================

    def test_add_credit_card_success(self):
        response = self.client.post(
            "/api/cards/",
            {
                "card_number": "4111111111111111",
                "card_type": "credit"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 201)

        self.assertEqual(
            response.data["message"],
            "Card added successfully"
        )

        card = Card.objects.get(
            user=self.user
        )

        self.assertEqual(
            card.last_four_digits,
            "1111"
        )

        self.assertEqual(
            card.masked_card_number,
            "**** **** **** 1111"
        )

        # Actual card number must not be stored.
        self.assertFalse(
            hasattr(card, "card_number")
        )

    def test_add_debit_card_success(self):
        response = self.client.post(
            "/api/cards/",
            {
                "card_number": "5555555555554444",
                "card_type": "debit"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 201)

        card = Card.objects.get(
            user=self.user
        )

        self.assertEqual(
            card.card_type,
            "debit"
        )

        self.assertEqual(
            card.last_four_digits,
            "4444"
        )

    def test_add_card_without_card_number(self):
        response = self.client.post(
            "/api/cards/",
            {
                "card_type": "credit"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 400)

        self.assertEqual(
            response.data["error"],
            "Card number is required"
        )

    def test_add_card_invalid_card_type(self):
        response = self.client.post(
            "/api/cards/",
            {
                "card_number": "4111111111111111",
                "card_type": "invalid"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 400)

        self.assertEqual(
            response.data["error"],
            "Card type must be credit or debit"
        )

    def test_add_card_non_numeric_card_number(self):
        response = self.client.post(
            "/api/cards/",
            {
                "card_number": "4111abcd11111111",
                "card_type": "credit"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 400)

        self.assertEqual(
            response.data["error"],
            "Card number must contain only digits"
        )

    def test_add_card_invalid_length(self):
        response = self.client.post(
            "/api/cards/",
            {
                "card_number": "123456",
                "card_type": "credit"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 400)

        self.assertEqual(
            response.data["error"],
            "Invalid card number"
        )

    # ==================================================
    # VIEW SAVED CARDS
    # ==================================================

    def test_list_saved_cards(self):
        Card.objects.create(
            user=self.user,
            card_type="credit",
            masked_card_number="**** **** **** 1111",
            last_four_digits="1111"
        )

        Card.objects.create(
            user=self.user,
            card_type="debit",
            masked_card_number="**** **** **** 4444",
            last_four_digits="4444"
        )

        response = self.client.get(
            "/api/cards/list/"
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.data["message"],
            "Cards retrieved successfully"
        )

        self.assertEqual(
            len(response.data["cards"]),
            2
        )

    def test_list_cards_only_returns_current_users_cards(self):
        Card.objects.create(
            user=self.user,
            card_type="credit",
            masked_card_number="**** **** **** 1111",
            last_four_digits="1111"
        )

        Card.objects.create(
            user=self.other_user,
            card_type="debit",
            masked_card_number="**** **** **** 2222",
            last_four_digits="2222"
        )

        response = self.client.get(
            "/api/cards/list/"
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            len(response.data["cards"]),
            1
        )

        self.assertEqual(
            response.data["cards"][0]["last_four_digits"],
            "1111"
        )

    # ==================================================
    # DELETE CARD
    # ==================================================

    def test_delete_card_success(self):
        card = Card.objects.create(
            user=self.user,
            card_type="credit",
            masked_card_number="**** **** **** 1111",
            last_four_digits="1111"
        )

        response = self.client.delete(
            f"/api/cards/{card.id}/"
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.data["message"],
            "Card deleted successfully"
        )

        self.assertFalse(
            Card.objects.filter(
                id=card.id
            ).exists()
        )

    def test_delete_nonexistent_card(self):
        response = self.client.delete(
            "/api/cards/99999/"
        )

        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            response.data["error"],
            "Card not found"
        )

    def test_user_cannot_delete_another_users_card(self):
        other_card = Card.objects.create(
            user=self.other_user,
            card_type="credit",
            masked_card_number="**** **** **** 2222",
            last_four_digits="2222"
        )

        response = self.client.delete(
            f"/api/cards/{other_card.id}/"
        )

        self.assertEqual(response.status_code, 404)

        self.assertTrue(
            Card.objects.filter(
                id=other_card.id
            ).exists()
        )