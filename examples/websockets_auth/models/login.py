from pydantic import BaseModel

from examples.auth.models.PublicUser import PublicUser


class LoginInput(BaseModel):
    usernameOrEmail: str
    password: str


class LoginResponse(BaseModel):
    user: PublicUser
