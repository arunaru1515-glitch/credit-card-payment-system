import os
import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


security = HTTPBearer()


DJANGO_BASE_URL = os.getenv(
    "DJANGO_BASE_URL",
    "http://127.0.0.1:8000"
)

DJANGO_DASHBOARD_URL = (
    f"{DJANGO_BASE_URL}/api/transactions/dashboard/summary/"
)


@router.get(
    "/summary",
    summary="Get Dashboard Summary"
)
async def get_dashboard_summary(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    authorization = f"Bearer {credentials.credentials}"

    headers = {
        "Authorization": authorization
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                DJANGO_DASHBOARD_URL,
                headers=headers
            )

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Django service is unavailable"
        )

    if response.status_code != 200:
        try:
            detail = response.json()
        except Exception:
            detail = "Failed to fetch dashboard summary"

        raise HTTPException(
            status_code=response.status_code,
            detail=detail
        )

    return response.json()