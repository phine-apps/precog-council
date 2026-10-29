"""CLI entrypoint for Precog Council with rich cyber-aesthetic TUI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Optional

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from precog_council.backends.base import detect_best_backend
from precog_council.config import load_precog_config
from precog_council.council import CouncilVerdict, run_council
from precog_council.domains import get_domain_preset

console = Console()


def render_tui_verdict(verdict: CouncilVerdict) -> None:
    """Render rich visual verdict in terminal."""
    console.print()

    # 1. Header Banner
    header_text = Text()
    header_text.append("🏛️  PRECOG COUNCIL ", style="bold cyan")
    header_text.append("// PRE-CRIME ARBITRATION ENGINE\n", style="bold white")
    header_text.append(f"TOPIC : {verdict.topic}\n", style="yellow")
    header_text.append(f"DOMAIN: {verdict.domain.upper()}", style="dim")

    console.print(Panel(header_text, border_style="cyan", box=box.ROUNDED))

    # 2. Individual Ballots Table
    table = Table(title="🗳️ INDIVIDUAL PRECOG BALLOTS", box=box.HORIZONTALS, header_style="bold magenta")
    table.add_column("Precog", style="bold white")
    table.add_column("Engine", style="dim")
    table.add_column("Analytical Lens", style="cyan")
    table.add_column("Vote", justify="center")
    table.add_column("Confidence", justify="right")

    for r in verdict.results:
        vote_text = Text("🟢 ADOPT", style="bold green") if r.decision == "ADOPT" else Text("🔴 REJECT", style="bold red")
        table.add_row(
            r.name,
            r.model,
            r.role,
            vote_text,
            f"{r.confidence:.0%}"
        )

    console.print(table)
    console.print()

    # 3. Overall Outcome
    if verdict.is_vetoed:
        outcome_color = "red"
        outcome_title = "⛔ VETO OVERRIDE EXERCISED"
        outcome_desc = f"Majority voted ADOPT ({verdict.vote_count.get('ADOPT', 0)} vs {verdict.vote_count.get('REJECT', 0)}), but VETO triggered:\n{verdict.veto_reason}"
    elif verdict.final_decision == "ADOPT":
        outcome_color = "green"
        outcome_title = "🟢 COUNCIL VERDICT: ADOPT"
        outcome_desc = f"Consensus score: {verdict.consensus_score:.1%} | Votes: ADOPT {verdict.vote_count.get('ADOPT', 0)} vs REJECT {verdict.vote_count.get('REJECT', 0)}"
    else:
        outcome_color = "red"
        outcome_title = "🔴 COUNCIL VERDICT: REJECT"
        outcome_desc = f"Consensus score: {verdict.consensus_score:.1%} | Votes: REJECT {verdict.vote_count.get('REJECT', 0)} vs ADOPT {verdict.vote_count.get('ADOPT', 0)}"

    console.print(Panel(outcome_desc, title=f"[{outcome_color}]{outcome_title}[/]", border_style=outcome_color))
    console.print()

    # 4. Minority Report Alert (If split 2 vs 1)
    if verdict.minority_report:
        mr = verdict.minority_report
        alert_body = Text()
        alert_body.append(f"DISSENTING PRECOG: {mr.name} ({mr.role})\n", style="bold yellow")
        alert_body.append(f"MODEL ENGINE    : {mr.model} | CONFIDENCE: {mr.confidence:.0%}\n\n", style="dim")
        alert_body.append("⚠️ CRITICAL RISK WARNINGS:\n", style="bold red")
        for rf in mr.risk_factors:
            alert_body.append(f"  • {rf}\n", style="white")

        alert_body.append(f"\n📝 DISSENT REASONING:\n{mr.reasoning}\n\n", style="italic")
        alert_body.append("👉 ACTION REQUIRED: Do not proceed without evaluating the minority dissent above.", style="bold yellow")

        console.print(Panel(
            alert_body,
            title="[bold red]🚨 MINORITY REPORT DETECTED (2 vs 1 SPLIT) 🚨[/bold red]",
            border_style="bold red",
            box=box.HEAVY
        ))
        console.print()
    elif not verdict.is_vetoed:
        console.print("[dim green]🕊️ Unanimous consensus achieved across all 3 precogs. No minority dissent recorded.[/dim green]\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="precog",
        description="Precog Council: Multi-Model Voting & Minority Report Orchestration"
    )
    parser.add_argument("topic", type=str, help="Topic, feature, or proposal to evaluate")
    parser.add_argument("--context", type=str, default="", help="Inline context, formula, or diff")
    parser.add_argument("--file", "-f", type=str, default=None, help="File containing context or code")
    parser.add_argument(
        "--domain", "-d", type=str, default=None,
        choices=["code", "architecture", "business", "feature", "general"],
        help="Analytical domain preset (default: from precog.yaml or general)"
    )
    parser.add_argument(
        "--backend", "-b", type=str, default=None,
        choices=["auto", "direct", "claude", "agy"],
        help="Model execution backend"
    )
    parser.add_argument("--model", type=str, default=None, help="Unified model for all 3 precogs (Inherit mode)")
    parser.add_argument("--model-a", type=str, default=None, help="Model for Precog Agatha")
    parser.add_argument("--model-b", type=str, default=None, help="Model for Precog Arthur")
    parser.add_argument("--model-c", type=str, default=None, help="Model for Precog Dashiell")
    parser.add_argument("--timeout", type=int, default=None, help="Timeout per precog in seconds")
    parser.add_argument("--format", choices=["rich", "markdown", "json"], default=None, help="Output format")

    args = parser.parse_args()

    # Load configuration cascade
    cfg = load_precog_config()

    domain = args.domain or cfg.domain
    backend_choice = args.backend or cfg.backend
    default_model = args.model or cfg.default_model
    timeout = args.timeout or cfg.timeout
    output_format = args.format or cfg.format

    # Read context
    context = args.context
    if args.file:
        try:
            context = Path(args.file).read_text(encoding="utf-8")
        except Exception as e:
            console.print(f"[bold red]Error reading file {args.file}:[/bold red] {e}", file=sys.stderr)
            sys.exit(1)

    # Resolve domain preset
    preset = get_domain_preset(domain, custom_roles=cfg.precog_roles)

    # Resolve models
    models: Dict[str, str] = {}
    if args.model_a or cfg.model_a:
        models["precog_a"] = args.model_a or cfg.model_a
    if args.model_b or cfg.model_b:
        models["precog_b"] = args.model_b or cfg.model_b
    if args.model_c or cfg.model_c:
        models["precog_c"] = args.model_c or cfg.model_c

    # Resolve backend
    backend = detect_best_backend(backend_choice)

    if output_format == "rich":
        with console.status(f"[bold cyan]Querying the 3 Precogs via {backend.name}...[/bold cyan]", spinner="dots"):
            verdict = run_council(
                topic=args.topic,
                context=context,
                domain_preset=preset,
                backend=backend,
                models=models,
                default_model=default_model,
                veto_roles=cfg.veto_roles,
                timeout=timeout
            )
        render_tui_verdict(verdict)
    else:
        verdict = run_council(
            topic=args.topic,
            context=context,
            domain_preset=preset,
            backend=backend,
            models=models,
            default_model=default_model,
            veto_roles=cfg.veto_roles,
            timeout=timeout
        )
        if output_format == "markdown":
            print(verdict.to_markdown())
        elif output_format == "json":
            print(json.dumps({
                "topic": verdict.topic,
                "domain": verdict.domain,
                "majority_decision": verdict.majority_decision,
                "final_decision": verdict.final_decision,
                "vote_count": verdict.vote_count,
                "is_unanimous": verdict.is_unanimous,
                "is_vetoed": verdict.is_vetoed,
                "veto_reason": verdict.veto_reason,
                "consensus_score": verdict.consensus_score,
                "results": [
                    {
                        "id": r.id,
                        "name": r.name,
                        "model": r.model,
                        "role": r.role,
                        "decision": r.decision,
                        "confidence": r.confidence,
                        "key_points": r.key_points,
                        "risk_factors": r.risk_factors,
                        "reasoning": r.reasoning
                    }
                    for r in verdict.results
                ],
                "minority_report": {
                    "name": verdict.minority_report.name,
                    "model": verdict.minority_report.model,
                    "role": verdict.minority_report.role,
                    "decision": verdict.minority_report.decision,
                    "confidence": verdict.minority_report.confidence,
                    "risk_factors": verdict.minority_report.risk_factors,
                    "reasoning": verdict.minority_report.reasoning
                } if verdict.minority_report else None
            }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
