from examples.simple.models import PingMessage, PingPayload, PongMessage, PongPayload
from fastsockets.handlers import BaseActionHandler


# TODO: Do we really need to provide a PingMessage here? We have managed to create it dinamically previously.
class PingHandler(BaseActionHandler[PingMessage, PongMessage]):
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
