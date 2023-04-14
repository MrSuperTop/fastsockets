from typing import Literal

from pydantic import BaseModel

from fastsockets.types.BaseMessage import BaseMessage


class PingPayload(BaseModel):
    message: str


class PongPayload(BaseModel):
    message: str
    status: bool


class PongMessage(BaseMessage):
    action: Literal['pong']
    payload: PongPayload
