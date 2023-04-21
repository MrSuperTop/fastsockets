from examples.websockets_auth.handlers.models.ping import (
    PingPayload,
    PongMessage,
    PongPayload,
)
from fastsockets import handler


@handler()
async def ping(
    action: str,
    payload: PingPayload
) -> PongMessage:
    return PongMessage(
        action='pong',
        payload=PongPayload(
            initiator_action=action,
            message=payload.message,
            success=True
        )
    )
