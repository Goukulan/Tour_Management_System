# app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, Response, Request, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.config import settings
from app.schemas.users import (
    RegisterRequest,
    LoginRequest,
    UserOut,
    TokenResponse,
    LoginResponse,
)
from app.services import auth_service
from app.utils.dependencies import get_current_user
from app.models.users import User
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.REFRESH_TOKEN_COOKIE_SECURE,
        samesite=settings.REFRESH_TOKEN_COOKIE_SAMESITE,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/api/v1/auth",
    )


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    user = auth_service.register_user(db, payload)
    return user


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(db, payload)
    access_token, refresh_token = auth_service.issue_tokens(user)

    _set_refresh_cookie(response, refresh_token)

    return LoginResponse(
        user=user,
        tokens=TokenResponse(access_token=access_token),
    )

@router.post("/token", response_model=TokenResponse)
def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    payload = LoginRequest(
        email=form_data.username,
        password=form_data.password,
    )

    user = auth_service.authenticate_user(db, payload)

    access_token, refresh_token = auth_service.issue_tokens(user)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get(settings.REFRESH_TOKEN_COOKIE_NAME)
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
        )

    access_token, new_refresh_token = auth_service.rotate_refresh_token(db, refresh_token)
    _set_refresh_cookie(response, new_refresh_token)

    return TokenResponse(access_token=access_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    response.delete_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        path="/api/v1/auth",
    )
    return None


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user