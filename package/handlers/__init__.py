from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from package.types.Message import Message

ParsableArgumentMapping = dict[str, tuple[type[BaseModel], Any]]
JsonResponse = BaseModel


class BaseActionHandler(ABC):
    def __init__(
        self,
        action: str,
        data_validator: type[Message]
    ) -> None:
        self.action = action
        self.data_validator = data_validator

    @abstractmethod
    async def __call__(self, *args: Any, **kwds: Any) -> JsonResponse:
        pass
