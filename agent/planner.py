"""Planner agent: turns natural language into structured task dicts."""

import json
import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-3.5-flash")

PLANNER_PROMPT = """You convert pet care requests into structured tasks.

Return ONLY a JSON array. No markdown fences, no explanation.

Each object must have exactly these keys:
- "title": short string, e.g. "Morning walk"
- "pet": the pet's name as a string
- "duration": integer minutes
- "priority": one of "high", "medium", "low"
- "start_time": 24-hour "HH:MM" string
- "recurrence": one of "none", "daily", "weekly"

Rules:
- Medication and vet appointments are always "high" priority.
- If no time is given, pick a sensible one for that activity.
- If no duration is given, estimate a realistic one.
- If the request mentions something twice a day, emit two separate tasks.

Request: {user_input}"""


def plan_tasks(user_input):
    """Turn user_input into a list of task dicts.

    Returns [] on any failure; the Validator handles empties downstream.
    """
    if not user_input or not user_input.strip():
        logger.warning("Planner received empty input")
        return []

    try:
        response = model.generate_content(
            PLANNER_PROMPT.format(user_input=user_input)
        )
        raw = response.text.strip()
    except Exception as e:
        logger.error("Planner API call failed: %s", e)
        return []

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        tasks = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.error("Planner returned unparseable JSON: %s | raw=%r", e, raw[:200])
        return []

    if not isinstance(tasks, list):
        logger.error("Planner returned %s, expected list", type(tasks).__name__)
        return []

    logger.info("Planner produced %d task(s)", len(tasks))
    return tasks
