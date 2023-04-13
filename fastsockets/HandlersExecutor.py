from fastapi import WebSocket

from fastsockets.load_handlers import Handlers
from fastsockets.types.BaseMessage import BaseMessage


class HandlersExecutor:
    def __init__(
        self,
        connection: WebSocket,
        handlers: Handlers
    ) -> None:
        self.connection = connection
        self.handlers = handlers


    async def accept(self):
        await self.connection.accept()


    async def handle_messages(self):
        async for json_message in self.connection.iter_json():
            # * Parsing only the primary fields first
            base_data = BaseMessage.parse_obj(json_message)
            handler = self.handlers.get(base_data.action)

            if handler is None:
                continue

            # * We made sure primary data is valid, can parse the rest
            validated_data = handler.data_validator.parse_obj(json_message)
            handler_result = await handler(validated_data)
            if handler_result is None:
                continue

            await self.connection.send_json(handler_result.dict())


class HandlersExecutorProvider:
    def __init__(self, handlers: Handlers) -> None:
        self.handlers = handlers


    def __call__(
        self,
        websocket: WebSocket,
    ) -> HandlersExecutor:
        return HandlersExecutor(
            websocket,
            self.handlers
        )
