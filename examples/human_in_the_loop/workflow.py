"""
Human-in-the-Loop -- Refund Approval Workflow
================================================

A small, educational example built with the OpenAI Agents SDK's native
human-in-the-loop (HITL) mechanism, as covered in the OpenAI Academy
"Agents and Workflows" course.

The agent receives a refund request and, if it decides to act, proposes
calling an `issue_refund` tool. Because that tool is marked
`needs_approval=True`, the SDK pauses the run *before* the tool executes
and surfaces the pending call as an "interruption". A human then
approves it, or rejects it with a correction, before the run resumes.

Workflow steps this demonstrates:
    1. The agent receives a task
    2. It analyzes the request and produces a proposal (a tool call)
    3. The run pauses and waits for a human decision
    4. A human approves, or rejects with a correction
    5. The run resumes and reflects that decision in the final output

Setup
-----
    pip install openai-agents
    export OPENAI_API_KEY="sk-..."
    python workflow.py

See README.md in this folder for details and expected output.
"""

from __future__ import annotations

import json
import os
import sys

from agents import Agent, Runner, RunState, function_tool
from openai import OpenAIError

# ---------------------------------------------------------------------------
# A tool with real-world consequences -- refunding money -- so it is marked
# `needs_approval=True`. The SDK pauses any run right before this tool runs.
# ---------------------------------------------------------------------------


@function_tool(needs_approval=True)
def issue_refund(order_id: str, amount: float, reason: str) -> str:
    """
    Issue a refund to the customer.

    Args:
        order_id: The order being refunded.
        amount: The refund amount in USD.
        reason: Why the refund is being issued.
    """
    # A real system would call a payments API here. For this educational
    # example we simply report what would happen.
    return f"Refund of ${amount:.2f} for order {order_id} was processed ({reason})."


INSTRUCTIONS = """\
You are a customer support agent. When a refund request looks reasonable
(a legitimate reason, a modest amount), use the issue_refund tool to
process it. Briefly explain your reasoning before acting. If a reviewer
rejects the action with a note, take that note into account and decide
how to proceed.
"""

# A small, inexpensive default model for a fast run.
# Swap for any current OpenAI model your account has access to.
MODEL = "gpt-4o-mini"

TASK = (
    "Customer message: 'Hi, my order #4521 arrived with a cracked case. "
    "Can I get a refund? I paid $85.'\n"
    "Decide whether to issue the refund."
)


def build_agent() -> Agent:
    return Agent(
        name="Support Agent",
        instructions=INSTRUCTIONS,
        model=MODEL,
        tools=[issue_refund],
    )


def describe_pending_calls(state: RunState) -> None:
    """2 & 3. Show the human exactly what the agent is proposing before it runs."""
    for item in state.get_interruptions():
        print("The agent wants to run a tool that requires approval:")
        print(f"  tool:      {item.tool_name}")
        try:
            args = json.loads(item.arguments) if item.arguments else {}
            print(f"  arguments: {json.dumps(args, indent=4)}")
        except (TypeError, ValueError):
            print(f"  arguments: {item.arguments}")


def ask_human_decision() -> tuple[bool, str | None]:
    """4. Collect a human decision: approve, or reject with a correction."""
    while True:
        choice = input("\nApprove this action? [y/n]: ").strip().lower()
        if choice == "y":
            return True, None
        if choice == "n":
            correction = input("Optional reason / correction for the agent: ").strip()
            return False, (correction or "Rejected by reviewer.")
        print("Please answer 'y' or 'n'.")


def main() -> int:
    if not os.environ.get("OPENAI_API_KEY"):
        print(
            "OPENAI_API_KEY is not set. Export it before running this example "
            "(see README.md).",
            file=sys.stderr,
        )
        return 1

    agent = build_agent()

    try:
        # 1. The agent receives the task.
        print(f"Task: {TASK}\n")
        result = Runner.run_sync(agent, TASK)

        # 2 & 3. If the agent proposed the approval-gated tool, the run
        # pauses here instead of finishing.
        if result.interruptions:
            state = result.to_state()
            describe_pending_calls(state)

            approved, note = ask_human_decision()
            for item in state.get_interruptions():
                if approved:
                    state.approve(item)
                else:
                    state.reject(item, rejection_message=note)

            # 5. Resume the run with the human decision applied.
            result = Runner.run_sync(agent, state)

    except OpenAIError as exc:
        print(f"Agent run failed: {exc}", file=sys.stderr)
        return 1

    print("\n=== Final output ===")
    print(result.final_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
