from typing import Any, Callable, Generic, ParamSpec, Self, TypeVar

from fastsockets.handlers.BaseActionHandler import ArgumentsMapping

DependencyArguments = ParamSpec('DependencyArguments')
DependencyResult = TypeVar('DependencyResult')
OtherArguments = ArgumentsMapping


class Dependency(Generic[DependencyArguments, DependencyResult]):
    def __init__(
        self,
        dependency: Callable[DependencyArguments, DependencyResult],
        other_arguments: OtherArguments | None = None,
        depends_on: dict[str, Self] | None = None,
        use_cache: bool = True
    ) -> None:
        self.callable = dependency

        self.depends_on = depends_on
        self.other_arguments = other_arguments

        self.use_cache = use_cache


def Depends(
    dependency: Callable[DependencyArguments, Any],
    use_cache: bool = True
) -> Any:
    return Dependency(
        dependency,
        None,
        None,
        use_cache
    )
