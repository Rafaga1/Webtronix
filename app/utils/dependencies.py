from utils import users as users_utils
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from schemas.users import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth")


async def get_current_user(user: User):
    """
    Идентификация и проверка на аутентификацию пользователя
    :param user: User
    :return: bool
    """
    user = await users_utils.get_user_by_token(user.token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return user
