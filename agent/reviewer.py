"""Reviewer agent: critiques a proposed task list and flags problems."""

import json
import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-3.5-flash"))

REVIEWER_PROMPT = """You review pet care schedules for practical problems.

Here is a proposed schedule:
{tasks}

Check for issues a simple scheduler would miss:
- Feeding scheduled within 30 minutes after exercise (bloat risk in dogs)
- Two high-priority tasks at the same clock time
- Tasks between 23:00 and 05:00 without clear reason
- Medication doses less than 4 hours apart
- Unrealistic durations for the activity described

Return ONLY a JSON object, no markdown fences:
{{"approved": true or false,
  "issues": ["short description of each problem found"],
  "suggested_fix": "one sentence on what to change, or empty string"}}

If the schedule is sound, return approved true with an empty issues list."""


def review_plan(tasks):
    """Ask the model to critique a task list.

    Returns a verdict dict. On any failure, approves by default so a
    reviewer outage cannot block the user from getting a schedule.
    """
    if not tasks:
        return {"approved": True, "issues": [], "suggested_fix": ""}

    try:
        response = model.generate_content(
            REVIEWER_PROMPT.format(tasks=json.dumps(tasks, indent=2))
        )
        raw = response.text.strip()
    except Exception as e:
        logger.error("Reviewer API call failed: %s", e)
        return {"approved": True, "issues": [], "suggested_fix": "",
                "error": str(e)}

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        verdict = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.error("Reviewer returned unparseable JSON: %s | raw=%r", e, raw[:200])
        return {"approved": True, "issues": [], "suggested_fix": ""}

    if not isinstance(verdict, dict) or "approved" not in verdict:
        logger.error("Reviewer verdict malformed: %r", verdict)
        return {"approved": True, "issues": [], "suggested_fix": ""}

    verdict.setdefault("issues", [])
    verdict.setdefault("suggested_fix", "")

    logger.info("Reviewer: approved=%s, %d issue(s)",
                verdict["approved"], len(verdict["issues"]))
    return verdict