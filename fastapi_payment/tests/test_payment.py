from decimal import Decimal
from unittest import TestCase
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


class PaymentTests(TestCase):
    """
    Tests for FastAPI Payment API.

    Covers:
    - Successful payment
    - Failed payment
    - Authentication
    - Request validation
    """

    def setUp(self):
        self.headers = {
            "Authorization": "Bearer test-access-token"
        }

        self.success_result = {
            "success": True,
            "transaction_id": 101,
            "card_id": 1,
            "amount": 5000.0,
            "initial_status": "PENDING",
            "final_status": "SUCCESS",
            "failure_reason": None,
            "transaction": {
                "id": 101,
                "amount": "5000.00",
                "status": "SUCCESS"
            }
        }

        self.failed_result = {
            "success": True,
            "transaction_id": 102,
            "card_id": 1,
            "amount": 100001.0,
            "initial_status": "PENDING",
            "final_status": "FAILED",
            "failure_reason": (
                "Payment declined because the amount exceeds "
                "the simulated gateway limit of ₹100,000"
            ),
            "transaction": {
                "id": 102,
                "amount": "100001.00",
                "status": "FAILED",
                "failure_reason": (
                    "Payment declined because the amount exceeds "
                    "the simulated gateway limit of ₹100,000"
                )
            }
        }

    # ==================================================
    # SUCCESSFUL PAYMENT
    # ==================================================

    @patch(
        "routers.payment_router.process_payment",
        new_callable=AsyncMock
    )
    def test_successful_payment(self, mock_process_payment):
        mock_process_payment.return_value = self.success_result

        response = client.post(
            "/payments/",
            json={
                "card_id": 1,
                "amount": "5000.00"
            },
            headers=self.headers
        )

        self.assertEqual(
            response.status_code,
            200
        )

        data = response.json()

        self.assertEqual(
            data["message"],
            "Payment processed successfully"
        )

        self.assertTrue(
            data["payment"]["success"]
        )

        self.assertEqual(
            data["payment"]["initial_status"],
            "PENDING"
        )

        self.assertEqual(
            data["payment"]["final_status"],
            "SUCCESS"
        )

        mock_process_payment.assert_awaited_once()

        called_kwargs = (
            mock_process_payment.await_args.kwargs
        )

        self.assertEqual(
            called_kwargs["card_id"],
            1
        )

        self.assertEqual(
            called_kwargs["amount"],
            Decimal("5000.00")
        )

        self.assertEqual(
            called_kwargs["authorization"],
            "Bearer test-access-token"
        )

    # ==================================================
    # FAILED PAYMENT
    # ==================================================

    @patch(
        "routers.payment_router.process_payment",
        new_callable=AsyncMock
    )
    def test_failed_payment(self, mock_process_payment):
        mock_process_payment.return_value = {
            "success": False,
            "error": {
                "message": (
                    "Payment declined because the amount "
                    "exceeds the simulated gateway limit "
                    "of ₹100,000"
                )
            }
        }

        response = client.post(
            "/payments/",
            json={
                "card_id": 1,
                "amount": "100001.00"
            },
            headers=self.headers
        )

        self.assertEqual(
            response.status_code,
            400
        )

        data = response.json()

        self.assertIn(
            "detail",
            data
        )

        self.assertIn(
            "message",
            data["detail"]
        )

        mock_process_payment.assert_awaited_once()

    # ==================================================
    # PAYMENT WITHOUT AUTHENTICATION
    # ==================================================

    def test_payment_requires_authentication(self):
        response = client.post(
            "/payments/",
            json={
                "card_id": 1,
                "amount": "5000.00"
            }
        )

        self.assertEqual(
            response.status_code,
            401
        )

    # ==================================================
    # INVALID CARD ID
    # ==================================================

    @patch(
        "routers.payment_router.process_payment",
        new_callable=AsyncMock
    )
    def test_invalid_card_id_type(self, mock_process_payment):
        response = client.post(
            "/payments/",
            json={
                "card_id": "invalid",
                "amount": "5000.00"
            },
            headers=self.headers
        )

        self.assertEqual(
            response.status_code,
            422
        )

        mock_process_payment.assert_not_awaited()

    # ==================================================
    # ZERO AMOUNT
    # ==================================================

    @patch(
        "routers.payment_router.process_payment",
        new_callable=AsyncMock
    )
    def test_zero_amount_not_allowed(self, mock_process_payment):
        response = client.post(
            "/payments/",
            json={
                "card_id": 1,
                "amount": "0"
            },
            headers=self.headers
        )

        self.assertEqual(
            response.status_code,
            422
        )

        mock_process_payment.assert_not_awaited()

    # ==================================================
    # NEGATIVE AMOUNT
    # ==================================================

    @patch(
        "routers.payment_router.process_payment",
        new_callable=AsyncMock
    )
    def test_negative_amount_not_allowed(self, mock_process_payment):
        response = client.post(
            "/payments/",
            json={
                "card_id": 1,
                "amount": "-100"
            },
            headers=self.headers
        )

        self.assertEqual(
            response.status_code,
            422
        )

        mock_process_payment.assert_not_awaited()

    # ==================================================
    # MISSING CARD ID
    # ==================================================

    @patch(
        "routers.payment_router.process_payment",
        new_callable=AsyncMock
    )
    def test_missing_card_id(self, mock_process_payment):
        response = client.post(
            "/payments/",
            json={
                "amount": "5000.00"
            },
            headers=self.headers
        )

        self.assertEqual(
            response.status_code,
            422
        )

        mock_process_payment.assert_not_awaited()

    # ==================================================
    # MISSING AMOUNT
    # ==================================================

    @patch(
        "routers.payment_router.process_payment",
        new_callable=AsyncMock
    )
    def test_missing_amount(self, mock_process_payment):
        response = client.post(
            "/payments/",
            json={
                "card_id": 1
            },
            headers=self.headers
        )

        self.assertEqual(
            response.status_code,
            422
        )

        mock_process_payment.assert_not_awaited()


if __name__ == "__main__":
    import unittest

    unittest.main()