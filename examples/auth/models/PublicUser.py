from pydantic import BaseModel


class PublicUser(BaseModel):
    id: int
    username: str
    bio: str | None
