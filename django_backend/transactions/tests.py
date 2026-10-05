from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import Card
from .models import Transaction


User = get_user_model()


class TransactionManagementTests(TestCase):
    """
    Tests for:
    - Creating PENDING transactions
    - Updating transaction status
    - Transaction ownership
    - Transaction history
    - Status filtering
    - Amount filtering
    - Date filtering
    """

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="transactionuser",
            email="transactionuser@example.com",
            password="Transaction@12345"
        )

        self.other_user = User.objects.create_user(
            username="othertransactionuser",
            email="othertransaction@example.com",
            password="Other@12345"
        )

        self.card = Card.objects.create(
            user=self.user,
            card_type="credit",
            masked_card_number="**** **** **** 1111",
            last_four_digits="1111"
        )

        self.other_card = Card.objects.create(
            user=self.other_user,
            card_type="credit",
            masked_card_number="**** **** **** 2222",
            last_four_digits="2222"
        )

        self.client.force_authenticate(
            user=self.user
        )

    # ==================================================
    # CREATE PENDING TRANSACTION
    # ==================================================

    def test_create_pending_transaction_success(self):
        response = self.client.post(
            "/api/transactions/create/",
            {
                "card_id": self.card.id,
                "amount": "5000.00"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            201
        )

        self.assertEqual(
            response.data["message"],
            "Pending transaction created"
        )

        transaction = Transaction.objects.get(
            user=self.user
        )

        self.assertEqual(
            transaction.amount,
            Decimal("5000.00")
        )

        self.assertEqual(
            transaction.status,
            "PENDING"
        )

        self.assertEqual(
            transaction.card,
            self.card
        )

    def test_create_transaction_without_card_id(self):
        response = self.client.post(
            "/api/transactions/create/",
            {
                "amount": "5000.00"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.data["error"],
            "card_id is required"
        )

    def test_create_transaction_without_amount(self):
        response = self.client.post(
            "/api/transactions/create/",
            {
                "card_id": self.card.id
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.data["error"],
            "amount is required"
        )

    def test_create_transaction_with_invalid_amount(self):
        response = self.client.post(
            "/api/transactions/create/",
            {
                "card_id": self.card.id,
                "amount": "invalid"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.data["error"],
            "Invalid amount"
        )

    def test_create_transaction_with_zero_amount(self):
        response = self.client.post(
            "/api/transactions/create/",
            {
                "card_id": self.card.id,
                "amount": "0"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.data["error"],
            "Amount must be greater than 0"
        )

    def test_create_transaction_with_negative_amount(self):
        response = self.client.post(
            "/api/transactions/create/",
            {
                "card_id": self.card.id,
                "amount": "-100"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.data["error"],
            "Amount must be greater than 0"
        )

    def test_create_transaction_with_nonexistent_card(self):
        response = self.client.post(
            "/api/transactions/create/",
            {
                "card_id": 99999,
                "amount": "5000.00"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            404
        )

        self.assertEqual(
            response.data["error"],
            "Card not found"
        )

    def test_user_cannot_create_transaction_using_another_users_card(self):
        response = self.client.post(
            "/api/transactions/create/",
            {
                "card_id": self.other_card.id,
                "amount": "5000.00"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            404
        )

        self.assertEqual(
            response.data["error"],
            "Card not found"
        )

    # ==================================================
    # UPDATE TRANSACTION - SUCCESS
    # ==================================================

    def test_update_transaction_to_success(self):
        transaction = Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=Decimal("5000.00"),
            status="PENDING"
        )

        response = self.client.patch(
            f"/api/transactions/{transaction.id}/status/",
            {
                "status": "SUCCESS"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.data["message"],
            "Transaction status updated successfully"
        )

        transaction.refresh_from_db()

        self.assertEqual(
            transaction.status,
            "SUCCESS"
        )

        self.assertIsNone(
            transaction.failure_reason
        )

    # ==================================================
    # UPDATE TRANSACTION - FAILED
    # ==================================================

    def test_update_transaction_to_failed(self):
        transaction = Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=Decimal("100001.00"),
            status="PENDING"
        )

        failure_reason = (
            "Payment declined because the amount exceeds "
            "the simulated gateway limit of ₹100,000"
        )

        response = self.client.patch(
            f"/api/transactions/{transaction.id}/status/",
            {
                "status": "FAILED",
                "failure_reason": failure_reason
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        transaction.refresh_from_db()

        self.assertEqual(
            transaction.status,
            "FAILED"
        )

        self.assertEqual(
            transaction.failure_reason,
            failure_reason
        )

    def test_failed_transaction_requires_failure_reason(self):
        transaction = Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=Decimal("100001.00"),
            status="PENDING"
        )

        response = self.client.patch(
            f"/api/transactions/{transaction.id}/status/",
            {
                "status": "FAILED"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.data["error"],
            "failure_reason is required when status is FAILED"
        )

    def test_invalid_transaction_status(self):
        transaction = Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=Decimal("5000.00"),
            status="PENDING"
        )

        response = self.client.patch(
            f"/api/transactions/{transaction.id}/status/",
            {
                "status": "PENDING"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.data["error"],
            "Status must be SUCCESS or FAILED"
        )

    def test_update_nonexistent_transaction(self):
        response = self.client.patch(
            "/api/transactions/99999/status/",
            {
                "status": "SUCCESS"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            404
        )

        self.assertEqual(
            response.data["error"],
            "Transaction not found"
        )

    def test_user_cannot_update_another_users_transaction(self):
        transaction = Transaction.objects.create(
            user=self.other_user,
            card=self.other_card,
            amount=Decimal("5000.00"),
            status="PENDING"
        )

        response = self.client.patch(
            f"/api/transactions/{transaction.id}/status/",
            {
                "status": "SUCCESS"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            404
        )

        transaction.refresh_from_db()

        self.assertEqual(
            transaction.status,
            "PENDING"
        )

    # ==================================================
    # TRANSACTION HISTORY
    # ==================================================

    def test_transaction_history(self):
        Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=Decimal("1000.00"),
            status="SUCCESS"
        )

        Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=Decimal("5000.00"),
            status="FAILED",
            failure_reason="Test failure"
        )

        response = self.client.get(
            "/api/transactions/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            len(response.data),
            2
        )

    def test_transaction_history_only_returns_current_users_transactions(self):
        Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=Decimal("1000.00"),
            status="SUCCESS"
        )

        Transaction.objects.create(
            user=self.other_user,
            card=self.other_card,
            amount=Decimal("2000.00"),
            status="SUCCESS"
        )

        response = self.client.get(
            "/api/transactions/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            len(response.data),
            1
        )

    # ==================================================
    # STATUS FILTER
    # ==================================================

    def test_transaction_history_status_filter(self):
        Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=Decimal("1000.00"),
            status="SUCCESS"
        )

        Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=Decimal("2000.00"),
            status="FAILED",
            failure_reason="Test failure"
        )

        response = self.client.get(
            "/api/transactions/?status=success"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            len(response.data),
            1
        )

        self.assertEqual(
            response.data[0]["status"],
            "SUCCESS"
        )

    # ==================================================
    # MINIMUM AMOUNT FILTER
    # ==================================================

    def test_transaction_history_min_amount_filter(self):
        Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=Decimal("1000.00"),
            status="SUCCESS"
        )

        Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=Decimal("5000.00"),
            status="SUCCESS"
        )

        response = self.client.get(
            "/api/transactions/?min_amount=3000"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            len(response.data),
            1
        )

        self.assertEqual(
            Decimal(str(response.data[0]["amount"])),
            Decimal("5000.00")
        )

    # ==================================================
    # MAXIMUM AMOUNT FILTER
    # ==================================================

    def test_transaction_history_max_amount_filter(self):
        Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=Decimal("1000.00"),
            status="SUCCESS"
        )

        Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=Decimal("5000.00"),
            status="SUCCESS"
        )

        response = self.client.get(
            "/api/transactions/?max_amount=3000"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            len(response.data),
            1
        )

        self.assertEqual(
            Decimal(str(response.data[0]["amount"])),
            Decimal("1000.00")
        )

    # ==================================================
    # DATE FILTER
    # ==================================================

    def test_transaction_history_date_filter(self):
        transaction = Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=Decimal("1000.00"),
            status="SUCCESS"
        )

        date_value = transaction.transaction_date.date().isoformat()

        response = self.client.get(
            f"/api/transactions/?date={date_value}"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            len(response.data),
            1
        )

    # ==================================================
    # AUTHENTICATION PROTECTION
    # ==================================================

    def test_transaction_history_requires_authentication(self):
        self.client.force_authenticate(
            user=None
        )

        response = self.client.get(
            "/api/transactions/"
        )

        self.assertEqual(
            response.status_code,
            401
        )

    def test_create_transaction_requires_authentication(self):
        self.client.force_authenticate(
            user=None
        )

        response = self.client.post(
            "/api/transactions/create/",
            {
                "card_id": self.card.id,
                "amount": "5000.00"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            401
        )

    def test_update_transaction_requires_authentication(self):
        transaction = Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=Decimal("5000.00"),
            status="PENDING"
        )

        self.client.force_authenticate(
            user=None
        )

        response = self.client.patch(
            f"/api/transactions/{transaction.id}/status/",
            {
                "status": "SUCCESS"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            401
        )