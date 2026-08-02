"""Validator: schema and guardrail checks on planner output. No AI involved."""

import logging

logger = logging.getLogger(__name__)

REQUIRED_KEYS = {"title", "pet", "duration", "priority", "start_time", "recurrence"}
VALID_PRIORITIES = {"high", "medium", "low"}
VALID_RECURRENCE = {"none", "daily", "weekly"}
MAX_DURATION = 480


def _valid_time(value):
    if not isinstance(value, str) or ":" not in value:
        return False
    parts = value.split(":")
    if len(parts) != 2:
        return False
    try:
        hour, minute = int(parts[0]), int(parts[1])
    except ValueError:
        return False
    return 0 <= hour <= 23 and 0 <= minute <= 59


def validate_tasks(tasks):
    """Split planner output into (accepted, rejections)."""
    accepted, rejections = [], []

    if not isinstance(tasks, list):
        logger.error("Validator got %s, expected list", type(tasks).__name__)
        return [], [(tasks, "input was not a list")]

    for task in tasks:
        if not isinstance(task, dict):
            rejections.append((task, "not a dictionary"))
            continue

        missing = REQUIRED_KEYS - task.keys()
        if missing:
            rejections.append((task, "missing keys: " + ", ".join(sorted(missing))))
            continue

        if not isinstance(task["duration"], int) or task["duration"] <= 0:
            rejections.append((task, "duration must be a positive integer"))
            continue

        if task["duration"] > MAX_DURATION:
            rejections.append((task, "duration exceeds %d minutes" % MAX_DURATION))
            continue

        if task["priority"] not in VALID_PRIORITIES:
            rejections.append((task, "invalid priority: %r" % task["priority"]))
            continue

        if task["recurrence"] not in VALID_RECURRENCE:
            rejections.append((task, "invalid recurrence: %r" % task["recurrence"]))
            continue

        if not _valid_time(task["start_time"]):
            rejections.append((task, "invalid start_time: %r" % task["start_time"]))
            continue

        if not str(task["title"]).strip() or not str(task["pet"]).strip():
            rejections.append((task, "title and pet cannot be empty"))
            continue

        accepted.append(task)

    logger.info("Validator: %d accepted, %d rejected", len(accepted), len(rejections))
    for task, reason in rejections:
        logger.warning("Rejected task: %s", reason)

    return accepted, rejections
