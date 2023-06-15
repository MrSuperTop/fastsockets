from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Self,
    TypedDict,
    TypeVar,
    cast,
)

from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect

from fastsockets.handlers.ActionHandler import ActionHandler
from fastsockets.types.BaseMessage import BaseMessage

if TYPE_CHECKING:
    from fastsockets.handlers.Handlers import Handlers

class BaseAdditionalDependencies(TypedDict):
    handlers_executor: 'HandlersExecutor'


AdditionalDependencies = TypeVar(
    'AdditionalDependencies',
    bound=BaseAdditionalDependencies
)

# TODO: Better naming for this classes... Making a subclass does not seem to be convenient https://stackoverflow.com/questions/75278075/fastapi-custom-websocket-object
class HandlersExecutor(Generic[AdditionalDependencies]):
    def __init__(
        self,
        connection: WebSocket,
        handlers: 'Handlers',
    ) -> None:
        self.connection = connection
        self.handlers = handlers

        self.additional_dependencies: AdditionalDependencies = {
            'handlers_executor': self
        }

    def saturate(self, **additional_dependencides: Any):

        self.additional_dependencies = cast(
            AdditionalDependencies,
            {
                **self.additional_dependencies,
                **additional_dependencides
            }
        )

    def _connection_established(self) -> None:
        ...

    def _connection_closed(self) -> None:
        ...

    async def __aenter__(
        self
    ) -> Self:
        try:
            await self.connection.accept()
            self._connection_established()
        except WebSocketDisconnect:
            self._connection_closed()


        return self

    async def __aexit__(self, *_) -> None:
        await self.connection.close()
        self._connection_closed()

    async def send_message(self, message: BaseMessage):
        try:
            await self.connection.send_json(message.dict())
        except WebSocketDisconnect:
            pass

    async def _send_handler_result(
        self,
        _: ActionHandler,
        handler_result: BaseMessage
    ) -> None:
        await self.send_message(handler_result)


    async def handle_messages(self):
        async for json_message in self.connection.iter_json():
            # * Parsing only the primary fields first
            base_data = BaseMessage.parse_obj(json_message)
            handler = self.handlers.get_handler(base_data)

            # TODO: Proper error message, that this action could not be found
            if handler is None:
                continue

            # * We made sure primary data is valid, can parse the rest
            combined_data = {
                **self.additional_dependencies,
                **json_message
            }

            validated_data = handler.data_validator.parse_obj(combined_data)
            handler_result: BaseMessage | None = await handler(validated_data)
            if handler_result is None:
                continue

            await self._send_handler_result(handler, handler_result)
