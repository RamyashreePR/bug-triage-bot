import os
from anthropic import Anthropic
from pydantic import BaseModel, Field
from typing import Literal
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()


class TriageResult(BaseModel):
    quality_score: int = Field(ge=0, le=100, description="0-100 completeness score based on the rubric")
    severity: Literal["critical", "high", "medium", "low"]
    category: Literal["ui", "backend", "database", "auth", "performance", "integration", "other"]
    missing_fields: list[str] = Field(description="List of missing items, e.g. 'reproduction steps', 'environment'")
    suggested_owner: str = Field(description="Team or role best suited to handle this, e.g. 'Backend team', 'DevOps'")
    rewritten_title: str = Field(description="A clearer, action-oriented version of the bug title")
    improvement_suggestions: list[str] = Field(description="Concrete suggestions to improve the report")
    is_likely_duplicate_indicator: bool = Field(description="True if vague wording suggests this may duplicate existing bugs")


SYSTEM_PROMPT = """You are a senior QA lead triaging incoming bug reports.
Score reports against this rubric (total 100 points):
- Clear, descriptive title (10 points)
- Reproduction steps (25 points)
- Expected vs actual behaviour (20 points)
- Environment details: OS, browser, version (15 points)
- Severity indication by reporter (10 points)
- Screenshots, logs, or error messages mentioned (10 points)
- User impact described (10 points)

Be strict. A vague one-liner like 'app crashes' should score under 20.

IMPORTANT routing rules:
- For suggested_owner: ALWAYS provide a concrete team suggestion based on 
  the most likely component, even when information is sparse. Use your best 
  judgment. Never return placeholder values like UNKNOWN, N/A, or empty 
  strings. When the report is too vague to identify a specific owner, 
  suggest 'Triage team for clarification' so the report gets routed to 
  someone who can investigate further.
- For category: ALWAYS pick the most likely category. Default to 'other' 
  only when no other category fits.
- For rewritten_title: ALWAYS produce a clearer version, even for vague 
  reports - inferring the most likely intent from context."""


def triage(bug_report: str) -> TriageResult:
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        tools=[{
            "name": "submit_triage",
            "description": "Submit the structured triage analysis for the bug report",
            "input_schema": TriageResult.model_json_schema(),
        }],
        tool_choice={"type": "tool", "name": "submit_triage"},
        messages=[{"role": "user", "content": f"Triage this bug report:\n\n{bug_report}"}],
    )
    tool_use = next(block for block in response.content if block.type == "tool_use")
    return TriageResult(**tool_use.input)


if __name__ == "__main__":
    import sys
    from rich.console import Console
    from rich.panel import Panel

    console = Console()

    if not sys.stdin.isatty():
        bug = sys.stdin.read()
    else:
        console.print("[bold]Paste your bug report below. Press Enter twice when done:[/bold]")
        lines = []
        empty_count = 0
        while empty_count < 1:
            line = input()
            if line == "":
                empty_count += 1
            else:
                empty_count = 0
            lines.append(line)
        bug = "\n".join(lines).strip()

    if not bug:
        console.print("[red]No bug report provided.[/red]")
        sys.exit(1)

    with console.status("[cyan]Triaging with Claude...[/cyan]"):
        result = triage(bug)

    suggestions_text = "\n".join(f"  - {s}" for s in result.improvement_suggestions)
    missing_text = ", ".join(result.missing_fields) if result.missing_fields else "nothing"

    console.print(Panel.fit(
        f"[bold]Quality score:[/bold] {result.quality_score}/100\n"
        f"[bold]Severity:[/bold] {result.severity}\n"
        f"[bold]Category:[/bold] {result.category}\n"
        f"[bold]Suggested owner:[/bold] {result.suggested_owner}\n"
        f"[bold]Rewritten title:[/bold] {result.rewritten_title}\n\n"
        f"[bold]Missing fields:[/bold] {missing_text}\n"
        f"[bold]Suggestions:[/bold]\n{suggestions_text}",
        title="Triage Result",
        border_style="cyan",
    ))