from pydantic import BaseModel


class LogoutResponse(BaseModel):
    success: bool
