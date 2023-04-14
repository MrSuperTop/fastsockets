from typing import TYPE_CHECKING

from fastapi import WebSocket

from fastsockets.types.BaseMessage import BaseMessage

if TYPE_CHECKING:
    from fastsockets.handlers.Handlers import Handlers


class HandlersExecutor:
    def __init__(
        self,
        connection: WebSocket,
        handlers: 'Handlers'
    ) -> None:
        self.connection = connection
        self.handlers = handlers


    async def accept(self):
        await self.connection.accept()


    async def handle_messages(self):
        async for json_message in self.connection.iter_json():
            # * Parsing only the primary fields first
            base_data = BaseMessage.parse_obj(json_message)
            handler = self.handlers.get_handler(base_data)

            if handler is None:
                continue

            # * We made sure primary data is valid, can parse the rest
            validated_data = handler.data_validator.parse_obj(json_message)
            handler_result = await handler(validated_data)
            if handler_result is None:
                continue

            await self.connection.send_json(handler_result.dict())
