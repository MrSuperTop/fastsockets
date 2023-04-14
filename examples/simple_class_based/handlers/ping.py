from examples.simple_class_based.models import (
    PingPayload,
    PongMessage,
    PongPayload,
)
from fastsockets.handlers.BaseActionHandler import BaseActionHandler


class PingHandler(BaseActionHandler[PongMessage]):
    async def handle(
        self,
        payload: PingPayload
    ) -> PongMessage:
        return PongMessage(
            action='pong',
            payload=PongPayload(
                message=payload.message,
                status=True
            )
        )
