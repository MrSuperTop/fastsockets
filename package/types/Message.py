from typing import Generic, TypeVar

from pydantic import BaseModel

Payload = TypeVar('Payload', bound=BaseModel)


class Message(BaseModel, Generic[Payload]):
    action: str
    payload: Payload
