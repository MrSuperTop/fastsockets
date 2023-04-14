from typing import Any, ParamSpec

from pydantic import create_model

from fastsockets.handlers.BaseActionHandler import BaseActionHandler, HandleFunction, HandlerResponse
from fastsockets.types.BaseMessage import BaseMessage

AllArgumentsMapping = dict[str, tuple[Any, Any]]

P = ParamSpec('P')


def analyze_handle_function(
    handler_function: HandleFunction
) -> tuple[
    AllArgumentsMapping,
    HandlerResponse
]:
    response_type: HandlerResponse = None

    # TODO: Come up with a more robust way to handle this. Param class to incapsulate all needed logic and data
    all_arguments: AllArgumentsMapping = {}

    for arg_name, arg_type in handler_function.__annotations__.items(): # type: ignore
        if arg_name == 'return':
            response_type = arg_type
            continue

        # FIXME: Make sure this works (__defaults__???)
        field_data: tuple[Any, Any] = (arg_type, ...)
        if handler_function.__defaults__ is not None:
            default_value = handler_function.__defaults__[arg_name]
            if default_value is not None:
                field_data = (arg_type, default_value)

        all_arguments[arg_name] = field_data

    return all_arguments, response_type


def create_data_validator(
    action_name: str,
    additional_params: AllArgumentsMapping
) -> type[BaseMessage]:
    DataValidator = create_model(
        f'{action_name.capitalize()}Validator',
        __base__=BaseMessage,
        **additional_params
    )

    return DataValidator


def create_handler(
    action_name: str,
    handle_function: HandleFunction,
    handler_class: type[BaseActionHandler]
) -> BaseActionHandler:
    all_arguments, response_type = analyze_handle_function(
        handle_function
    )

    DataValidator = create_data_validator(action_name, all_arguments)

    handler = handler_class(
        action_name,
        # TODO: Other types of object could be in the definition of the handler and this will likely break, as we provide unsufficient amount of params to the handler in the HandlersExecutor
        all_arguments,
        DataValidator,
        response_type,
        handle_function
    )

    return handler
