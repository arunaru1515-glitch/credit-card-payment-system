from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import Card
from .models import Transaction, FraudLog, APIMetricLog


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


class NewFeaturesAndAnalyticsTests(TestCase):
    """
    Comprehensive tests for:
    - Rule-based Fraud Detection logic
    - Fraud log management & staff review
    - Card Usage Analytics (Monthly, Categories, Credit Utilization)
    - Advanced Search, sorting, and server-side pagination
    - System health monitoring API
    - CSV and PDF export endpoints
    """

    def setUp(self):
        self.client = APIClient()

        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="adminuser@example.com",
            password="Admin@12345",
            role=User.ROLE_ADMIN,
        )

        self.support_user = User.objects.create_user(
            username="supportuser",
            email="supportuser@example.com",
            password="Support@12345",
            role=User.ROLE_SUPPORT,
        )

        self.read_only_user = User.objects.create_user(
            username="readonlyuser",
            email="readonly@example.com",
            password="ReadOnly@12345",
            role=User.ROLE_READ_ONLY,
        )

        self.customer = User.objects.create_user(
            username="testcustomer",
            email="customer@example.com",
            password="Customer@12345",
            role=User.ROLE_CUSTOMER,
        )

        self.card = Card.objects.create(
            user=self.customer,
            card_type="credit",
            masked_card_number="**** **** **** 8888",
            last_four_digits="8888",
            credit_limit=Decimal("100000.00"),
        )

    def test_fraud_detection_high_value_burst(self):
        self.client.force_authenticate(user=self.customer)

        # 1st high-value transaction
        Transaction.objects.create(
            user=self.customer,
            card=self.card,
            amount=Decimal("15000.00"),
            status="SUCCESS",
        )

        # 2nd high-value transaction within 10 minutes -> should trigger fraud rule
        response = self.client.post(
            "/api/transactions/create/",
            {
                "card_id": self.card.id,
                "amount": "12000.00",
                "category": "Shopping",
            },
            format="json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["transaction"]["fraud_status"], "FLAGGED")

        fraud_log = FraudLog.objects.filter(user=self.customer).first()
        self.assertIsNotNone(fraud_log)
        self.assertEqual(fraud_log.risk_level, "HIGH")
        self.assertIn("Multiple high-value transactions", fraud_log.rule_triggered)

    def test_fraud_detection_rapid_locations(self):
        self.client.force_authenticate(user=self.customer)

        # Initial transaction in Delhi
        t1 = Transaction.objects.create(
            user=self.customer,
            card=self.card,
            amount=Decimal("1000.00"),
            status="SUCCESS",
            location="Delhi",
        )

        # Rapid subsequent transaction claiming location New York
        response = self.client.post(
            "/api/transactions/create/",
            {
                "card_id": self.card.id,
                "amount": "2000.00",
                "location": "New York",
            },
            format="json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["transaction"]["fraud_status"], "FLAGGED")

        fraud_log = FraudLog.objects.filter(location="New York").first()
        self.assertIsNotNone(fraud_log)
        self.assertIn("different locations", fraud_log.rule_triggered)

    def test_fraud_log_staff_review(self):
        log = FraudLog.objects.create(
            user=self.customer,
            amount=Decimal("12000.00"),
            risk_level="HIGH",
            rule_triggered="Multiple high-value transactions",
            status="UNDER_REVIEW",
        )

        # Customer forbidden
        self.client.force_authenticate(user=self.customer)
        res_cust = self.client.get("/api/transactions/fraud-logs/")
        self.assertEqual(res_cust.status_code, 403)

        # Support user allowed
        self.client.force_authenticate(user=self.support_user)
        res_supp = self.client.get("/api/transactions/fraud-logs/")
        self.assertEqual(res_supp.status_code, 200)

        # Review action
        res_review = self.client.patch(
            f"/api/transactions/fraud-logs/{log.id}/review/",
            {"status": "RESOLVED"},
            format="json"
        )
        self.assertEqual(res_review.status_code, 200)
        log.refresh_from_db()
        self.assertEqual(log.status, "RESOLVED")
        self.assertEqual(log.reviewed_by, self.support_user)

    def test_card_usage_analytics_api(self):
        self.client.force_authenticate(user=self.customer)

        Transaction.objects.create(
            user=self.customer,
            card=self.card,
            amount=Decimal("5000.00"),
            category="Groceries",
            status="SUCCESS",
        )
        Transaction.objects.create(
            user=self.customer,
            card=self.card,
            amount=Decimal("15000.00"),
            category="Dining",
            status="SUCCESS",
        )

        response = self.client.get("/api/transactions/analytics/card-usage/")
        self.assertEqual(response.status_code, 200)

        data = response.data
        self.assertIn("monthly_spending", data)
        self.assertIn("category_expenses", data)
        self.assertIn("credit_utilization", data)

        # Verify utilization calculation (20000 spent out of 100000 limit = 20%)
        self.assertEqual(data["credit_utilization"]["total_credit_spent"], 20000.0)
        self.assertEqual(data["credit_utilization"]["utilization_percentage"], 20.0)

    def test_advanced_search_and_pagination(self):
        self.client.force_authenticate(user=self.customer)

        t1 = Transaction.objects.create(
            user=self.customer,
            card=self.card,
            amount=Decimal("1000.00"),
            category="Groceries",
            status="SUCCESS",
        )
        t2 = Transaction.objects.create(
            user=self.customer,
            card=self.card,
            amount=Decimal("4000.00"),
            category="Dining",
            status="SUCCESS",
        )
        t3 = Transaction.objects.create(
            user=self.customer,
            card=self.card,
            amount=Decimal("9000.00"),
            category="Travel",
            status="FAILED",
            failure_reason="Declined",
        )

        # Filter by Category
        res_cat = self.client.get("/api/transactions/?category=Groceries")
        self.assertEqual(res_cat.status_code, 200)
        self.assertEqual(len(res_cat.data), 1)

        # Server-side pagination
        res_page = self.client.get("/api/transactions/?page=1&page_size=2&sort_by=amount_desc")
        self.assertEqual(res_page.status_code, 200)
        self.assertEqual(res_page.data["count"], 3)
        self.assertEqual(res_page.data["total_pages"], 2)
        self.assertEqual(len(res_page.data["results"]), 2)
        # Highest amount first: 9000
        self.assertEqual(Decimal(str(res_page.data["results"][0]["amount"])), Decimal("9000.00"))

    def test_system_health_monitoring_api(self):
        # Customer forbidden
        self.client.force_authenticate(user=self.customer)
        res_cust = self.client.get("/api/system/health/")
        self.assertEqual(res_cust.status_code, 403)

        # Admin allowed
        self.client.force_authenticate(user=self.admin_user)
        res_admin = self.client.get("/api/system/health/")
        self.assertEqual(res_admin.status_code, 200)
        self.assertEqual(res_admin.data["status"], "HEALTHY")
        self.assertIn("performance", res_admin.data)
        self.assertIn("database", res_admin.data)

    def test_analytics_and_transaction_exports(self):
        self.client.force_authenticate(user=self.customer)

        # CSV Export for Analytics
        res_csv = self.client.get("/api/transactions/analytics/export/csv/")
        self.assertEqual(res_csv.status_code, 200)
        self.assertEqual(res_csv["Content-Type"], "text/csv")

        # PDF Export for Analytics
        res_pdf = self.client.get("/api/transactions/analytics/export/pdf/")
        self.assertEqual(res_pdf.status_code, 200)
        self.assertEqual(res_pdf["Content-Type"], "application/pdf")

        # CSV Export for Filtered Transactions
        res_tx_csv = self.client.get("/api/transactions/export/csv/")
        self.assertEqual(res_tx_csv.status_code, 200)
        self.assertEqual(res_tx_csv["Content-Type"], "text/csv")