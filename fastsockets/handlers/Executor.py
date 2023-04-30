from typing import TYPE_CHECKING, Self

from fastapi import WebSocket

from fastsockets.auth.Session import Session
from fastsockets.types.BaseMessage import BaseMessage

if TYPE_CHECKING:
    from fastsockets.handlers.Handlers import Handlers


class HandlersExecutor:
    # TODO: Make it more generic, the Session does not have to be always provided
    def __init__(
        self,
        connection: WebSocket,
        handlers: 'Handlers',
    ) -> None:
        self.connection = connection
        self.handlers = handlers

        self.session: Session | None = None

    # TODO: Come up with something better than that, more abstractions, the end user does not have to be calling this in the handshake endpoint route
    # TODO: Make this fully generic, this can later be used as a way to provide global depencies to all of the handlers
    def saturate(self, session: Session):
        self.session = session

    async def __aenter__(
        self
    ) -> Self:
        await self.connection.accept()

        return self

    async def __aexit__(self, *_) -> None:
        await self.connection.close()

    async def handle_messages(self):
        async for json_message in self.connection.iter_json():
            # * Parsing only the primary fields first
            base_data = BaseMessage.parse_obj(json_message)
            handler = self.handlers.get_handler(base_data)

            if handler is None:
                continue

            # * We made sure primary data is valid, can parse the rest
            combined_data = {
                'session': self.session,
                **json_message
            }

            validated_data = handler.data_validator.parse_obj(combined_data)
            handler_result = await handler(validated_data)
            if handler_result is None:
                continue

            await self.connection.send_json(handler_result.dict())
