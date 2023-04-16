from pydantic import BaseModel

from examples.websockets_auth.models.PublicUser import PublicUser


class RegisterInput(BaseModel):
    email: str
    username: str
    password: str
    bio: str


class RegisterResponse(BaseModel):
    user: PublicUser
