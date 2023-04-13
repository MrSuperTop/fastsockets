from importlib import import_module
from inspect import isclass
from pathlib import Path
from typing import Any, Iterable

from pydantic import BaseModel, create_model

from fastsockets.handlers import BaseActionHandler, HandlerResponse
from fastsockets.types.BaseMessage import BaseMessage

Handlers = dict[str, BaseActionHandler]
ParsableArgumentMapping = dict[str, tuple[type[BaseModel], Any]]

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

            if not isclass(attribute) or BaseActionHandler not in attribute.__bases__:
                continue

            handler: type[BaseActionHandler] = attribute
            action_name = module.__name__.rpartition('.')[2]
            response_type: HandlerResponse = None
            parsable_objects: ParsableArgumentMapping = {}

            # * Ignored, because the type checker considers handler to be of type "type" and not of type "type[BaseActionHandler]"
            # * For that reason, the property is not defined, but it should be.
            # * I am not really sure hot to properly type it so it's working the right way and was not able to find anything for now

            for arg_name, arg_type in handler.handle.__annotations__.items(): # type: ignore
                if arg_name == 'return':
                    response_type = arg_type
                    continue

                if not isclass(arg_type) or BaseModel not in arg_type.__bases__:
                    continue

                parsable_objects[arg_name] = (arg_type, ...)

            HandlerClass: BaseActionHandler = attribute
            DataValidator = create_model(
                f'{action_name.capitalize()}Validator',
                __base__=BaseMessage,
                **parsable_objects
            )

            handlers[action_name] = HandlerClass(
                action_name,
                # TODO: Other types of object could be in the definition of the handler and this will likely break, as we provide unsufficient amount of params to the handler in the HandlersExecutor
                parsable_objects,
                DataValidator,
                response_type
            )

    return handlers
