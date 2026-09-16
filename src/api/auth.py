# Файл src/api/auth.py
import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

from src.api.limiter import limiter

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY", "sfmshop-dev-secret"))
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))

router = APIRouter()
v1_router = APIRouter()
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)
users_db = {}
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(c.isdigit() for c in v):
            raise ValueError(
                "Пароль должен содержать хотя бы одну цифру"
            )
        if not any(c.isalpha() for c in v):
            raise ValueError(
                "Пароль должен содержать хотя бы одну букву"
            )
        return v


class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int


class TokenUser(BaseModel):
    id: int
    username: str


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Собрать JWT: payload + exp, подпись SECRET_KEY."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """Разобрать JWT. None — токен битый или просрочен."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except InvalidTokenError:
        return None


def _authenticate_user(username: str, password: str) -> dict | None:
    user = users_db.get(username)
    if not user or not pwd_context.verify(password, user["hashed_password"]):
        return None
    return user


def _issue_token(user: dict) -> Token:
    access_token = create_access_token(
        {"sub": user["username"], "user_id": user["id"]}
    )
    return Token(access_token=access_token, user_id=user["id"])


async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenUser:
    """Пользователь из Authorization: Bearer <jwt>."""
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Недействительный или просроченный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username = payload.get("sub")
    user = users_db.get(username) if username else None
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Пользователь токена не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenUser(id=user["id"], username=user["username"])


@router.post("/register")
async def register(user: UserCreate):
    if user.username in users_db:
        raise HTTPException(
            status_code=400,
            detail="Пользователь уже существует",
        )
    user_id = len(users_db) + 1
    users_db[user.username] = {
        "id": user_id,
        "username": user.username,
        "hashed_password": pwd_context.hash(user.password),
    }
    return {"id": user_id, "username": user.username}


@router.post("/login")
@limiter.limit(os.getenv("RATE_LIMIT_LOGIN", "5/minute"))
async def login(request: Request, data: LoginRequest):
    user = _authenticate_user(data.username, data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Неверные учетные данные",
        )
    return _issue_token(user)


@v1_router.post("/login", response_model=Token)
@limiter.limit(os.getenv("RATE_LIMIT_LOGIN", "5/minute"))
async def login_v1(request: Request, data: LoginRequest):
    """Выдать JWT для заголовка Authorization: Bearer <token>."""
    user = _authenticate_user(data.username, data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Неверные учетные данные",
        )
    return _issue_token(user)
