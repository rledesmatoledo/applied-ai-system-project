# Model Card: PawPal+ Applied AI System

## What this is

A scheduling assistant that takes a normal sentence about your pet's day and
turns it into a checked, planned out schedule. It uses Gemini 3.5 Flash on top
of the scheduler I built for PawPal+ in Module 2.

## Working with AI

I used Claude to help me design this and debug it.

**Something it got right.** Claude said the Validator should be its own piece
with no AI in it. I thought that was not helpful since I already tell the
Planner what the rules are in the prompt. I was wrong. While testing, the
Planner sent back a priority of "urgent". That sounds fine but it is not one of
the three options my code allows, so it would have crashed later in a spot where
the error would have been hard to read. The Validator caught it right away and
told me what was wrong.

**Something it got wrong.** Claude told me to use gemini-2.0-flash, then
gemini-2.5-flash. Neither one worked. The 2.0 models were shut off in June 2026
and 2.5-flash is not open to new accounts. Claude said both with total
confidence. 