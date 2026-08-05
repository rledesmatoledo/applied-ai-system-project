import logging
from agent.planner import plan_tasks
from agent.validator import validate_tasks
from agent.adapter import dicts_to_tasks
from agent.reviewer import review_plan
from pawpal_system import Scheduler

logging.basicConfig(level=logging.INFO)

user_input = ("Feed Coco twice a day, walk her at 5pm for half an hour, "
              "and she has a vet appointment Tuesday at 2")

raw = plan_tasks(user_input)
accepted, rejected = validate_tasks(raw)
verdict = review_plan(accepted)
tasks = dicts_to_tasks(accepted)

plan = Scheduler().generate_plan(tasks, available_time=480)

print("\n--- REVIEWER ---")
print("approved:", verdict["approved"])
for i in verdict["issues"]:
    print("  issue:", i)

print("\n--- PLAN ---")
print(plan.reasoning)
for t in plan.scheduled_tasks:
    print("  ", t.time, t.name, t.duration, "min", t.priority.value)
