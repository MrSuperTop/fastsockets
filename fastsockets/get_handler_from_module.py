from inspect import isclass, isfunction
from types import ModuleType

from fastsockets.handlers.ActionHandler import ActionHandler
from fastsockets.handlers.BaseActionHandler import BaseActionHandler
from fastsockets.handlers.handler import handler


def get_handler_from_module(module: ModuleType) -> ActionHandler | None:
    # * Looking for needed classes, which implement BaseActionHandler
    for attribute_name in dir(module):
        attribute = getattr(module, attribute_name  )

        is_class_based = isclass(attribute) \
            and attribute is not BaseActionHandler \
            and issubclass(attribute, BaseActionHandler)

        # * In case the handler was defined usign a class
        if is_class_based:
            HandlerClass: type[BaseActionHandler] = attribute
            action_name = module.__name__.rpartition('.')[2]

            return ActionHandler(
                action_name,
                HandlerClass(action_name)
            )

        # * In case the handler was defined with the help of the "handler" decorator
        is_wrapped_function = isfunction(attribute) \
            and hasattr(attribute, '__wrapped__')

        if not is_wrapped_function:
            continue

        wrapped_function = getattr(attribute, '__wrapped__')
        is_decorator_based = hasattr(attribute, '__decorators__') \
            and handler in getattr(attribute, '__decorators__') \
            and hasattr(attribute, 'action_name')

        if not is_decorator_based:
            continue

        action_name = getattr(attribute, 'action_name')
        return ActionHandler(
            action_name,
            wrapped_function
        )
