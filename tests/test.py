
from postponed import postponed, execute_tasks_threads, execute_tasks_processes

def doubed(v: float)->float:
    return 2 * v


def tests()->None:
    postponed_double = postponed(double)
    task = postponed_double(5.0)
    print(task())

    tasks = [postponed(double)(value)for value in [3, 3, 4, 6]]
    results_multihtread = execute_tasks_threads(tasks, max_workers=3)
    results_multiprocess = execute_tasks_processes(tasks, max_workers=3)
    assert results_multihtread == [6, 6, 8, 12]
    assert results_multiprocess == [6, 6, 8, 12]


if __name__ == "__main__":
    tests()
