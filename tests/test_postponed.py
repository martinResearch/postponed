"""Test for the postponed module"""
import multiprocessing

from postponed import execute_tasks_processes, execute_tasks_threads, postponed


def multiply(a: float, b: float) -> float:
    return a * b


def repeat_string(s: str, n: int) -> str:
    return s * n


def tests() -> None:
    postponed_multiply = postponed(multiply)
    tasks = [postponed_multiply(a=1.0, b=2.0), postponed_multiply(a=3.0, b=4.0)]

    max_workers = 3
    pool = multiprocessing.Pool(processes=max_workers)
    futures = [pool.apply_async(task, ()) for task in tasks]
    results = [future.get() for future in futures]
    assert results == [2.0, 12.0]

    results = execute_tasks_processes(tasks=tasks, max_workers=max_workers)
    assert results == [2.0, 12.0]

    results = execute_tasks_threads(tasks=tasks, max_workers=max_workers)
    assert results == [2.0, 12.0]


def test_repeat_string() -> None:
    max_workers = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=max_workers)
    arguments = [("a", 2), ("b", 3)]
    outputs = pool.starmap(repeat_string, arguments)
    print(outputs)
    assert outputs == ["aa", "bbb"]

    # mypy does raise an error when the first argument
    # is a int and not a string in each tuple
    # arguments = [(2, 2), (2, 3)]
    # outputs = pool.starmap(repeat_string, arguments)
    # print(outputs)

    postponed_repeat_string = postponed(repeat_string, check_inputs=True)
    tasks = [
        postponed_repeat_string(s="a", n=2),
        postponed_repeat_string(s="b", n=3),
        postponed_repeat_string(s="c", n=4),
    ]
    outputs = execute_tasks_processes(tasks=tasks, max_workers=max_workers)
    assert outputs == ["aa", "bbb", "cccc"]


if __name__ == "__main__":
    tests()
