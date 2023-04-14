from typing import Any, Callable, Coroutine, Generic, ParamSpec, TypeVar

from pydantic import create_model

from fastsockets.handlers.BaseActionHandler import BaseActionHandler
from fastsockets.types.BaseMessage import BaseMessage

AllArgumentsMapping = dict[str, Any]
ResponseMessage = TypeVar('ResponseMessage', bound=BaseMessage)
ValidData = TypeVar('ValidData', bound=BaseMessage)

P = ParamSpec('P')
HandleCallable = Callable[P, Coroutine[ResponseMessage | None, Any, Any]]


def analyze_handle_callable(
    handle_callable: Callable[P, Coroutine[ResponseMessage | None, Any, Any]]
) -> tuple[
    AllArgumentsMapping,
    ResponseMessage | None
]:
    response_type: ResponseMessage | None = None

    # FIXME: Implement a dependency system similar to fastapi. Look at https://github.com/tiangolo/fastapi/blob/c81e136d75f5ac4252df740b35551cf2afb4c7f1/fastapi/dependencies/utils.py#L359
    all_arguments: AllArgumentsMapping = {}

    if isinstance(handle_callable, BaseActionHandler):
        function_with_annotations = handle_callable.handle
    else:
        function_with_annotations = handle_callable

    for arg_name, arg_type in function_with_annotations.__annotations__.items():
        if arg_name == 'return':
            response_type = arg_type
            continue

        field_data: tuple[Any, Any] = (arg_type, ...)
        if function_with_annotations.__defaults__ is not None:
            default_value = function_with_annotations.__defaults__[arg_name]
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

# ? Waiting for https://peps.python.org/pep-0696/
# ? Waiting for https://peps.python.org/pep-0695/


class ActionHandler(Generic[ValidData, ResponseMessage]):
    def __init__(
        self,
        action: str,
        handle_callable: HandleCallable,
    ) -> None:
        self.action = action
        self.handle_callable = handle_callable

        all_arguments, response_type = analyze_handle_callable(
            handle_callable
        )

        self.arguments = all_arguments
        self.response_validator = response_type

        DataValidator = create_data_validator(action, all_arguments)

        self.data_validator = DataValidator
        self.response_validator = response_type


    async def __call__(self, validated_data: ValidData) -> ResponseMessage | None:
        needed_data = {}
        for key in self.arguments.keys():
            needed_data[key] = getattr(validated_data, key)

        result = await self.handle_callable(**needed_data)

        if self.response_validator is not None:
            return self.response_validator.validate(result) 
