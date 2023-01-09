from schemas.posts import PostDetailsModel, PostModel
from schemas.users import User, LikeModel
from utils import posts as post_utils
from utils.dependencies import get_current_user
from fastapi import APIRouter, HTTPException, status

from utils.posts import like_post, dislike_post

router = APIRouter()


@router.post("/posts", response_model=PostDetailsModel, status_code=201)
async def create_post(post: PostModel, current_user: User) -> PostDetailsModel:
    """
    СОздание поста.
    :param post: PostModel
    :param current_user: User
    :return: PostDetailsModel
    """
    await get_current_user(user=current_user)
    post = await post_utils.create_post(post, current_user)
    return post


@router.get("/posts")
async def get_posts(page: int = 1):
    """
    Возвращает 10 найденных в БД постов согласно номеру офсета.
    :param page: int
    :return: Всего постов, посты заданнойстраницы
    """
    total_cout = await post_utils.get_posts_count()
    posts = await post_utils.get_posts(page)
    return {"total_count": total_cout, "results": posts}


@router.get("/posts/{post_id}", response_model=PostDetailsModel)
async def get_post(post_id: int) -> PostDetailsModel:
    """
    Получение одного поста
    :param post_id: int номер поста
    :return: PostModel
    """
    return await post_utils.get_post(post_id)


@router.post("/posts_edit/", response_model=PostDetailsModel)
async def update_post(
    post_data: PostModel, current_user: User
):
    user = await get_current_user(current_user)
    post = await post_utils.get_post(post_data.id)

    if post.user_id != user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to modify this post",
        )

    await post_utils.update_post(post_id=post_data.id, post=post_data)
    return await post_utils.get_post(post_data.id)

@router.post("/posts_like/", response_model=PostDetailsModel)
async def update_post(
    like: LikeModel, current_user: User
) -> PostDetailsModel:
    """
    Добавление лайка или дислайка посу указанным пользоателем
    :param post_id: id поста
    :param like: лайк или дислайк
    :param current_user: пользователь
    :return: пост
    """
    user = await get_current_user(current_user)
    post = await post_utils.get_post(like.post)

    if post.user_id == user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не можете лайкать свой пост",
        )
    if like.like:
        await like_post(post.id, user.id)
        return await post_utils.get_post(like.post)
    await dislike_post(post.id, user.id)
    return await post_utils.get_post(like.post)
