"""
Agent Workflow -- Meeting Notes to Structured Action Items
============================================================

A small, educational example built with the OpenAI Agents SDK that
demonstrates the core lifecycle of an agent-driven workflow, as covered
in the OpenAI Academy "Agents and Workflows" course:

    1. Defining a clear objective
    2. Providing relevant input context
    3. Setting instructions and constraints
    4. Executing the task
    5. Validating the result
    6. Producing structured output

The agent reads a block of raw meeting notes and turns them into a
structured brief: a short summary, a bounded list of action items, and
any open questions. The output shape is enforced by the SDK via
`output_type`, and the result is re-checked against the constraints
stated in the agent's own instructions before being accepted.

Setup
-----
    pip install openai-agents
    export OPENAI_API_KEY="sk-..."
    python workflow.py

See README.md in this folder for details and expected output.
"""

from __future__ import annotations

import os
import sys

from agents import Agent, Runner
from openai import OpenAIError
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# 6. Structured output -- the shape the agent must return.
# ---------------------------------------------------------------------------


class ActionItem(BaseModel):
    """A single action item extracted from the notes."""

    description: str = Field(description="What needs to be done.")
    owner: str = Field(description="Who is responsible, or 'unspecified'.")
    due_date: str = Field(description="Due date if mentioned, or 'unspecified'.")


class MeetingBrief(BaseModel):
    """The structured result the agent must produce."""

    summary: str = Field(description="A short summary of the meeting, max 3 sentences.")
    action_items: list[ActionItem]
    open_questions: list[str] = Field(
        default_factory=list,
        description="Anything left unresolved or unclear in the notes.",
    )


# ---------------------------------------------------------------------------
# 1 & 3. Objective, instructions, and constraints.
# ---------------------------------------------------------------------------

INSTRUCTIONS = """\
You are a project assistant that turns raw meeting notes into a structured
brief for the team.

Constraints:
- The summary must be no more than 3 sentences.
- List at most 6 action items. If there are more candidates, keep the
  6 most important ones.
- For each action item, fill in the owner and due date only if the notes
  state them clearly. Otherwise use the literal string "unspecified" --
  never invent a name or a date.
- Only include an open question if the notes leave something genuinely
  ambiguous or undecided.
"""

# A small, inexpensive default model for a fast run.
# Swap for any current OpenAI model your account has access to.
MODEL = "gpt-4o-mini"

# ---------------------------------------------------------------------------
# 2. Context -- the raw input the agent has to work with.
# ---------------------------------------------------------------------------

SAMPLE_MEETING_NOTES = """\
Weekly sync - Aug 11

- Reviewed the certificate repository. Lazaro will add a practical
  examples section by Friday.
- Discussed the OpenAI Agents SDK approval flow for sensitive tools.
  Still unclear whether a custom timeout is needed for pending approvals.
- The docs site needs a new "Getting Started" page. No owner assigned yet.
- Everyone agreed the current README structure works well and should
  not change for now.
"""


def build_agent() -> Agent:
    """Assemble the agent from its objective, instructions, and output shape."""
    return Agent(
        name="Meeting Brief Assistant",
        instructions=INSTRUCTIONS,
        model=MODEL,
        output_type=MeetingBrief,
    )


def validate_brief(brief: MeetingBrief) -> list[str]:
    """
    4 & 5. An explicit validation step.

    Re-checks the constraints declared in the instructions instead of
    trusting the model output blindly. Returns a list of problems; an
    empty list means the result passed validation.
    """
    problems: list[str] = []

    if len(brief.action_items) > 6:
        problems.append(f"Expected at most 6 action items, got {len(brief.action_items)}.")

    if brief.summary.count(".") > 3:
        problems.append("Summary looks longer than the 3-sentence constraint.")

    for item in brief.action_items:
        if not item.description.strip():
            problems.append("Found an action item with an empty description.")

    return problems


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
        # 4. Execute the task with the given context.
        result = Runner.run_sync(agent, SAMPLE_MEETING_NOTES)
    except OpenAIError as exc:
        print(f"Agent run failed: {exc}", file=sys.stderr)
        return 1

    brief = result.final_output_as(MeetingBrief, raise_if_incorrect_type=True)

    # 5. Validate before treating the output as trustworthy.
    problems = validate_brief(brief)

    print("=== Meeting Brief ===")
    print(f"Summary: {brief.summary}\n")

    print("Action items:")
    for item in brief.action_items:
        print(f"  - {item.description} (owner: {item.owner}, due: {item.due_date})")

    if brief.open_questions:
        print("\nOpen questions:")
        for question in brief.open_questions:
            print(f"  - {question}")

    print("\n=== Validation ===")
    if problems:
        print("Validation FAILED:")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    print("Validation passed: output respects the stated constraints.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
