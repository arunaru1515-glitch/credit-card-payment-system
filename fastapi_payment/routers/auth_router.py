import os

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import httpx


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
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
# REQUEST SCHEMAS
# ==================================================

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class LogoutRequest(BaseModel):
    refresh: str


# ==================================================
# REGISTER
# ==================================================

@router.post(
    "/register",
    summary="Register User"
)
async def register_user(
    data: RegisterRequest
):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{DJANGO_BASE_URL}/api/register/",
            json=data.model_dump()
        )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.json()
        )

    return response.json()


# ==================================================
# LOGIN
# ==================================================

@router.post(
    "/login",
    summary="Login User"
)
async def login_user(
    data: LoginRequest
):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{DJANGO_BASE_URL}/api/login/",
            json=data.model_dump()
        )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.json()
        )

    return response.json()


# ==================================================
# LOGOUT
# ==================================================

@router.post(
    "/logout",
    summary="Logout User"
)
async def logout_user(
    data: LogoutRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    authorization = f"Bearer {credentials.credentials}"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{DJANGO_BASE_URL}/api/logout/",
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
# PROTECTED PROFILE
# ==================================================

@router.get(
    "/profile",
    summary="Get Protected Profile"
)
async def get_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    authorization = f"Bearer {credentials.credentials}"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DJANGO_BASE_URL}/api/profile/",
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