# Example 1 — Agent Workflow

A small, runnable example of a single-agent workflow built with the
[OpenAI Agents SDK](https://openai.github.io/openai-agents-python/).

## What This Demonstrates

The full lifecycle of directing an AI agent through a structured task —
the central idea behind the **Agents and Workflows** course:

1. **Objective** — a clearly defined goal in the agent's instructions.
2. **Context** — raw input (sample meeting notes) provided to the agent.
3. **Instructions & constraints** — explicit rules the output must follow
   (max sentence count, max number of items, no invented details).
4. **Execution** — the agent runs the task via `Runner.run_sync`.
5. **Validation** — the result is programmatically re-checked against
   the stated constraints, instead of being trusted blindly.
6. **Structured output** — the agent's response is enforced to match a
   Pydantic schema (`output_type`), not free-form text.

## How It Works

`workflow.py` defines a `MeetingBrief` schema (summary, action items,
open questions), gives the agent instructions with explicit constraints,
runs it against a sample block of meeting notes, and then validates the
returned object against those same constraints before printing it.

## Requirements

- Python 3.10+
- An [OpenAI API key](https://platform.openai.com/api-keys)
- The `openai-agents` package:

  ```bash
  pip install openai-agents
  ```

## How to Run

```bash
export OPENAI_API_KEY="sk-..."   # never hardcode this
python workflow.py
```

## Example Usage

The script runs with a built-in sample set of meeting notes — no input
files or arguments needed. To try it on your own notes, replace the
`SAMPLE_MEETING_NOTES` constant at the top of `workflow.py`.

## What to Expect

Illustrative output (exact wording will vary by model run):

```
=== Meeting Brief ===
Summary: The team reviewed the certificate repository and the Agents
SDK approval flow. Two tasks remain unassigned.

Action items:
  - Add a practical examples section to the certificate repo (owner: Lazaro, due: Friday)
  - Assign an owner for the new "Getting Started" docs page (owner: unspecified, due: unspecified)

Open questions:
  - Is a custom timeout needed for pending tool approvals?

=== Validation ===
Validation passed: output respects the stated constraints.
```

If the model's output ever breaks a constraint (e.g. too many action
items), the script reports exactly which check failed instead of
silently accepting the result.

---

*Educational / portfolio demonstration — not an official OpenAI implementation.*
