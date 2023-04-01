"""Postpone module.

Martin de La Gorce. 2023.
"""
__version__ = "0.0.1"

__all__ = [
    "postponed",
    "execute_tasks_threads",
    "execute_tasks_processes",
    "Postponed",
    "Task",
    "check_arguments",
]

from .postponed import (
    postponed,
    execute_tasks_threads,
    execute_tasks_processes,
    Task,
    check_arguments,
)
