# Example 2 — Human-in-the-Loop

A small, runnable example of pausing an agent for human approval, built
with the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)'s
native human-in-the-loop (HITL) mechanism.

## What This Demonstrates

Human oversight of agent-driven actions — a core theme of the
**Agents and Workflows** course:

1. **The agent receives a task** — a customer refund request.
2. **It analyzes the request and produces a proposal** — deciding to
   call an `issue_refund` tool with specific arguments.
3. **The workflow pauses** — because the tool is marked
   `needs_approval=True`, the SDK halts the run *before* the tool
   executes and surfaces it as an "interruption".
4. **A human reviews and decides** — approve, or reject with a
   correction, from the terminal.
5. **The workflow resumes** — reflecting that decision in the final
   output.

## How It Works

`workflow.py` defines one tool, `issue_refund`, marked
`needs_approval=True`. When the agent decides to call it,
`Runner.run_sync` returns a result with a non-empty `.interruptions`
list instead of a final answer. The script converts that result to a
`RunState`, prints the pending tool call for review, asks for a
`y`/`n` decision (plus an optional correction if rejected), applies it
with `state.approve(...)` / `state.reject(...)`, and resumes the run
by passing the updated state back into `Runner.run_sync`.

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

The script will pause and prompt you interactively in the terminal
when the agent proposes the refund.

## Example Usage

No arguments needed — the task (a sample refund request) is built into
the script. To experiment, edit the `TASK` constant at the top of
`workflow.py`.

## What to Expect

Illustrative session (exact wording will vary by model run):

```
Task: Customer message: 'Hi, my order #4521 arrived with a cracked
case. Can I get a refund? I paid $85.' Decide whether to issue the refund.

The agent wants to run a tool that requires approval:
  tool:      issue_refund
  arguments: {
    "order_id": "4521",
    "amount": 85.0,
    "reason": "item arrived damaged"
  }

Approve this action? [y/n]: y

=== Final output ===
I've processed the refund. Refund of $85.00 for order 4521 was
processed (item arrived damaged).
```

Answering `n` instead prompts for a correction (e.g. "confirm the
order first"), which is fed back to the agent so it can adjust its
next step rather than blindly retrying.

---

*Educational / portfolio demonstration — not an official OpenAI implementation.*
