# Файл src/api/auth.py
from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel, Field, field_validator


router = APIRouter()
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    )
users_db = {}


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


@router.post("/register")
def register(user: UserCreate):
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
def login(data: LoginRequest):
    user = users_db.get(data.username)
    if not user or not pwd_context.verify(
        data.password, user["hashed_password"]
        ):
        raise HTTPException(
            status_code=401,
            detail="Неверные учетные данные",
            )
    return {
        "message": "Авторизация успешна",
        "user_id": user["id"],
        }