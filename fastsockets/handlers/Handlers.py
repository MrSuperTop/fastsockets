from importlib import import_module
from pathlib import Path
from typing import Iterable

from fastapi import WebSocket

from fastsockets.get_handler_from_module import get_handler_from_module
from fastsockets.handlers.ActionHandler import ActionHandler
from fastsockets.handlers.Executor import HandlersExecutor
from fastsockets.types.BaseMessage import BaseMessage

HandlersContainer = dict[str, ActionHandler]


class Handlers:
    def __init__(
        self,
        handler_files: Iterable[Path]
    ) -> None:
        self._handlers: HandlersContainer = {}

        for file in handler_files:
            full_module_name = '.'.join(
                file.relative_to(Path().absolute()).with_suffix('').parts
            ) 

            module = import_module(full_module_name)
            found_handler = get_handler_from_module(module)

            # TODO: Add logging, a warning message here
            if found_handler is None:
                continue

            self.add_handler(found_handler)


    def get_executor(
        self,
        websocket: WebSocket,
    ) -> HandlersExecutor:
        return HandlersExecutor(
            websocket,
            self
        )


    @property
    def handlers(self) -> HandlersContainer:
        return self._handlers


    def add_handler(self, new_handler: ActionHandler) -> None:
        self._handlers[new_handler.action] = new_handler


    def get_handler(self, for_message: BaseMessage) -> ActionHandler | None:
        return self._handlers.get(for_message.action, None)
