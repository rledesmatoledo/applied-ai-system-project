"""Adapter: converts validated task dicts into PawPal Task objects.

The AI layer speaks dicts; the domain layer speaks Tasks. This is the
single bridge between them, so the scheduler never sees raw model output.
"""

import logging
from pawpal_system import Task, Priority, Recurrence

logger = logging.getLogger(__name__)


def dict_to_task(task_dict):
    """Convert one validated dict into a Task. Returns None on failure."""
    try:
        return Task(
            name=task_dict["title"],
            duration=task_dict["duration"],
            priority=Priority(task_dict["priority"]),
            category=task_dict.get("category", "general"),
            recurs=Recurrence(task_dict["recurrence"]),
            time=task_dict["start_time"],
        )
    except (KeyError, ValueError) as e:
        logger.error("Could not build Task from %r: %s", task_dict, e)
        return None


def dicts_to_tasks(task_dicts):
    """Convert a list of validated dicts into Task objects, skipping failures."""
    tasks = [t for t in (dict_to_task(d) for d in task_dicts) if t is not None]
    logger.info("Adapter: built %d Task(s) from %d dict(s)",
                len(tasks), len(task_dicts))
    return tasks
