from pathlib import Path
from typing import Iterable

from fastapi import Depends, WebSocket

from fastsockets.auth.SessionProvider import SessionProvider, get_session_id
from fastsockets.handlers.HandlersExecutorsManager import HandlersExecutorsManager
from fastsockets.handlers.auth.SessionExecutor import SessionHandlersExecutor
from fastsockets.handlers.Handlers import Handlers


class AuthHandlers(Handlers):
    def __init__(
        self,
        handler_files: Iterable[Path],
        session_provider: SessionProvider
    ) -> None:
        super().__init__(handler_files)

        self.sesssion_provider = session_provider
        self.executors_manager = HandlersExecutorsManager()


    async def get_executor(
        self,
        websocket: WebSocket,
        session_id: str = Depends(get_session_id)
    ) -> SessionHandlersExecutor:
        session = await self.sesssion_provider(session_id)

        # * Passing the HandlersExecutorManager into the executor so that it managers on
        # * its own when to add itself into the "broadcast pool" in this instance, when
        # * The connection was established, __aenter__ and to remove itself on __aexit__

        handler = SessionHandlersExecutor(
            websocket,
            self.executors_manager,
            self,
            session
        )

        return handler
