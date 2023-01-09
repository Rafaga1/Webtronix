from fastapi import APIRouter, HTTPException

from schemas import users
from utils import users as users_utils

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from utils.dependencies import get_current_user
from schemas.users import LogOut
from utils.users import delete_user_token

router = APIRouter()


@router.post("/sign-up", response_model=users.User)
async def create_user(user: users.UserCreate):
    db_user = await users_utils.get_user_by_email(email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    created_user = await users_utils.create_user(user=user)
    return created_user

@router.post("/auth", response_model=users.TokenBase)
async def auth(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await users_utils.get_user_by_email(email=form_data.username)

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if not users_utils.validate_password(
        password=form_data.password, hashed_password=user["hashed_password"]
    ):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    return await users_utils.create_user_token(user_id=user["id"])

@router.post("/users/me", response_model=users.UserBase)
async def read_users_me(current_user: users.User = Depends(get_current_user)):
    return current_user

@router.post("/logout")
async def user_logout(user: LogOut):
    await delete_user_token(user)
    return {"message": "Вы вышли из системмы"}
