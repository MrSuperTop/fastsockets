from fastapi import WebSocket

from fastsockets.auth.Session import Session
from fastsockets.handlers.ActionHandler import ActionHandler
from fastsockets.handlers.auth.AuthHandlers import HandlersExecutorsManager
from fastsockets.handlers.Executor import BaseAdditionalDependencies, HandlersExecutor
from fastsockets.handlers.Handlers import Handlers
from fastsockets.types.BaseMessage import BaseMessage


class SessionBaseAdditionalDependencies(BaseAdditionalDependencies):
    session: Session


class SessionHandlersExecutor(HandlersExecutor[SessionBaseAdditionalDependencies]):
    def __init__(
        self,
        connection: WebSocket,
        executors_manager: HandlersExecutorsManager,
        handlers: Handlers,
        session: Session
    ) -> None:
        super().__init__(connection, handlers)

        self.executors_manager = executors_manager
        self.manager_unique_id: int | None = None

        self.session = session
        self.manager_group_id = self.session.data.user_id
        self.saturate(
            session=session
        )

    def _connection_established(self) -> None:
        self.manager_unique_id = self.executors_manager.add_executor(
            self.manager_group_id,
            self
        )

        return super()._connection_established()

    def _connection_closed(self) -> None:
        # TODO: proper logging output, don't throw an error here, see how to handle
        if self.manager_unique_id is None:
            return

        is_removed = self.executors_manager.remove_executor(
            self.manager_group_id,
            self.manager_unique_id,
        )

        # TODO: Log the fact that the connection was not removed
        if not is_removed:
            return

        return super()._connection_closed()

    async def broadcast(self, message: BaseMessage) -> None:
        await self.executors_manager.broadcast(
            self.manager_group_id,
            message
        )

    async def _send_handler_result(
        self,
        _: ActionHandler,
        handler_result: BaseMessage
    ) -> None:
        # TODO: broadcast_response param to the ActionHandler class, and check the param to determine if the message should be broadcasted or simply sent
        await self.broadcast(handler_result)
