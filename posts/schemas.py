from ninja import Schema
from typing import Optional, List
from datetime import datetime
from user.schemas import UserSchema


class CommentSchema(Schema):
    id: int
    post: int
    author: int
    content: str


class PostSchema(Schema):
    id: int
    title: str
    content: str
    author: UserSchema
    auto_reply: bool
    reply_delay: int
    pub_date: datetime


class PostGetSchema(Schema):
    id: int
    title: str
    content: str
    author: UserSchema
    # auto_reply: bool
    # reply_delay: int
    pub_date: datetime
    comments: List[CommentSchema]


class PostSettingsSchema(Schema):
    auto_reply: bool
    reply_delay: int


class PostCreateSchema(Schema):
    title: str
    content: str
    author: UserSchema
    auto_reply: Optional[bool] = False
    reply_delay: Optional[int] = 0


class CommentCreateSchema(Schema):
    post: int
    author: UserSchema
    content: str


class DailyCommentAnalytics(Schema):
    date: datetime
    total_comments: int
    blocked_comments: int


class CommentsDailyBreakdownResponse(Schema):
    analytics: List[DailyCommentAnalytics]


class ReplySchema(Schema):
    id: int
    comment_id: int
    content: str
    created_at: datetime
