import logging
from agent.planner import plan_tasks

logging.basicConfig(level=logging.INFO)

result = plan_tasks(
    "Feed Coco twice a day, walk her at 5pm for half an hour, "
    "and she has a vet appointment Tuesday at 2"
)

for t in result:
    print(t)
