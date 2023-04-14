from functools import wraps
from typing import Callable, ParamSpec

from fastsockets.handlers.BaseActionHandler import HandlerResponse

P = ParamSpec('P')


def handler(
    action: str | None = None
) -> Callable[[Callable[..., HandlerResponse]], Callable[..., HandlerResponse]]:
    def decorator(
        func: Callable[P, HandlerResponse]
    ) -> Callable[..., HandlerResponse]:
        action_name = func.__name__ if action is None else action

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> HandlerResponse:
            return func(*args, **kwargs)

        setattr(wrapper, 'action_name', action_name)

        wrapper_decorators = getattr(wrapper, '__decorators__', list())
        wrapper_decorators.append(handler)

        setattr(wrapper, '__decorators__', wrapper_decorators)

        return wrapper
    return decorator
