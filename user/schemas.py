from ninja import Schema
from pydantic import BaseModel, EmailStr


class UserSchema(Schema):
    id: int
    email: EmailStr


class UserCreateSchema(BaseModel):
    email: EmailStr
    password: str


class UserLoginSchema(Schema):
    email: EmailStr
    password: str


class LoginResponseSchema(Schema):
    refresh: str
    access: str

