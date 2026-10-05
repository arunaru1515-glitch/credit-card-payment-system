import os

import httpx
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel


router = APIRouter(
    prefix="/cards",
    tags=["Cards"]
)


# ==================================================
# DJANGO BACKEND URL
# ==================================================

DJANGO_BASE_URL = os.getenv(
    "DJANGO_BASE_URL",
    "http://127.0.0.1:8000"
)


security = HTTPBearer()


# ==================================================
# REQUEST SCHEMA
# ==================================================

class CardRequest(BaseModel):
    card_number: str
    card_type: str


# ==================================================
# ADD CREDIT/DEBIT CARD
# ==================================================

@router.post(
    "/",
    summary="Add Credit/Debit Card"
)
async def add_card(
    data: CardRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    authorization = f"Bearer {credentials.credentials}"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{DJANGO_BASE_URL}/api/cards/",
            json=data.model_dump(),
            headers={
                "Authorization": authorization
            }
        )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.json()
        )

    return response.json()


# ==================================================
# VIEW SAVED CARDS
# ==================================================

@router.get(
    "/",
    summary="View Saved Cards"
)
async def get_cards(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    authorization = f"Bearer {credentials.credentials}"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DJANGO_BASE_URL}/api/cards/list/",
            headers={
                "Authorization": authorization
            }
        )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.json()
        )

    return response.json()


# ==================================================
# DELETE SAVED CARD
# ==================================================

@router.delete(
    "/{card_id}",
    summary="Delete Saved Card"
)
async def delete_card(
    card_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    authorization = f"Bearer {credentials.credentials}"

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{DJANGO_BASE_URL}/api/cards/{card_id}/",
            headers={
                "Authorization": authorization
            }
        )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.json()
        )

    return response.json()