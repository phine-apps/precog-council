"""Domain presets and analytical roles for the Precog Council."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PrecogRoleConfig:
    """Configuration for an individual precog's analytical lens."""
    id: str
    name: str
    role: str
    focus_description: str
    default_model: str = "inherit"


@dataclass
class DomainPreset:
    """Pre-configured council composition for a specific decision domain."""
    name: str
    description: str
    precogs: List[PrecogRoleConfig]


BUILTIN_DOMAINS: Dict[str, DomainPreset] = {
    "code": DomainPreset(
        name="code",
        description="Source code review, refactoring, and algorithm audit",
        precogs=[
            PrecogRoleConfig(
                id="precog_a",
                name="Agatha",
                role="Algorithm & Computational Efficiency",
                focus_description=(
                    "Evaluate computational complexity O(N), memory footprint, concurrency safety, "
                    "algorithmic scalability, and theoretical soundness."
                )
            ),
            PrecogRoleConfig(
                id="precog_b",
                name="Arthur",
                role="Adversarial Security & Robustness Auditor",
                focus_description=(
                    "Hunt for edge cases, null/undefined safety, unhandled exceptions, injection vulnerabilities, "
                    "boundary condition collapses, and silent failure modes."
                )
            ),
            PrecogRoleConfig(
                id="precog_c",
                name="Dashiell",
                role="Occam's Razor & Idiomatic Maintainability",
                focus_description=(
                    "Enforce simplicity, readability, YAGNI (You Aren't Gonna Need It), "
                    "idiomatic patterns, and elimination of unnecessary abstractions."
                )
            ),
        ]
    ),
    "architecture": DomainPreset(
        name="architecture",
        description="System architecture, infrastructure, and technical design decisions",
        precogs=[
            PrecogRoleConfig(
                id="precog_a",
                name="Agatha",
                role="Scalability & Strategic Extensibility",
                focus_description=(
                    "Examine distributed system scalability, API decoupling, future evolution path, "
                    "and long-term architectural leverage."
                )
            ),
            PrecogRoleConfig(
                id="precog_b",
                name="Arthur",
                role="Resilience & Failure Mode Auditor",
                focus_description=(
                    "Audit single points of failure (SPOF), partition tolerance, data inconsistency, "
                    "cascade failure risks, and disaster recovery viability."
                )
            ),
            PrecogRoleConfig(
                id="precog_c",
                name="Dashiell",
                role="Operational Simplicity & Cost Efficiency",
                focus_description=(
                    "Scrutinize operational overhead, cloud resource expenses, deployment complexity, "
                    "and team cognitive load. Fight architectural bloat."
                )
            ),
        ]
    ),
    "business": DomainPreset(
        name="business",
        description="Business strategy, product feature prioritization, and commercial trade-offs",
        precogs=[
            PrecogRoleConfig(
                id="precog_a",
                name="Agatha",
                role="Market Opportunity & Upside Maximizer",
                focus_description=(
                    "Assess market size, competitive moat, revenue potential, differentiation, "
                    "and viral growth vectors."
                )
            ),
            PrecogRoleConfig(
                id="precog_b",
                name="Arthur",
                role="Downside Risk & Compliance Sentinel",
                focus_description=(
                    "Audit legal/regulatory compliance, financial downside exposure, reputation risks, "
                    "customer churn potential, and competitor retaliation."
                )
            ),
            PrecogRoleConfig(
                id="precog_c",
                name="Dashiell",
                role="Lean Pragmatism & Execution Velocity",
                focus_description=(
                    "Evaluate speed to market, minimum viable scope, resource constraints, "
                    "and fast validation loops. Strip vanity features."
                )
            ),
        ]
    ),
    "feature": DomainPreset(
        name="feature",
        description="Quantitative trading features, alpha signals, and financial time-series indicators",
        precogs=[
            PrecogRoleConfig(
                id="precog_a",
                name="Agatha",
                role="Mathematical & Causal Reasoning",
                focus_description=(
                    "Inspect market microstructure physics, volatility dynamics, nonlinear causality, "
                    "and scale-invariant mathematical foundations."
                )
            ),
            PrecogRoleConfig(
                id="precog_b",
                name="Arthur",
                role="Adversarial Risk & Leakage Auditor",
                focus_description=(
                    "Hunt for forward-looking leakage (shift(1) violations), lookahead bias, regime fragility, "
                    "spread/slippage friction sensitivity, and boundary collapse."
                )
            ),
            PrecogRoleConfig(
                id="precog_c",
                name="Dashiell",
                role="Occam's Razor & Noise Filter",
                focus_description=(
                    "Verify parsimony, numerical conditioning, intuitive interpretability, and rejection "
                    "of noise overfitting or trivial indicator relabeling."
                )
            ),
        ]
    ),
    "general": DomainPreset(
        name="general",
        description="General multi-perspective decision making and trade-off evaluation",
        precogs=[
            PrecogRoleConfig(
                id="precog_a",
                name="Agatha",
                role="Structural & Strategic Visionary",
                focus_description="Examine structural coherence, strategic leverage, and positive ripple effects."
            ),
            PrecogRoleConfig(
                id="precog_b",
                name="Arthur",
                role="Devil's Advocate & Risk Auditor",
                focus_description="Hunt for hidden assumptions, worst-case consequences, and unacknowledged risks."
            ),
            PrecogRoleConfig(
                id="precog_c",
                name="Dashiell",
                role="Pragmatic Realist & Minimalist",
                focus_description="Enforce Occam's razor, cost-benefit realism, and immediate actionable clarity."
            ),
        ]
    ),
}


def get_domain_preset(
    domain: str,
    custom_roles: Optional[Dict[str, str]] = None
) -> DomainPreset:
    """Retrieve domain preset by name or construct custom council configuration."""
    domain_key = domain.lower()
    if domain_key in BUILTIN_DOMAINS and not custom_roles:
        return BUILTIN_DOMAINS[domain_key]

    base = BUILTIN_DOMAINS.get(domain_key, BUILTIN_DOMAINS["general"])
    if not custom_roles:
        return base

    precogs = []
    for p in base.precogs:
        # Match by ID or name
        override_role = (
            custom_roles.get(p.id)
            or custom_roles.get(p.name.lower())
            or custom_roles.get(p.name)
            or p.role
        )
        precogs.append(
            PrecogRoleConfig(
                id=p.id,
                name=p.name,
                role=override_role,
                focus_description=f"Evaluate proposal strictly under: {override_role}"
            )
        )

    return DomainPreset(
        name=domain,
        description=f"Customized council for {domain}",
        precogs=precogs
    )
