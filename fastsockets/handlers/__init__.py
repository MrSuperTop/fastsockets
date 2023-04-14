from typing import Any, Callable, Coroutine, ParamSpec

from fastsockets.types.BaseMessage import BaseMessage

P = ParamSpec('P')
AnyHandlerResponse = BaseMessage | Coroutine[BaseMessage, Any, Any] | None
AnyHandleFunction = Callable[P, Coroutine[AnyHandlerResponse | None, Any, Any]]
