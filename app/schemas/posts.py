from typing import Optional
from pydantic import BaseModel
from pydantic.validators import datetime


class PostModel(BaseModel):
    id: Optional[int]
    title: str
    content: str
    created_at: Optional[datetime]
    user_id: Optional[int]


class PostDetailsModel(BaseModel):
    id: Optional[int]
    title: str
    content: str
    created_at: Optional[datetime]
    user_id: Optional[int]
    user_name: str
