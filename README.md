Delayed/Deferred/Lazy function evaluation with static and run-time type checks.

![Python package](https://github.com/martinResearch/postponed/workflows/Python%20package/badge.svg)

# Goal

The goal of the `postponed` package is to provide an interface that allows the user to provide the input arguments to a function but postpone it evaluation to later.
This can be usefull to make parallelization through multithreading or multiprocessing less error-prone
by providing:
* autocompletion when providing the list of argument to the postponed function in you IDE
* optional runtime-check of the input arguments and their types, ahead of the execution in a thread or subprocess in order to fail faster in the main thread if there is an error on the the input arguments.

# Motivation

The common approach to to use multiprocessing to run a function that takes several input arguments over several sub processes is to use `pool.starmap` as done in the following example:

```
import multiprocessing
max_threads=3

def repeat_string(s: str, n: int) -> str:
    return s * n

def test_repeat_string() -> None:
    max_workers = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=max_workers)
    arguments = [("a", 2), ("b", 3)]
    outputs = pool.starmap(repeat_string, arguments)
    print(outputs)

if __name__ == "__main__":
    test_repeat_string()
```

This has several limitations:
* The IDE cannot provide autocompletion and code hints based of the signature of the function `repeat_string` when creating the list `arguments`
which makes it more error prone than normal direct call to `repeat_string`.
* You have to make sure you provide the arguments in the right order (positional arguments) and you cannot use named arguments.
* If one uses a runtime type checker like `typegard` using a decorator `@typechecked` on the function `repeat_string`, then the error will be raised in the subprocess which makes debugging harder.

Note that mypy does raise an error when some of the provided arguments in `arguments` have the wrong type. This is the case when one uses  `arguments = [("a", 2), (2, 3)]`for example.

# Solution

Postpone allows to overcome these two limitations by enabling the IDE to provide useful code hints and by allowing the use of named arguments as illustrated  here:
```
from postponed import postponed, execute_tasks_processes, execute_tasks_threads
def repeat_string(s: str, n: int) -> str:
    return s * n

def test_repeat_string() -> None:
    postponed_repeat_string = postponed(repeat_string, check_inputs=True)
    tasks = [
        postponed_repeat_string(s="a", n=2),
        postponed_repeat_string(s="b", n=3),
        postponed_repeat_string(s="c", n=4),
    ]
    outputs = execute_tasks_processes(tasks=tasks, max_workers=max_workers)

if __name__ == "__main__":
    test_repeat_string()
```

In Visual Studio Code the code hint appears like this:

![image](https://user-images.githubusercontent.com/18285382/229304858-7a292775-120e-4f95-8520-a80a1e70738e.png)

Note that the signature of `postponed_repeat_string`, `(s: str, n: int) -> (() -> str)` is explicit and relatively easy to understand: it returns a callable that take not arguments and return a string.

In addition, by using `check_inputs=True`, one can automatically check at run time that the list of arguments and their type are conform with the function signature. The is done in the main process as early as possible when `postponed_repeat_string` is called by using [typeguard](https://pypi.org/project/typeguard/) under the hood. This allows to catch errors earlier, before the tasks executes on a subprocess which can make the code easier to debug and reduce the duration of the debugging loop.

## Alternatives

* Dask's [delayed decorator](https://dask.pydata.org/en/latest/delayed.html). It soes not perform run-time type checks and requires installing Dask and all its dependencies.
* [lazy python](https://pypi.org/project/lazy_python/). It does not perform run-time type checks and seems unmaintained.
* Joblib's [delayed](https://joblib.readthedocs.io/en/latest/parallel.html). It does not propagate the type information. Using `delayed(repeat_string)(s=1, n="sdf")` with the `repeat_string` defined above does not cause mypy to raise any error and the delayed function signature is displaid as `(*args: Any, **kwargs: Any) -> tuple[Any, tuple, dict[str, Any]]` when doing autocompletion in Visual Studio Code, which is not very useful. There is an [open issue](https://github.com/joblib/joblib/issues/1176) to solve this. 


