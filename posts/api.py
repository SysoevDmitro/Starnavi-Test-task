import time
from datetime import datetime
from typing import List
from better_profanity import profanity
from django.db.models import Count, Q
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import Router
from user.api import AuthBearer
from .ai import generate_reply
from .models import Post, Comment, Reply
from .schemas import (PostSchema, PostCreateSchema, PostGetSchema,
                      CommentCreateSchema, CommentSchema, DailyCommentAnalytics,
                      CommentsDailyBreakdownResponse, PostSettingsSchema,
                      ReplySchema)

router = Router()


def send_auto_reply(comment_id, post_content, delay):
    time.sleep(delay)  # Задержка перед отправкой ответа
    comment = Comment.objects.get(id=comment_id)  # Получаем комментарий

    reply_content = generate_reply(post_content, comment.content)  # Генерируем ответ с помощью OpenAI
    Reply.objects.create(
        content=reply_content,
        comment_id=comment.id,
        created_at=timezone.now()  # Добавьте, если у вас есть поле для даты создания
    )


# Функция для триггера автоматического ответа
def trigger_auto_reply_async(comment, post):
    if post.auto_reply:
        send_auto_reply(comment.id, post.content, post.reply_delay)


@router.get("/", response=List[PostSchema])
def list_posts(request):
    queryset = Post.objects.select_related("author")
    return list(queryset)


@router.get("/{post_id}", response=PostGetSchema)
def get_post(request, post_id: int):
    post = Post.objects.prefetch_related("comment_set").get(id=post_id)
    comments = [
        CommentSchema(
            id=comment.id,
            content=comment.content,
            author=comment.author.id,
            post=comment.post.id,
            created_at=comment.created_at
        )
        for comment in post.comment_set.all()
    ]

    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "author": {"id": post.author.id, "email": post.author.email},
        "pub_date": post.pub_date,
        "comments": comments
    }


@router.post("/", response=PostCreateSchema, auth=AuthBearer())
def create_post(request, data: PostCreateSchema):
    user = request.auth
    if profanity.contains_profanity(data.title) or profanity.contains_profanity(data.content):
        return HttpResponseBadRequest("Post contains profanity!")
    post = Post.objects.create(author=user, **data.dict(exclude={"author"}))
    return post


@router.put("/{post_id}", response=PostSchema)
def update_post(request, post_id: int, data: PostSchema):
    post = get_object_or_404(Post, id=post_id)
    if profanity.contains_profanity(data.title) or profanity.contains_profanity(data.content):
        return HttpResponseBadRequest("Post contains profanity!")
    for attr, value in data.dict(exclude={"author"}).items():
        setattr(post, attr, value)
    post.save()
    return post


@router.patch("/posts/{post_id}/settings")
def update_post_settings(request, post_id: int, data: PostSettingsSchema):
    post = Post.objects.get(id=post_id)
    post.auto_reply = data.auto_reply
    post.reply_delay = data.reply_delay
    post.save()
    return {
        "auto_reply": post.auto_reply,
        "reply_delay": post.reply_delay
    }


@router.delete("/{post_id}")
def delete_post(request, post_id: int):
    post = get_object_or_404(Post, id=post_id)
    post.delete()
    return {"success": True}


@router.post("/comment/{post_id}", response=CommentCreateSchema, auth=AuthBearer())
def create_comment(request, post_id: int, data: CommentCreateSchema):
    user = request.auth
    post = get_object_or_404(Post, id=post_id)
    if profanity.contains_profanity(data.content):
        return HttpResponseBadRequest("Comment contains profanity!")
    comment = Comment.objects.create(author=user, post=post, **data.dict(exclude={"author", "post"}))
    if post.auto_reply:
        trigger_auto_reply_async(comment, post)
    return {
        "content": comment.content,
        "post": comment.post.id,
        "author": {"id": user.id, "email": user.email}
    }


@router.get("/comments/{comment_id}/replies", response=List[ReplySchema])
def get_comment_replies(request, comment_id: int):
    try:
        comment = get_object_or_404(Comment, id=comment_id)
        replies = Reply.objects.filter(comment_id=comment_id)
        return replies
    except Comment.DoesNotExist:
        return {"detail": "Comment not found"}, 404


@router.delete("/comment/{post_id}/{comment_id}")
def delete_comment(request, comment_id: int, post_id: int):
    comment = get_object_or_404(Comment, id=comment_id)
    comment.delete()
    return {"success": True}


@router.put("/comment/{post_id}/{comment_id}", response=CommentSchema, auth=AuthBearer())
def update_comment(request, comment_id: int, post_id: int, data: CommentSchema):
    comment = get_object_or_404(Comment, id=comment_id)
    if profanity.contains_profanity(data.content):
        return HttpResponseBadRequest("Comment contains profanity!")
    for attr, value in data.dict(exclude=("author", "post")).items():
        setattr(comment, attr, value)

    comment.save()
    return CommentSchema(
        id=comment.id,
        post=comment.post.id,
        author=comment.author.id,
        content=comment.content,
        created_at=comment.created_at,
    )


@router.get("/{post_id}/comments-daily-breakdown", response=CommentsDailyBreakdownResponse)
def comments_daily_breakdown(request, date_from: str, date_to: str, post_id: int):
    try:
        start_date = datetime.strptime(date_from, "%Y-%m-%d").date()
        end_date = datetime.strptime(date_to, "%Y-%m-%d").date()

        if start_date > end_date:
            return {"detail": "date_from must be earlier than date_to."}, 400
    except ValueError:
        return {"detail": "Invalid date format. Use YYYY-MM-DD."}, 400

        # Агрегуємо дані по днях
    analytics = (
        Comment.objects.filter(post=post_id, created_at__range=(start_date, end_date))
        .values("created_at__date")
        .annotate(
            total_comments=Count("id"),
            blocked_comments=Count("id", filter=Q(is_blocked=True)),
        )
        .order_by("created_at__date")
    )

    # Формуємо відповідь
    result = [
        DailyCommentAnalytics(
            date=entry["created_at__date"],
            total_comments=entry["total_comments"],
            blocked_comments=entry["blocked_comments"]
        )
        for entry in analytics
    ]

    return {"analytics": result}
