from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from fastsockets.types.BaseMessage import BaseMessage

ResponseMessage = TypeVar('ResponseMessage', bound=BaseMessage)


class BaseActionHandler(ABC, Generic[ResponseMessage]):
    def __init__(
        self,
        action: str | None = None,
    ) -> None:
        self.action = action


    @abstractmethod
    async def handle(self, *args: Any, **kwds: Any) -> ResponseMessage | None:
        ...


    async def __call__(self, *args: Any, **kwds: Any) -> ResponseMessage | None:
        return await self.handle(*args, **kwds)
