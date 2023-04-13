from pathlib import Path
from typing import Iterable

from fastsockets.HandlersExecutor import HandlersExecutorProvider
from fastsockets.load_handlers import load_handlers


def get_executor_provider(
    handlers_locations: Iterable[Path]
) -> HandlersExecutorProvider:
    handlers = load_handlers(handlers_locations)
    handlers_exectors_provider = HandlersExecutorProvider(handlers)

    return handlers_exectors_provider
