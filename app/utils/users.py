import hashlib
import random
import string
import uuid
from datetime import datetime, timedelta
from sqlalchemy import select

from models.database import session
from models.users import tokens_table, users_table
from schemas import users as user_schema
from schemas.users import TokenBase, User, LogOut


def get_random_string(length=12):
    """ Генерирует случайную строку, использующуюся как соль """
    return "".join(random.choice(string.ascii_letters) for _ in range(length))


def hash_password(password: str, salt: str = None):
    """ Хеширует пароль с солью """
    if salt is None:
        salt = get_random_string()
    enc = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return enc.hex()


def validate_password(password: str, hashed_password: str):
    """ Проверяет, что хеш пароля совпадает с хешем из БД """
    salt, hashed = hashed_password.split("$")
    return hash_password(password, salt) == hashed


async def get_user_by_email(email: str):
    """ Возвращает информацию о пользователе """
    query = users_table.select().where(users_table.c.email == email)
    async with session.begin() as ses:
        result = await ses.execute(query)
        result = result.first()
    return result


async def get_user_by_token(user: User):
    """ Возвращает информацию о владельце указанного токена """
    async with session.begin() as ses:
        result = await ses.execute(select(tokens_table, users_table).
                                   join(users_table, users_table.c.id == tokens_table.c.user_id).
                                   filter(tokens_table.c.token == user.token,
                                          tokens_table.c.expires > datetime.now()))
        result = result.first()
    return result


async def create_user_token(user_id: int):
    """ Создает токен для пользователя с указанным user_id """
    query = (
        tokens_table.insert()
        .values(expires=datetime.now() + timedelta(weeks=2), user_id=user_id, token=str(uuid.uuid4()))
        .returning(tokens_table.c.token, tokens_table.c.expires)
    )

    async with session.begin() as ses:
        result = await ses.execute(query)
        return_result = result.first()
    return return_result


async def delete_user_token(user: LogOut):
    """ Удаляет токен пользователя с указанным user_id и токеном"""
    query = (
        tokens_table.delete()
        .where(tokens_table.c.user_id == user.user_id, tokens_table.c.token == user.token)
    )

    async with session.begin() as ses:
        await ses.execute(query)


async def create_user(user: user_schema.UserCreate):
    """ Создает нового пользователя в БД """
    salt = get_random_string()
    hashed_password = hash_password(user.password, salt)
    query = users_table.insert().values(
        email=user.email, name=user.name, hashed_password=f"{salt}${hashed_password}"
    )

    async with session.begin() as ses:
        ses.autoflush = False
        created_user = await ses.execute(query)
        user_id = created_user.inserted_primary_key[0]
    token, expires = await create_user_token(user_id)
    token_base = TokenBase(token=token, expires=expires)
    user_response = User(id=user_id, email=user.email, name=user.name, token=token_base)
    return user_response
