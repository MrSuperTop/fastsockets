from examples.simple_class_based.models import (
    PingPayload,
    PongMessage,
    PongPayload,
)
from fastsockets import handler


@handler()
async def ping(
    payload: PingPayload
) -> PongMessage:
    return PongMessage(
        action='pong',
        payload=PongPayload(
            message=payload.message,
            status=True
        )
    )
