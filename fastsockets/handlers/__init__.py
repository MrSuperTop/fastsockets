from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from fastsockets.types.BaseMessage import BaseMessage

ResponseMessage = TypeVar('ResponseMessage', bound=BaseMessage)
ValidData = TypeVar('ValidData', bound=BaseMessage)
HandlerResponse = BaseMessage | None


# TODO: Implement a decorator, which creates a handler from a function
# ? Waiting for https://peps.python.org/pep-0696/
# ? Waiting for https://peps.python.org/pep-0695/

class BaseActionHandler(ABC, Generic[ValidData, ResponseMessage]):
    def __init__(
        self,
        action: str,
        # FIXME: Implement a dependency system similar to fastapi. Look at https://github.com/tiangolo/fastapi/blob/c81e136d75f5ac4252df740b35551cf2afb4c7f1/fastapi/dependencies/utils.py#L359
        needed_params: dict[str, Any],
        data_validator: type[ValidData],
        response_type: type[ResponseMessage] | None
    ) -> None:
        self.action = action
        self.needed_params = needed_params
        self.data_validator = data_validator
        self.response_validator = response_type


    @abstractmethod
    async def handle(self, *args: Any, **kwds: Any) -> ResponseMessage | None:
        ...


    async def __call__(self, validated_data: ValidData) -> ResponseMessage | None:
        # TODO: Look at how the dependencies are done in fastapi. Implement a similar system
        needed_data: dict[str, Any] = {}
        for key in self.needed_params.keys():
            needed_data[key] = getattr(validated_data, key)

        result = await self.handle(**needed_data)

        if self.response_validator is not None:
            return self.response_validator.validate(result) 
