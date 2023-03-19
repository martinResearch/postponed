
from typing import Any, Dict, TypeVar, Callable, Generic, ParamSpec, Iterable, List
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
import inspect
from typeguard import check_type

P = ParamSpec("P")
R = TypeVar("R")


def check_arguments(signature: inspect.Signature, args: P.args, kwargs: Dict[str, Any]) -> None:
    # check all required parameters are provided
    all_args = kwargs.copy()
    for name, value in zip(signature.parameters.keys(), args):
        if name in all_args:
            raise ValueError(f"Argument {name} is provided twice")
        all_args[name] = value

    for name, value in kwargs.items():
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
        check_type(argname=name, value=value, expected_type=expected_type)


class Delayed(Generic[P, R]):
    """Delayed evaluation of a function with arguments."""

    def __init__(self, f:  Callable[P, R], args: P.args, kwargs: P.kwargs):
        self.f = f
        self.args = args
        self.kwargs = kwargs

    def __call__(self) -> R:
        return self.f(*self.args, **self.kwargs)


class Lazy(Generic[P, R]):
    """Lazy version of a given function.
    
    Similar to lazy_evaluation_decorator in multiprocessing.connection ?
    """

    def __init__(self, f:  Callable[P, R], check_inputs: bool = True):
        self._f = f
        self.check_inputs = check_inputs
        if self.check_inputs:
            self._signature = inspect.signature(f)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Callable[[], R]:
        if self.check_inputs:
            check_arguments(signature=self._signature, args=args, kwargs=kwargs)
        return Delayed(self._f, args, kwargs).__call__


def lazy(f:  Callable[P, R], /, check_inputs: bool = True) -> Callable[P, Callable[[], R]]:
    """Lazy version of a given function.

    If `check_inputs` is True then the input arguments and their types are checked as early as possible to fail fast.

    Example:
    >>> l = lazy(print)(5)
    >>> l()
        5    
    """
    return Lazy(f, check_inputs=check_inputs).__call__


def execute_tasks_threads(tasks: Iterable[Callable[[], R]], max_workers: int) -> List[R]:
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(task) for task in tasks]
        results = [future.result() for future in futures]
    return results


def execute_tasks_processes(tasks: Iterable[Callable[[], R]], max_workers: int) -> List[R]:

    pool = multiprocessing.Pool(processes=max_workers)
    futures = [pool.apply_async(task, ()) for task in tasks]
    results = [future.get() for future in futures]
    return results


def tests()->None:
    lazy_f3 = lazy(double)
    delayed3 = lazy_f3(5.0)
    delayed4 = lazy_f3(6.0)
    print(delayed3())

    lazy_f = Lazy(double)
    delayed = lazy_f(5)
    result = delayed()

    lazy_f2 = Lazy(multiply)
    delayed2 = lazy_f2(a=5, b=6)
    result2 = delayed2()
    print(result2)

    tasks = [Lazy(double)(value)for value in [3, 3, 4, 6]]
    results3 = execute_tasks_threads(tasks, max_workers=3)
    results4 = execute_tasks_processes(tasks, max_workers=3)
    print(results4)


if __name__ == "__main__":
    tests()
