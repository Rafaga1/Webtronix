from typing import Optional
from pydantic import BaseModel, EmailStr
from pydantic.validators import datetime


class UserCreate(BaseModel):
    """ Проверяет sign-up запрос """
    email: EmailStr
    name: str
    password: str


class UserBase(BaseModel):
    """ Формирует тело ответа с деталями пользователя """
    id: int
    email: EmailStr
    name: str


class TokenBase(BaseModel):
    token: str
    expires: datetime
    token_type: Optional[str] = "bearer"


class User(UserBase):
    """ Формирует тело ответа с деталями пользователя и токеном """
    token: TokenBase = {}


class LogOut(BaseModel):
    user_id: int
    token: str

class LikeModel(BaseModel):
    post: int
    like: bool
