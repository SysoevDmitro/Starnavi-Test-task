from django.contrib.auth.models import User
from ninja import Router
from ninja.security import HttpBearer
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from .schemas import UserCreateSchema, UserLoginSchema

router = Router()


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        jwt_auth = JWTAuthentication()
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'
        user, auth_token = jwt_auth.authenticate(request)  # Теперь передаем request
        if user is not None:
            return user


@router.post("/register")
def register(request, data: UserCreateSchema):
    if User.objects.filter(email=data.email).exists():
        return {"message": "Email already registered"}
    user = User.objects.create(
        username=data.email,
        email=data.email,
        password=data.password
    )
    return {"message": "User created successfully"}


@router.post("/login")
def login(request, data: UserLoginSchema):
    try:
        user = User.objects.get(username=data.email)
        if not user.check_password(data.password):
            return {"error": "Password is incorrect"}

        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
    except User.DoesNotExist:
        return {"error": "User does not exist"}


@router.get("/profile", auth=AuthBearer())
def profile(request):
    if request.auth:
        return {"email": request.auth.email}
    return {"detail": "Not authenticated"}, 401
