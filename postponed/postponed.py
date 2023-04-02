"""Deferred function evaluation with static and run-time type checks.

https://github.com/martinResearch/postponed/blob/main/README.md
"""
import inspect
import multiprocessing
import sys
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, Generic, Iterable, List, TypeVar

from typeguard import check_type

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec
else:
    from typing import ParamSpec

P = ParamSpec("P")
R = TypeVar("R")


def check_arguments(
    signature: inspect.Signature, args: P.args, kwargs: Dict[str, Any]  # type: ignore
) -> None:
    # check all required parameters are provided
    all_args = kwargs.copy()
    for name, value in zip(signature.parameters.keys(), args):
        if name in all_args:
            raise ValueError(f"Argument {name} is provided twice")
        all_args[name] = value

    for name in kwargs.keys():
        if name not in signature.parameters:
            raise ValueError(f"Argument {name} not expected")

    for name, v in signature.parameters.items():
        if v.default == inspect._empty:
            if name not in all_args:
                raise ValueError(f"Missing required argument {name}")

    # checking the types using the function check_type from the typeguard library
    for name, value in all_args.items():
        assert name in signature.parameters
        expected_type = signature.parameters[name].annotation
        check_type(value=value, expected_type=expected_type)


class Task(Generic[P, R]):
    """Postponed evaluation of a function with arguments."""

    def __init__(self, f: Callable[P, R], args: P.args, kwargs: P.kwargs):  # type: ignore
        self.f = f
        self.args = args
        self.kwargs = kwargs

    def __call__(self) -> R:
        return self.f(*self.args, **self.kwargs)


class Postponed(Generic[P, R]):
    """Postponed version of a given function."""

    def __init__(self, f: Callable[P, R], check_inputs: bool = True):
        self._f = f
        self.check_inputs = check_inputs
        if self.check_inputs:
            self._signature = inspect.signature(f)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Callable[[], R]:
        if self.check_inputs:
            check_arguments(signature=self._signature, args=args, kwargs=kwargs)
        return Task(self._f, args, kwargs).__call__


def postponed(
    f: Callable[P, R], /, check_inputs: bool = True
) -> Callable[P, Callable[[], R]]:
    """Lazy version of a given function.

    If `check_inputs` is True then the input arguments and their types are checked as early as possible to fail fast.

    Example:
    >>> p = postponed(print)(5)
    >>> p()
        5
    """
    return Postponed(f, check_inputs=check_inputs).__call__


def execute_tasks_threads(
    tasks: Iterable[Callable[[], R]], max_workers: int
) -> List[R]:
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(task) for task in tasks]
        results = [future.result() for future in futures]
    return results


def execute_tasks_processes(
    tasks: Iterable[Callable[[], R]], max_workers: int
) -> List[R]:
    pool = multiprocessing.Pool(processes=max_workers)
    futures = [pool.apply_async(task, ()) for task in tasks]
    results = [future.get() for future in futures]
    return results
