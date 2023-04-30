import inspect
from typing import (
    Any,
    Callable,
    Coroutine,
    ForwardRef,
    Generic,
    ParamSpec,
    TypeVar,
)

from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo, ModelField
from pydantic.typing import evaluate_forwardref
from pydantic.utils import lenient_issubclass

from fastsockets.handlers.BaseActionHandler import ArgumentsMapping, BaseActionHandler
from fastsockets.handlers.params.Dependency import Dependency
from fastsockets.types.BaseMessage import BaseMessage

ResponseMessage = TypeVar('ResponseMessage', bound=BaseMessage)
ValidData = TypeVar('ValidData', bound=BaseMessage)

P = ParamSpec('P')
HandleCallable = Callable[P, Coroutine[ResponseMessage | None, Any, Any]]
# TODO: Code separation into a folder?


def get_typed_signature(call: Callable[..., Any]) -> inspect.Signature:
    signature = inspect.signature(call)
    globalns = getattr(call, "__globals__", {})
    typed_params = [
        inspect.Parameter(
            name=param.name,
            kind=param.kind,
            default=param.default,
            annotation=get_typed_annotation(param.annotation, globalns),
        )
        for param in signature.parameters.values()
    ]

    typed_signature = inspect.Signature(
        typed_params,
        return_annotation=get_typed_annotation(signature.return_annotation,  globalns)
    )

    return typed_signature


def get_typed_annotation(annotation: Any, globalns: dict[str, Any]) -> Any:
    if isinstance(annotation, str):
        annotation = ForwardRef(annotation)
        annotation = evaluate_forwardref(annotation, globalns, globalns)

    return annotation


def analyze_param(
    param_name: str,
    value: inspect.Parameter
) -> tuple[Any, Dependency | None, ModelField | None]:
    type_annotation: Any = Any
    dependency: Dependency | None = None
    model_filed: ModelField | None = None

    if value.annotation is not inspect.Signature.empty:
        type_annotation = value.annotation

    if isinstance(value.default, Dependency):
        dependency = value.default

        additional_argument, dependencies, _ = analyze_callable(
            dependency.callable
        )

        dependency.other_arguments = additional_argument
        dependency.depends_on = dependencies

    if lenient_issubclass(value.annotation, BaseModel):
        model_filed = ModelField(
            name=param_name,
            type_=value.annotation,
            class_validators={},
            model_config=value.annotation.Config
        )

    return type_annotation, dependency, model_filed


def analyze_callable(
    handle_callable: Callable[P, Coroutine[ResponseMessage | None, Any, Any]]
) -> tuple[
    ArgumentsMapping,
    dict[str, Dependency],
    ResponseMessage | None
]:
    all_arguments: ArgumentsMapping = {}
    dependencies: dict[str, Dependency] = {}

    if isinstance(handle_callable, BaseActionHandler):
        function_with_annotations = handle_callable.handle
    else:
        function_with_annotations = handle_callable

    signature = get_typed_signature(function_with_annotations)
    signature_params = signature.parameters

    response_type: None | ResponseMessage = None
    if (
        signature.return_annotation is not inspect.Signature.empty
    ):
        response_type = signature.return_annotation

    for param_name, param in signature_params.items():
        type_annotation, dependency, model_field = analyze_param(
            param_name,
            param
        )

        field_info: FieldInfo | ModelField = FieldInfo()
        if model_field is not None:
            field_info = model_field
        elif param.default is not inspect.Signature.empty:
            field_info = FieldInfo(param.default)

        if dependency is not None:
            dependencies[param_name] = dependency
        else:
            all_arguments[param_name] = (type_annotation, field_info)

    return all_arguments, dependencies, response_type


def create_data_validator(
    action_name: str,
    additional_params: ArgumentsMapping
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

        all_arguments, dependencies, response_type = analyze_callable(
            handle_callable
        )

        self.arguments = all_arguments
        self.dependencies = dependencies
        self.response_validator = response_type

        DataValidator = create_data_validator(action, all_arguments)

        self.data_validator = DataValidator
        self.response_validator = response_type


    # TODO: Implement using the use_cache property on the Dependency instance
    def _prepare_dependency_arguments(
        self,
        present_data: ValidData,
        dependency: Dependency
    ) -> dict[str, Any]:
        needed_aguments = {}
        if dependency.other_arguments is not None:
            for key in dependency.other_arguments.keys():
                needed_aguments[key] = getattr(present_data, key)

        if dependency.depends_on is not None:
            for name, child_dependency in dependency.depends_on.items():
                child_needed_arguments = self._prepare_dependency_arguments(
                    present_data,
                    child_dependency
                )

                needed_aguments[name] = child_dependency.callable(
                    **child_needed_arguments
                )

        return needed_aguments


    async def __call__(self, validated_data: ValidData) -> ResponseMessage | None:
        needed_data = {}
        for key in self.arguments.keys():
            needed_data[key] = getattr(validated_data, key)

        for dependency_name, dependency in self.dependencies.items():
            arguments = self._prepare_dependency_arguments(validated_data, dependency)
            needed_data[dependency_name] = dependency.callable(**arguments)

        result = await self.handle_callable(**needed_data)

        if self.response_validator is not None:
            return self.response_validator.validate(result) 
