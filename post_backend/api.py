from ninja import NinjaAPI
from django.middleware.csrf import get_token
from posts.api import router as post_router
from user.api import router as user_router

api = NinjaAPI(urls_namespace='main_api')


@api.get("/set-csrf-token")
def get_csrf_token(request):
    return {"csrf_token": get_token(request)}


api.add_router("/posts/", post_router)
api.add_router("/auth/", user_router)
