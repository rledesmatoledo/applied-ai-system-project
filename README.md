# PawPal+ Applied AI System

Type out your pet's day in a sentence and get back a checked, scheduled plan.

## What this started as

This builds on **PawPal+**, my Module 2 project, which was a pet care scheduler
using a greedy priority algorithm. It took `Task` objects, fit them into an
available time budget in priority order, flagged conflicts, and explained its
reasoning in plain English.

The problem was the input. You had to fill out a form for every single task:
name, duration, priority dropdown, time picker. For someone scheduling six
things a day that is a lot of clicking. So I put an agentic layer in front of it.

## What it does now

You type:

> Feed Coco twice a day, walk her at 5pm for half an hour, vet Tuesday at 2

The system pulls structured tasks out of that, checks them against a schema,
runs a second AI pass to look for practical problems, re-plans once if it finds
any, and only then hands everything to the scheduler I already had.

## How it's put together

Diagram source is in `diagrams/architecture.mmd`.

**Planner** (`agent/planner.py`) sends your sentence to Gemini with the schema
and rules, and gets JSON back.

**Validator** (`agent/validator.py`) is plain Python with no AI. It checks every
field and rejects anything malformed with a reason.

**Reviewer** (`agent/reviewer.py`) is a second Gemini call that critiques the
plan. It catches things the scheduler structurally cannot, like feeding a dog
right after a walk.

**Adapter** (`agent/adapter.py`) turns validated dicts into PawPal `Task`
objects. It is the only place that conversion happens.

**Orchestrator** (`agent/orchestrator.py`) runs the loop, retries once when the
Reviewer objects, and logs every step to `logs/agent_trace.jsonl`.


## Running it

```bash
git clone https://github.com/rledesmatoledo/applied-ai-system-project.git
cd applied-ai-system-project
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install google-generativeai python-dotenv
```

Make a `.env` in the project root:

```
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-3.5-flash
```

Then:

```bash
python3 main.py
```

## Sample runs

Full traces for both of these are in `logs/agent_trace.jsonl`.

### The retry loop catching itself

Input:

> Feed Coco twice a day, walk her at 5pm for half an hour, vet Tuesday at 2

The Reviewer rejected the first plan:

```json
{
  "approved": false,
  "issues": ["Evening feeding is scheduled at 18:00, which is exactly 30 minutes after the evening walk ends (17:30), posing a bloat risk."],
  "suggested_fix": "Delay the evening feeding to 18:30 or later."
}
```

Second attempt moved feeding to 19:30 and passed:

```
attempts: 2
approved: True
Scheduled 4 of 4 task(s) in priority order, using 120 of 480 available minutes.
14:00  Vet appointment   60 min  high
08:00  Morning feeding   15 min  medium
19:30  Evening feeding   15 min  medium
17:00  Evening walk      30 min  medium
```

### Guardrails rejecting bad output

Validator run against six deliberately broken tasks:

```
Validator: 1 accepted, 5 rejected
  duration must be a positive integer
  invalid priority: 'urgent'
  invalid start_time: '25:99'
  missing keys: duration, priority, recurrence, start_time
  not a dictionary
```

Nothing crashed, and every rejection came back with a reason.

## Testing

All 22 original PawPal+ tests still pass with the AI layer on top:

```
$ pytest tests/ -q
...................... [100%]
22 passed in 0.02s
```

The Validator checks above are in `manual_validator_check.py`. Both sample
inputs were rejected on the first attempt and approved on the second.

## What I learned

The big one is that making something reliable is about where you draw the lines,
not how good your prompt is. My Planner prompt is pretty detailed and it still
sent back bad data. What made this work is that nothing from the model reaches
code I already tested without going through a check first.
