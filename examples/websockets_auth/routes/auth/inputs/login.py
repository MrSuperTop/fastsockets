from pydantic import BaseModel

from examples.websockets_auth.db.models.PublicUser import PublicUser


class LoginInput(BaseModel):
    usernameOrEmail: str
    password: str


class LoginResponse(BaseModel):
    user: PublicUser
