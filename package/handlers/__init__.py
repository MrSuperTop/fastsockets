from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

NeededArgumentMapping = dict[str, type[BaseModel]]
JsonResponse = BaseModel


class BaseActionHandler(ABC):
    def __init__(
        self,
        name: str,
        argument_mapping: NeededArgumentMapping
    ) -> None:
        self.name = name
        self.argument_object_mapping: NeededArgumentMapping = argument_mapping

    @abstractmethod
    async def __call__(self, *args: Any, **kwds: Any) -> JsonResponse:
        pass
