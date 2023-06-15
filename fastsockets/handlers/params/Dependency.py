from typing import Any, Callable, Generic, ParamSpec, Self, TypeVar

from pydantic import BaseModel

from fastsockets.handlers.BaseActionHandler import ArgumentsMapping

DependencyArguments = ParamSpec('DependencyArguments')
DependencyResult = TypeVar('DependencyResult')
PartialConcreteData = TypeVar('PartialConcreteData', bound=BaseModel)
OtherArguments = ArgumentsMapping
DependencyCache = dict[str, DependencyResult]


# TODO: Make the dependecies interchangable with fastapi dependencies
class Dependency(Generic[DependencyArguments, DependencyResult, PartialConcreteData]):
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

    def _prepare_arguments(
        self,
        present_data: PartialConcreteData,
        dependency_cache: DependencyCache,
    ) -> dict[str, Any]:
        needed_aguments = {}
        if self.other_arguments is not None:
            for key in self.other_arguments.keys():
                needed_aguments[key] = getattr(present_data, key)

        if self.depends_on is not None:
            for name, child_dependency in self.depends_on.items():
                child_dependency_result = child_dependency(
                    present_data,
                    dependency_cache,
                )

                needed_aguments[name] = child_dependency_result

        return needed_aguments

    def _callable_wrapper(
        self,
        *args: DependencyArguments.args,
        **kwargs: DependencyArguments.kwargs
    ) -> DependencyResult:
        """This function is created to eliminate errors which appear, when providing
        the dict recieved from Dependency.prepare_arguments to the Dependency.callable
        I am not exactly sure how to fix this as of right now.
        The error: "Pyright: Arguments for ParamSpec "DependencyArguments@Dependency" are missing"
        Code example:
        callable_arguments = self.prepare_arguments(present_data, dependency_cache)
        self.callable(**callable_arguments)
        Useful links:
        \thttps://github.com/python/mypy/issues/12718
        \thttps://github.com/python/mypy/issues/12386
        """
        return self.callable(*args, **kwargs)

    def __call__(
        self,
        present_data: PartialConcreteData,
        dependency_cache: DependencyCache = dict(),
    ) -> DependencyResult:
        cache_key = getattr(self.callable, "__name__", None)

        if self.use_cache and cache_key is not None and cache_key in dependency_cache:
            return dependency_cache[cache_key]

        callable_arguments = self._prepare_arguments(present_data, dependency_cache)
        result = self._callable_wrapper(**callable_arguments)

        if cache_key is not None:
            dependency_cache[cache_key] = result

        return result
        


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
