import logging
from agent.validator import validate_tasks

logging.basicConfig(level=logging.INFO)

bad_tasks = [
    {"title": "Walk", "pet": "Coco", "duration": 30, "priority": "high",
     "start_time": "17:00", "recurrence": "daily"},
    {"title": "Feed", "pet": "Coco", "duration": -5, "priority": "high",
     "start_time": "08:00", "recurrence": "daily"},
    {"title": "Vet", "pet": "Coco", "duration": 60, "priority": "urgent",
     "start_time": "14:00", "recurrence": "none"},
    {"title": "Nap", "pet": "Coco", "duration": 20, "priority": "low",
     "start_time": "25:99", "recurrence": "none"},
    {"title": "Groom", "pet": "Coco"},
    "not even a dict",
]

accepted, rejections = validate_tasks(bad_tasks)
print("\nACCEPTED:", len(accepted))
for t in accepted:
    print("  ", t)
print("\nREJECTED:", len(rejections))
for t, reason in rejections:
    print("  ", reason)
