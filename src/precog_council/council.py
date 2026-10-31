"""Precog Council core: Independent prompt building, response parsing, and verdict aggregation."""

from __future__ import annotations

import concurrent.futures
import json
import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from precog_council.backends.base import BaseBackend
from precog_council.domains import DomainPreset, PrecogRoleConfig

logger = logging.getLogger("precog_council.council")


@dataclass
class PrecogResult:
    """Individual ballot and analysis from a single precog."""

    id: str
    name: str
    model: str
    role: str
    decision: str  # "ADOPT" or "REJECT"
    confidence: float  # 0.0 to 1.0
    key_points: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    reasoning: str = ""
    raw_response: str = ""


@dataclass
class CouncilVerdict:
    """Final synthesis and report from the Precog Council."""

    topic: str
    domain: str
    majority_decision: str
    final_decision: str
    vote_count: Dict[str, int]
    is_unanimous: bool
    is_vetoed: bool
    veto_reason: Optional[str]
    results: List[PrecogResult]
    minority_report: Optional[PrecogResult] = None
    consensus_score: float = 0.0

    def to_markdown(self) -> str:
        """Render a clean GitHub Flavored Markdown report."""
        unanimous_badge = (
            "🕊️ **Unanimous Consensus (3 vs 0)**" if self.is_unanimous else "⚖️ **Majority Consensus (2 vs 1 Split)**"
        )
        decision_badge = "🟢 **ADOPT**" if self.final_decision == "ADOPT" else "🔴 **REJECT**"

        md = [
            "# 🏛️ Precog Council Evaluation Report",
            "",
            f"**Topic**: {self.topic}",
            f"**Domain**: `{self.domain}`",
            "",
            "### 1. Council Verdict",
            f"* **Final Decision**: {decision_badge}" + (" ⚠️ *(VETO Override Exercised)*" if self.is_vetoed else ""),
            f"* **Consensus State**: {unanimous_badge} (ADOPT: {self.vote_count.get('ADOPT', 0)} / REJECT: {self.vote_count.get('REJECT', 0)})",
            f"* **Consensus Confidence**: {self.consensus_score:.1%}",
            "",
            "### 2. Individual Ballots",
            "| Precog | Engine | Analytical Lens | Decision | Confidence |",
            "| :--- | :--- | :--- | :---: | :---: |",
        ]

        for r in self.results:
            icon = "🟢 ADOPT" if r.decision == "ADOPT" else "🔴 REJECT"
            md.append(f"| **{r.name}** | `{r.model}` | {r.role} | {icon} | {r.confidence:.0%} |")

        md.append("")
        md.append("### 3. Detailed Precog Findings")
        for r in self.results:
            md.append(f"#### 👁️ {r.name} ({r.role})")
            md.append(f"* **Decision**: `{r.decision}` (Confidence: {r.confidence:.0%})")
            if r.key_points:
                md.append("* **Key Strengths & Rationale**:")
                for p in r.key_points:
                    md.append(f"  - {p}")
            if r.risk_factors:
                md.append("* **Risk Factors & Failure Modes**:")
                for rf in r.risk_factors:
                    md.append(f"  - {rf}")
            md.append(f"* **Detailed Reasoning**: {r.reasoning}")
            md.append("")

        if self.is_vetoed and self.veto_reason:
            md.append("---")
            md.append("## ⛔ VETO Override Exercised")
            md.append("> [!CAUTION] **VETO power exercised by designated role**")
            md.append(
                f"> Majority voted `{self.majority_decision}`, but {self.veto_reason} overrode the final decision to `REJECT`."
            )
            md.append("")

        if self.minority_report:
            mr = self.minority_report
            md.append("---")
            md.append("## 🚨 【CRITICAL】 Minority Report Detected")
            md.append(f"> [!WARNING] **Dissenting Precog: {mr.name} (`{mr.model}`)**")
            md.append(
                f"> While the majority (2 precogs) concluded `{self.majority_decision}`, {mr.name} dissented with `{mr.decision}` (Confidence: {mr.confidence:.0%})."
            )
            md.append(
                "> In mission-critical systems, systemic failures and fatal blind spots often reside within minority dissent."
            )
            md.append("")
            md.append("### ⚠️ Critical Risk Warnings from Dissenting Precog:")
            for rf in mr.risk_factors:
                md.append(f"1. **{rf}**")
            md.append("")
            md.append("### 📝 Dissenting Reasoning:")
            md.append(f"> {mr.reasoning}")
            md.append("")
            md.append(
                "**👉 Action Required**: Before proceeding, evaluate counter-evidence or mitigations against the minority dissent warnings above."
            )
        elif not self.is_vetoed:
            md.append("---")
            md.append("## 🕊️ Unanimous Consensus")
            md.append(
                "All three precogs reached identical conclusions. Potential for overlooked edge cases or hidden blind spots is estimated to be minimal."
            )

        return "\n".join(md)


