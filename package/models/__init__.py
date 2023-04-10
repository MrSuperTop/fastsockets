from pydantic import BaseModel


class RegisterPayload(BaseModel):
    name: str
    email: str


class RegisterResponse(BaseModel):
    status: bool
