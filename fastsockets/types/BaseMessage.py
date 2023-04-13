from abc import ABC
from typing import Generic, TypeVar

from pydantic import BaseModel

Payload = TypeVar('Payload', bound=BaseModel)


class BaseMessage(ABC, BaseModel, Generic[Payload]):
    action: str
    payload: Payload

    class Config:
        extra = 'allow'
