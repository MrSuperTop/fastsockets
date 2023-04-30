from abc import ABC
from typing import Generic, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

Payload = TypeVar('Payload', bound=BaseModel)


class BaseMessage(ABC, GenericModel, Generic[Payload]):
    action: str
    payload: Payload

    class Config:
        arbitrary_types_allowed = True
        extra = 'allow'
