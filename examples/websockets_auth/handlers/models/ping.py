from typing import Literal

from pydantic import BaseModel

from fastsockets import BaseMessage


class PingPayload(BaseModel):
    message: str


class PongPayload(BaseModel):
    initiator_action: str
    message: str
    success: bool


class PongMessage(BaseMessage[PongPayload]):
    action: Literal['pong']
