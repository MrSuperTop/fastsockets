from importlib import import_module
from inspect import isclass, isfunction
from pathlib import Path
from typing import Iterable

from fastsockets.create_handler import create_handler
from fastsockets.handlers.BaseActionHandler import BaseActionHandler
from fastsockets.handlers.handler import handler

Handlers = dict[str, BaseActionHandler]


def load_handlers(
    handler_files: Iterable[Path]
) -> Handlers:
    handlers: Handlers = {}

    for file in handler_files:
        full_module_name = '.'.join(
            file.relative_to(Path().absolute()).with_suffix('').parts
        ) 

        module = import_module(full_module_name)

        # * Looking for needed classes, which implement BaseActionHandler
        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)

            is_class_based = isclass(attribute) \
                and isinstance(BaseActionHandler, attribute)

            # * In case the handler was defined usign a class
            if is_class_based:
                HandlerClass: type[BaseActionHandler] = attribute
                action_name = module.__name__.rpartition('.')[2]

                # * Ignored, because the type checker considers HandlerClass to be of type "type" and not of type "type[BaseActionHandler]"
                # * For that reason, the property is not defined, but it should be.
                # * I am not really sure hot to properly type it so it's working the right way and was not able to find anything for now

                handlers[action_name] = create_handler(
                    action_name,
                    HandlerClass.handle # type: ignore
                )

                continue

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
            DynamicHandler = type(
                f'{action_name.capitalize()}Handler',
                (BaseActionHandler, ),
                {}
            )

            handlers[action_name] = create_handler(
                action_name,
                wrapped_function,
                DynamicHandler
            )

    return handlers
