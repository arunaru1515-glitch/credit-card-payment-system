import os
from decimal import Decimal

import httpx


# ==================================================
# DJANGO BACKEND URL
# ==================================================

DJANGO_BASE_URL = os.getenv(
    "DJANGO_BASE_URL",
    "http://127.0.0.1:8000"
)


# ==================================================
# PROCESS PAYMENT
# ==================================================

async def process_payment(
    card_id: int,
    amount: Decimal,
    authorization: str
):

    async with httpx.AsyncClient() as client:

        # ==================================================
        # STEP 1: CREATE TRANSACTION WITH PENDING STATUS
        # ==================================================
        #
        # Django performs:
        # - Card ownership validation
        # - Card-wise credit limit validation
        # - Available credit calculation
        # - Pending transaction creation
        #
        # ==================================================

        create_response = await client.post(
            f"{DJANGO_BASE_URL}/api/transactions/create/",
            json={
                "card_id": card_id,
                "amount": float(amount)
            },
            headers={
                "Authorization": authorization
            }
        )

        # --------------------------------------------------
        # HANDLE PAYMENT VALIDATION FAILURE
        # --------------------------------------------------

        if create_response.status_code >= 400:

            try:
                error_data = create_response.json()

            except ValueError:
                error_data = {
                    "error": create_response.text
                }

            return {
                "success": False,
                "error": error_data
            }

        pending_data = create_response.json()

        transaction = pending_data["transaction"]

        transaction_id = transaction["id"]

        # ==================================================
        # STEP 2: PAYMENT PROCESSING
        # ==================================================
        #
        # Credit-limit validation has already been completed
        # by Django.
        #
        # If we reached this point, the selected card has
        # sufficient available credit.
        #
        # ==================================================

        final_status = "SUCCESS"

        failure_reason = None

        # ==================================================
        # STEP 3: UPDATE TRANSACTION STATUS
        # ==================================================

        update_payload = {
            "status": final_status
        }

        if failure_reason:
            update_payload["failure_reason"] = failure_reason

        update_response = await client.patch(
            f"{DJANGO_BASE_URL}/api/transactions/"
            f"{transaction_id}/status/",
            json=update_payload,
            headers={
                "Authorization": authorization
            }
        )

        # --------------------------------------------------
        # HANDLE STATUS UPDATE FAILURE
        # --------------------------------------------------

        if update_response.status_code >= 400:

            try:
                error_data = update_response.json()

            except ValueError:
                error_data = {
                    "error": update_response.text
                }

            return {
                "success": False,
                "error": error_data,
                "transaction_id": transaction_id
            }

        updated_data = update_response.json()

        # ==================================================
        # FINAL RESPONSE
        # ==================================================

        return {
            "success": True,
            "transaction_id": transaction_id,
            "card_id": card_id,
            "amount": float(amount),
            "initial_status": "PENDING",
            "final_status": final_status,
            "failure_reason": failure_reason,
            "transaction": updated_data["transaction"]
        }