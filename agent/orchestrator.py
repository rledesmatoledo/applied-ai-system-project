"""Orchestrator: runs the full plan -> validate -> review -> retry loop."""

import json
import logging
import os
from datetime import datetime

from agent.planner import plan_tasks
from agent.validator import validate_tasks
from agent.reviewer import review_plan
from agent.adapter import dicts_to_tasks
from pawpal_system import Scheduler

logger = logging.getLogger(__name__)

TRACE_PATH = os.path.join("logs", "agent_trace.jsonl")
MAX_RETRIES = 1


def _trace(step, payload):
    """Append one reasoning step to the trace log."""
    os.makedirs("logs", exist_ok=True)
    entry = {"timestamp": datetime.now().isoformat(), "step": step,
             "payload": payload}
    try:
        with open(TRACE_PATH, "a") as f:
            f.write(json.dumps(entry, default=str) + "\n")
    except OSError as e:
        logger.error("Could not write trace: %s", e)


def run(user_input, available_time=480):
    """Run the full agentic pipeline. Always returns a result dict."""
    _trace("input", {"user_input": user_input})

    attempt = 0
    feedback = ""
    accepted, rejected, verdict = [], [], {}

    while attempt <= MAX_RETRIES:
        prompt_input = user_input
        if feedback:
            prompt_input = (user_input +
                            "\n\nA previous attempt had this problem: " +
                            feedback + " Avoid it this time.")

        raw = plan_tasks(prompt_input)
        _trace("planner", {"attempt": attempt, "tasks": raw})

        accepted, rejected = validate_tasks(raw)
        _trace("validator", {"attempt": attempt,
                             "accepted": len(accepted),
                             "rejected": [r for _, r in rejected]})

        if not accepted:
            _trace("halt", {"reason": "no valid tasks after validation"})
            return {"tasks": [], "plan": None, "verdict": {},
                    "rejected": rejected, "attempts": attempt + 1}

        verdict = review_plan(accepted)
        _trace("reviewer", {"attempt": attempt, "verdict": verdict})

        if verdict.get("approved", True):
            break

        feedback = " ".join(verdict.get("issues", []))
        attempt += 1

    tasks = dicts_to_tasks(accepted)
    plan = Scheduler().generate_plan(tasks, available_time)
    _trace("scheduler", {"reasoning": plan.reasoning,
                         "scheduled": len(plan.scheduled_tasks),
                         "deferred": len(plan.deferred_tasks)})

    return {"tasks": tasks, "plan": plan, "verdict": verdict,
            "rejected": rejected, "attempts": attempt + 1}
