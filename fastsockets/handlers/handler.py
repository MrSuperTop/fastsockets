from functools import wraps
from typing import Callable, ParamSpec

from fastsockets.handlers import AnyHandlerResponse

P = ParamSpec('P')


def handler(
    action: str | None = None
) -> Callable[[Callable[..., AnyHandlerResponse]], Callable[..., AnyHandlerResponse]]:
    def decorator(
        func: Callable[P, AnyHandlerResponse]
    ) -> Callable[..., AnyHandlerResponse]:
        action_name = func.__name__ if action is None else action

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> AnyHandlerResponse:
            return func(*args, **kwargs)

        setattr(wrapper, 'action_name', action_name)

        wrapper_decorators = getattr(wrapper, '__decorators__', list())
        wrapper_decorators.append(handler)

        setattr(wrapper, '__decorators__', wrapper_decorators)

        return wrapper
    return decorator
