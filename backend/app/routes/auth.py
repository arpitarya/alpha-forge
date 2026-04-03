"""Authentication endpoints — register, login, token refresh."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

router = APIRouter()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest):
    # TODO: persist user to DB, hash password, return token
    raise HTTPException(status_code=501, detail="Registration not yet implemented")


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    # TODO: verify credentials, return token
    raise HTTPException(status_code=501, detail="Login not yet implemented")
