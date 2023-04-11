import sys
from importlib.machinery import FileFinder
from inspect import isclass
from pathlib import Path
from pkgutil import iter_modules
from typing import Iterable

from pydantic import BaseModel, create_model

from package.handlers import BaseActionHandler, ParsableArgumentMapping
from package.types.Message import Message


def load_handlers(handlers_pathes: Iterable[Path]) -> dict[str, BaseActionHandler]:
    handlers: dict[str, BaseActionHandler] = {}
    handler_files = [str(single_path.absolute()) for single_path in handlers_pathes]

    for (file_finder, module_name, _) in iter_modules(handler_files):
        if not isinstance(file_finder, FileFinder):
            continue

        full_package_name = '.'.join([
            *Path(file_finder.path).relative_to(Path().absolute()).parts,
            module_name
        ]) 

        if full_package_name in sys.modules:
            module = sys.modules[full_package_name]
        else:
            loader, _ = file_finder.find_loader(full_package_name)
            if loader is None:
                continue

            module = loader.load_module(full_package_name)

        # * Looking for needed classes, which implement BaseActionHandler
        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)

            if not isclass(attribute) or BaseActionHandler not in attribute.__bases__:
                continue

            action_name = module.__name__.rpartition('.')[2]
            parsable_objects: ParsableArgumentMapping = {}

            for arg_name, arg_type in attribute.__call__.__annotations__.items():
                # TODO: Also implement data validation for the response data
                if arg_name == 'return':
                    continue

                if not isclass(arg_type) or BaseModel not in arg_type.__bases__:
                    continue

                parsable_objects[arg_name] = (arg_type, ...)

            HandlerClass: BaseActionHandler = attribute
            DataValidator = create_model(
                f'{action_name.capitalize()}Validator',
                __base__=Message,
                **parsable_objects
            )

            handlers[action_name] = HandlerClass(
                action_name,
                DataValidator
            )

    return handlers
