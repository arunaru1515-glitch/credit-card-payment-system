from decimal import Decimal
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch

from services.payment_service import process_payment


class PaymentServiceTests(IsolatedAsyncioTestCase):

    def create_response(self, status_code, json_data):
        response = MagicMock()
        response.status_code = status_code
        response.json.return_value = json_data
        response.text = str(json_data)
        return response

    # ==================================================
    # SUCCESSFUL PAYMENT
    # ==================================================

    @patch("services.payment_service.httpx.AsyncClient")
    async def test_process_payment_success(
        self,
        mock_client_class
    ):
        create_response = self.create_response(
            201,
            {
                "transaction": {
                    "id": 1
                }
            }
        )

        update_response = self.create_response(
            200,
            {
                "transaction": {
                    "id": 1,
                    "status": "SUCCESS"
                }
            }
        )

        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(
            return_value=mock_client
        )
        mock_client.__aexit__ = AsyncMock(
            return_value=None
        )

        mock_client.post = AsyncMock(
            return_value=create_response
        )

        mock_client.patch = AsyncMock(
            return_value=update_response
        )

        mock_client_class.return_value = mock_client

        result = await process_payment(
            card_id=1,
            amount=Decimal("5000.00"),
            authorization="Bearer test-token"
        )

        self.assertTrue(
            result["success"]
        )

        self.assertEqual(
            result["transaction_id"],
            1
        )

        self.assertEqual(
            result["card_id"],
            1
        )

        self.assertEqual(
            result["amount"],
            5000.0
        )

        self.assertEqual(
            result["initial_status"],
            "PENDING"
        )

        self.assertEqual(
            result["final_status"],
            "SUCCESS"
        )

        self.assertIsNone(
            result["failure_reason"]
        )

    # ==================================================
    # SIMULATED FAILED PAYMENT
    # ==================================================

    @patch("services.payment_service.httpx.AsyncClient")
    async def test_process_payment_failed_due_to_limit(
        self,
        mock_client_class
    ):
        create_response = self.create_response(
            201,
            {
                "transaction": {
                    "id": 2
                }
            }
        )

        update_response = self.create_response(
            200,
            {
                "transaction": {
                    "id": 2,
                    "status": "FAILED"
                }
            }
        )

        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(
            return_value=mock_client
        )
        mock_client.__aexit__ = AsyncMock(
            return_value=None
        )

        mock_client.post = AsyncMock(
            return_value=create_response
        )

        mock_client.patch = AsyncMock(
            return_value=update_response
        )

        mock_client_class.return_value = mock_client

        result = await process_payment(
            card_id=1,
            amount=Decimal("100001.00"),
            authorization="Bearer test-token"
        )

        self.assertTrue(
            result["success"]
        )

        self.assertEqual(
            result["transaction_id"],
            2
        )

        self.assertEqual(
            result["initial_status"],
            "PENDING"
        )

        self.assertEqual(
            result["final_status"],
            "FAILED"
        )

        self.assertIsNotNone(
            result["failure_reason"]
        )

        mock_client.patch.assert_awaited_once()

        update_payload = (
            mock_client.patch.await_args.kwargs["json"]
        )

        self.assertEqual(
            update_payload["status"],
            "FAILED"
        )

        self.assertIn(
            "failure_reason",
            update_payload
        )

    # ==================================================
    # DJANGO TRANSACTION CREATION FAILURE
    # ==================================================

    @patch("services.payment_service.httpx.AsyncClient")
    async def test_process_payment_transaction_creation_failure(
        self,
        mock_client_class
    ):
        create_response = self.create_response(
            400,
            {
                "error": "Card not found"
            }
        )

        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(
            return_value=mock_client
        )
        mock_client.__aexit__ = AsyncMock(
            return_value=None
        )

        mock_client.post = AsyncMock(
            return_value=create_response
        )

        mock_client.patch = AsyncMock()

        mock_client_class.return_value = mock_client

        result = await process_payment(
            card_id=999,
            amount=Decimal("5000.00"),
            authorization="Bearer test-token"
        )

        self.assertFalse(
            result["success"]
        )

        self.assertEqual(
            result["error"]["error"],
            "Card not found"
        )

        mock_client.patch.assert_not_awaited()

    # ==================================================
    # DJANGO STATUS UPDATE FAILURE
    # ==================================================

    @patch("services.payment_service.httpx.AsyncClient")
    async def test_process_payment_status_update_failure(
        self,
        mock_client_class
    ):
        create_response = self.create_response(
            201,
            {
                "transaction": {
                    "id": 3
                }
            }
        )

        update_response = self.create_response(
            400,
            {
                "error": "Transaction update failed"
            }
        )

        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(
            return_value=mock_client
        )
        mock_client.__aexit__ = AsyncMock(
            return_value=None
        )

        mock_client.post = AsyncMock(
            return_value=create_response
        )

        mock_client.patch = AsyncMock(
            return_value=update_response
        )

        mock_client_class.return_value = mock_client

        result = await process_payment(
            card_id=1,
            amount=Decimal("5000.00"),
            authorization="Bearer test-token"
        )

        self.assertFalse(
            result["success"]
        )

        self.assertEqual(
            result["transaction_id"],
            3
        )

        self.assertEqual(
            result["error"]["error"],
            "Transaction update failed"
        )