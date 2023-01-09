import asyncio
from datetime import datetime
from typing import List

from models.database import session
from models.posts import posts_table, like_table
from models.users import users_table
from schemas import posts as post_schema
from sqlalchemy import desc, func, select

from schemas.posts import PostDetailsModel


async def create_post(post: post_schema.PostModel, user) -> PostDetailsModel:
    """
    Создание записи поста в БД
    :param post: Данные для добавления поста
    :param user: пользователь добавивший пост
    :return:
    """
    query = (
        posts_table.insert()
        .values(
            title=post.title,
            content=post.content,
            created_at=datetime.now(),
            user_id=user.id,
        )
        .returning(
            posts_table.c.id,
            posts_table.c.title,
            posts_table.c.content,
            posts_table.c.created_at,
        )
    )
    async with session.begin() as ses:
        post = await ses.execute(query)
        post = post.context.compiled_parameters[0]
        post["user_name"] = user.name
    return post


async def get_post(post_id: int) -> PostDetailsModel:
    """
    Полечение одного поста по id
    :param post_id: id поста
    :return: найденный пост
    """
    query = (
        select(
            [
                posts_table.c.id,
                posts_table.c.created_at,
                posts_table.c.title,
                posts_table.c.content,
                posts_table.c.user_id,
                users_table.c.name.label("user_name"),
            ]
        )
        .select_from(posts_table.join(users_table))
        .where(posts_table.c.id == post_id)
    )
    async with session.begin() as ses:
        post = await ses.execute(query)
        post = post.first()
    return post


async def get_posts(page: int) -> List[PostDetailsModel]:
    """
    Получение 10ти постов согласно полученной странице
    :param page: int номер десятка постов
    :return: List[PostDetailsModel] список постов
    """
    max_per_page = 10
    offset1 = (page - 1) * max_per_page
    query = (
        select(
            [
                posts_table.c.id,
                posts_table.c.created_at,
                posts_table.c.title,
                posts_table.c.content,
                posts_table.c.user_id,
                users_table.c.name.label("user_name"),
            ]
        )
        .select_from(posts_table.join(users_table))
        .order_by(desc(posts_table.c.created_at))
        .limit(max_per_page)
        .offset(offset1)
    )
    async with session.begin() as ses:
        post = await ses.execute(query)
        post = post.all()
        return post


async def get_posts_count() -> int:
    """
    Возвращает колличество постов в БД
    :return: int колличество имеющихся постов в БД
    """
    query = select([func.count()]).select_from(posts_table)
    async with session.begin() as ses:
        result = await ses.execute(query)
        result = result.first()[0]
        return result


async def update_post(post_id: int, post: post_schema.PostModel):
    """
    Изменение значений title и content поста
    :param post_id: int Номер поста
    :param post: Новые значения для поста
    :return:
    """
    query = (
        posts_table.update()
        .where(posts_table.c.id == post_id)
        .values(title=post.title, content=post.content)
    )
    async with session.begin() as ses:
        result = await ses.execute(query)
        return result

async def check_user_like(post_id: int, user_id: int) -> bool:
    """
    Проверяет лайкал ли пользователь пост. Если да, возвращае True, иниче False
    :param post_id: id номер поста
    :param user_id: id номер пользователя
    :return: bool
    """
    query_check = (
        select(
            [
                like_table.c.id
            ]
        )
        .select_from(like_table)
        .where(like_table.c.post_id == post_id, like_table.c.user_id == user_id)
    )
    async with session.begin() as ses:
        check_like = await ses.execute(query_check)
        if check_like.first():
            return True
        return False

async def like_post(post_id: int, user_id: int):
    """
    Добавление лайка поста
    :param post_id: id номер поста
    :param user_id: id номер пользователя
    :return: bool
    """
    query_insert = (
        like_table.insert()
        .values(
            post_id=post_id,
            user_id=user_id,
            like=True
        ))
    if await check_user_like(post_id, user_id):
        return False
    async with session.begin() as ses:
        await ses.execute(query_insert)
        return True

async def dislike_post(post_id: int, user_id: int):
    """
    Добавление дислайка поста
    :param post_id: id номер поста
    :param user_id: id номер пользователя
    :return: bool
    """
    query_insert = (
        like_table.insert()
        .values(
            post_id=post_id,
            user_id=user_id,
            like=False
        ))
    if await check_user_like(post_id, user_id):
        return False
    async with session.begin() as ses:
        await ses.execute(query_insert)
        return True
