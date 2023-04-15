from pydantic import BaseModel


class User(BaseModel):
    id: int
    email: str
    password: str
    username: str
    bio: str | None
