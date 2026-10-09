from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Card, AuditLog


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


class RoleBasedAccessControlTests(TestCase):
    """
    Tests for RBAC and Audit Logging:
    - Roles: Admin, Support, Read-Only, Customer
    - Card block / unblock with audit logs
    - Credit limit updates with role protection
    - Audit log API and persistence
    - User role updates
    """

    def setUp(self):
        self.client = APIClient()

        self.admin_user = User.objects.create_user(
            username="admin_user",
            email="admin@example.com",
            password="Admin@12345",
            role=User.ROLE_ADMIN
        )

        self.support_user = User.objects.create_user(
            username="support_user",
            email="support@example.com",
            password="Support@12345",
            role=User.ROLE_SUPPORT
        )

        self.read_only_user = User.objects.create_user(
            username="readonly_user",
            email="readonly@example.com",
            password="ReadOnly@12345",
            role=User.ROLE_READ_ONLY
        )

        self.customer_user = User.objects.create_user(
            username="customer_user",
            email="customer@example.com",
            password="Customer@12345",
            role=User.ROLE_CUSTOMER
        )

        self.card = Card.objects.create(
            user=self.customer_user,
            card_type="credit",
            masked_card_number="**** **** **** 8888",
            last_four_digits="8888",
            credit_limit=100000.00,
            is_blocked=False
        )

    # --------------------------------------------------------
    # ROLE ASSIGNMENT & PERMISSION PROPERTIES
    # --------------------------------------------------------

    def test_user_role_defaults_and_properties(self):
        default_user = User.objects.create_user(
            username="defaultuser",
            email="default@example.com",
            password="Pass@12345"
        )
        self.assertEqual(default_user.role, User.ROLE_CUSTOMER)
        self.assertFalse(default_user.is_admin_role)
        self.assertFalse(default_user.is_support_role)
        self.assertFalse(default_user.is_read_only_role)

        self.assertTrue(self.admin_user.is_admin_role)
        self.assertTrue(self.admin_user.is_support_role)
        self.assertTrue(self.admin_user.is_read_only_role)

        self.assertFalse(self.support_user.is_admin_role)
        self.assertTrue(self.support_user.is_support_role)
        self.assertTrue(self.support_user.is_read_only_role)

        self.assertFalse(self.read_only_user.is_admin_role)
        self.assertFalse(self.read_only_user.is_support_role)
        self.assertTrue(self.read_only_user.is_read_only_role)

    # --------------------------------------------------------
    # CARD BLOCKING RBAC & AUDIT LOGS
    # --------------------------------------------------------

    def test_admin_can_block_card_and_creates_audit_log(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            f"/api/cards/{self.card.id}/block/",
            {"reason": "Suspicious activity detected"},
            format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.card.refresh_from_db()
        self.assertTrue(self.card.is_blocked)

        # Audit log verification
        log = AuditLog.objects.filter(
            action="CARD_BLOCK",
            target_id=str(self.card.id)
        ).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.actor, self.admin_user)
        self.assertEqual(log.target_type, "Card")
        self.assertEqual(log.new_value["is_blocked"], True)

    def test_support_can_block_and_unblock_card(self):
        self.client.force_authenticate(user=self.support_user)

        # Block
        response_block = self.client.post(
            f"/api/cards/{self.card.id}/block/",
            {"reason": "Support requested card hold"},
            format="json"
        )
        self.assertEqual(response_block.status_code, 200)
        self.card.refresh_from_db()
        self.assertTrue(self.card.is_blocked)

        # Unblock
        response_unblock = self.client.post(
            f"/api/cards/{self.card.id}/unblock/",
            {"reason": "Customer identity verified"},
            format="json"
        )
        self.assertEqual(response_unblock.status_code, 200)
        self.card.refresh_from_db()
        self.assertFalse(self.card.is_blocked)

        unblock_log = AuditLog.objects.filter(
            action="CARD_UNBLOCK",
            target_id=str(self.card.id)
        ).first()
        self.assertIsNotNone(unblock_log)
        self.assertEqual(unblock_log.actor, self.support_user)

    def test_readonly_user_cannot_block_card(self):
        self.client.force_authenticate(user=self.read_only_user)
        response = self.client.post(
            f"/api/cards/{self.card.id}/block/",
            {"reason": "Attempting unauthorized block"},
            format="json"
        )
        self.assertEqual(response.status_code, 403)
        self.card.refresh_from_db()
        self.assertFalse(self.card.is_blocked)

    def test_customer_cannot_block_card_via_admin_endpoint(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.post(
            f"/api/cards/{self.card.id}/block/",
            {"reason": "Unauthorized customer attempt"},
            format="json"
        )
        self.assertEqual(response.status_code, 403)

    # --------------------------------------------------------
    # CREDIT LIMIT UPDATES RBAC & AUDIT LOGS
    # --------------------------------------------------------

    def test_admin_can_update_credit_limit_and_creates_audit_log(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(
            f"/api/cards/{self.card.id}/limit/",
            {"credit_limit": 150000.00, "reason": "Good credit score"},
            format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.card.refresh_from_db()
        self.assertEqual(float(self.card.credit_limit), 150000.00)

        log = AuditLog.objects.filter(
            action="CREDIT_LIMIT_UPDATE",
            target_id=str(self.card.id)
        ).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.actor, self.admin_user)
        self.assertEqual(log.old_value["credit_limit"], "100000.00")
        self.assertEqual(log.new_value["credit_limit"], "150000.00")

    def test_support_user_forbidden_from_updating_credit_limit(self):
        self.client.force_authenticate(user=self.support_user)
        response = self.client.patch(
            f"/api/cards/{self.card.id}/limit/",
            {"credit_limit": 200000.00},
            format="json"
        )
        self.assertEqual(response.status_code, 403)

    def test_readonly_user_forbidden_from_updating_credit_limit(self):
        self.client.force_authenticate(user=self.read_only_user)
        response = self.client.patch(
            f"/api/cards/{self.card.id}/limit/",
            {"credit_limit": 200000.00},
            format="json"
        )
        self.assertEqual(response.status_code, 403)

    # --------------------------------------------------------
    # AUDIT LOGS INSPECTION API
    # --------------------------------------------------------

    def test_staff_can_view_audit_logs_but_customer_forbidden(self):
        # Create an audit log
        AuditLog.objects.create(
            actor=self.admin_user,
            action="CARD_BLOCK",
            target_type="Card",
            target_id=str(self.card.id),
            description="Test log"
        )

        # Admin can view
        self.client.force_authenticate(user=self.admin_user)
        resp_admin = self.client.get("/api/audit-logs/")
        self.assertEqual(resp_admin.status_code, 200)
        self.assertGreaterEqual(resp_admin.data["total_count"], 1)

        # Support can view
        self.client.force_authenticate(user=self.support_user)
        resp_support = self.client.get("/api/audit-logs/")
        self.assertEqual(resp_support.status_code, 200)

        # Read-Only can view
        self.client.force_authenticate(user=self.read_only_user)
        resp_ro = self.client.get("/api/audit-logs/")
        self.assertEqual(resp_ro.status_code, 200)

        # Customer forbidden
        self.client.force_authenticate(user=self.customer_user)
        resp_customer = self.client.get("/api/audit-logs/")
        self.assertEqual(resp_customer.status_code, 403)

    # --------------------------------------------------------
    # USER ROLE MANAGEMENT API
    # --------------------------------------------------------

    def test_admin_can_update_user_role(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(
            f"/api/users/{self.customer_user.id}/role/",
            {"role": User.ROLE_SUPPORT},
            format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.customer_user.refresh_from_db()
        self.assertEqual(self.customer_user.role, User.ROLE_SUPPORT)

        # Check audit log for role update
        log = AuditLog.objects.filter(
            action="ROLE_UPDATE",
            target_id=str(self.customer_user.id)
        ).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.actor, self.admin_user)

    def test_non_admin_cannot_update_user_role(self):
        self.client.force_authenticate(user=self.support_user)
        response = self.client.patch(
            f"/api/users/{self.customer_user.id}/role/",
            {"role": User.ROLE_ADMIN},
            format="json"
        )
        self.assertEqual(response.status_code, 403)