def parse_model_response(raw_text: str, precog_id: str = "", model_name: str = "") -> PrecogResult:
    """Parse JSON or structured text response into PrecogResult."""
    clean_text = raw_text.strip()
    json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", clean_text, re.DOTALL)
    if json_match:
        payload_str = json_match.group(1)
    else:
        brace_match = re.search(r"(\{.*\})", clean_text, re.DOTALL)
        payload_str = brace_match.group(1) if brace_match else ""

    if payload_str:
        try:
            data = json.loads(payload_str)
            decision = str(data.get("decision", "REJECT")).upper()
            if decision not in ["ADOPT", "REJECT"]:
                decision = "ADOPT" if any(w in decision for w in ["ADOPT", "YES", "APPROVE", "PASS"]) else "REJECT"

            confidence = float(data.get("confidence", 0.70))
            confidence = max(0.0, min(1.0, confidence))

            return PrecogResult(
                id=precog_id,
                name="",
                model=model_name,
                role="",
                decision=decision,
                confidence=confidence,
                key_points=data.get("key_points", []) or [],
                risk_factors=data.get("risk_factors", []) or [],
                reasoning=data.get("reasoning", data.get("summary", "")),
                raw_response=clean_text,
            )
        except Exception:
            pass

    # Fallback heuristic: Fail-Safe parsing
    decision = "REJECT"

    # 1. Check for explicit negative keywords first
    has_negative_keywords = bool(
        re.search(
            r"\b(REJECT|DISAPPROVE|DENY|VETO|DISAGREE|見送り|却下|否決|反対|不採用|不合格)\b",
            clean_text,
            re.IGNORECASE,
        )
    )

    # 2. Check for negated positive expressions (e.g., "do not adopt", "cannot approve")
    has_negated_approval = bool(
        re.search(
            r"\b(NOT|DON'?T|CANNOT|CAN'?T|SHOULDN'?T|WON'?T|NEVER|NO)\s+(ADOPT|APPROVE|PASS|ACCEPT|RECOMMEND)\b",
            clean_text,
            re.IGNORECASE,
        )
    )

    # 3. Only adopt if explicitly positive and NOT negated
    if not has_negative_keywords and not has_negated_approval:
        if re.search(r"\b(ADOPT|APPROVE|YES|採用|合格|推奨)\b", clean_text, re.IGNORECASE):
            decision = "ADOPT"

    conf_match = re.search(r"confidence[^\d]*([0-1]?\.\d+)", clean_text, re.IGNORECASE)
    confidence = float(conf_match.group(1)) if conf_match else 0.70

    return PrecogResult(
        id=precog_id,
        name="",
        model=model_name,
        role="",
        decision=decision,
        confidence=confidence,
        key_points=[],
        risk_factors=[],
        reasoning=clean_text[:500],
        raw_response=clean_text,
    )


def build_precog_prompt(topic: str, context: str, domain: str, precog: PrecogRoleConfig) -> str:
    """Construct an independent, role-specialized prompt for a single precog."""
    return f"""You are **{precog.name}**, one of the three Precognitives (Precogs) of the Precog Council.
Your role: **{precog.role}**

You must independently and objectively evaluate the following proposal without bias.
Do not assume what other precogs will say. Focus 100% on your specific analytical lens.

---
### 📋 EVALUATION PROPOSAL
* **Domain**: {domain}
* **Topic**: {topic}
* **Context / Code / Specification**:
{context}

---
### 🎯 YOUR SPECIALIZED ANALYTICAL FOCUS
As {precog.name} ({precog.role}):
{precog.focus_description}

---
### 📤 REQUIRED JSON OUTPUT FORMAT
Respond ONLY with a valid JSON block enclosed in ```json ... ```:
```json
{{
  "decision": "ADOPT" or "REJECT",
  "confidence": 0.85,
  "key_points": [
    "Key rationale point 1",
    "Key rationale point 2"
  ],
  "risk_factors": [
    "Specific potential risk or failure mode 1",
    "Specific potential risk or failure mode 2"
  ],
  "reasoning": "A concise paragraph explaining your final verdict from your role's perspective."
}}
```
"""


def aggregate_precog_votes(
    results: List[PrecogResult], topic: str, domain: str = "general", veto_roles: Optional[List[str]] = None
) -> CouncilVerdict:
    """Aggregate ballots into a CouncilVerdict, isolating minority reports and enforcing vetoes."""
    veto_roles = veto_roles or []
    votes: Dict[str, int] = {"ADOPT": 0, "REJECT": 0}
    for r in results:
        votes[r.decision] = votes.get(r.decision, 0) + 1

    majority_decision = "ADOPT" if votes["ADOPT"] > votes["REJECT"] else "REJECT"
    is_unanimous = (votes["ADOPT"] == len(results)) or (votes["REJECT"] == len(results))

    minority_report: Optional[PrecogResult] = None
    if not is_unanimous:
        for r in results:
            if r.decision != majority_decision:
                minority_report = r
                break

    # Veto check
    is_vetoed = False
    veto_reason = None
    if majority_decision == "ADOPT" and veto_roles:
        for r in results:
            if r.decision == "REJECT" and any(v.lower() in r.role.lower() for v in veto_roles):
                is_vetoed = True
                veto_reason = f"Role '{r.role}' ({r.name}) rejected with risk: {', '.join(r.risk_factors[:2]) or r.reasoning[:100]}"
                break

    final_decision = "REJECT" if is_vetoed else majority_decision

    majority_confs = [r.confidence for r in results if r.decision == majority_decision]
    consensus_score = sum(majority_confs) / len(majority_confs) if majority_confs else 0.5

    return CouncilVerdict(
        topic=topic,
        domain=domain,
        majority_decision=majority_decision,
        final_decision=final_decision,
        vote_count=votes,
        is_unanimous=is_unanimous,
        is_vetoed=is_vetoed,
        veto_reason=veto_reason,
        results=results,
        minority_report=minority_report,
        consensus_score=consensus_score,
    )


def run_council(
    topic: str,
    context: str,
    domain_preset: DomainPreset,
    backend: BaseBackend,
    models: Optional[Dict[str, str]] = None,
    default_model: str = "inherit",
    veto_roles: Optional[List[str]] = None,
    timeout: int = 90,
) -> CouncilVerdict:
    """Run all 3 precogs in parallel via backend and aggregate verdict."""
    models = models or {}
    results: List[PrecogResult] = []

    def _query_precog(p: PrecogRoleConfig) -> PrecogResult:
        model = models.get(p.id) or models.get(p.name.lower()) or default_model
        prompt = build_precog_prompt(topic, context, domain_preset.name, p)
        try:
            raw_text = backend.query(model, prompt, timeout=timeout)
            res = parse_model_response(raw_text, precog_id=p.id, model_name=model)
            res.name = p.name
            res.role = p.role
            return res
        except Exception as e:
            logger.error("Failed to query precog %s (%s): %s", p.name, model, e)
            return PrecogResult(
                id=p.id,
                name=p.name,
                model=model,
                role=p.role,
                decision="REJECT",
                confidence=0.50,
                risk_factors=[f"Query error: {e}"],
                reasoning=f"Failed to obtain response: {e}",
            )

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(_query_precog, p): p for p in domain_preset.precogs}
        for f in concurrent.futures.as_completed(futures):
            results.append(f.result())

    results.sort(key=lambda r: r.id)
    return aggregate_precog_votes(results=results, topic=topic, domain=domain_preset.name, veto_roles=veto_roles)
