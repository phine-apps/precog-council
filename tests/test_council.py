"""Tests for core council voting, aggregation, and veto mechanism."""

from precog_council.council import (
    PrecogResult,
    aggregate_precog_votes,
    parse_model_response,
)


def test_aggregate_unanimous():
    r1 = PrecogResult(id="precog_a", name="Agatha", model="m1", role="Role A", decision="ADOPT", confidence=0.9)
    r2 = PrecogResult(id="precog_b", name="Arthur", model="m2", role="Role B", decision="ADOPT", confidence=0.8)
    r3 = PrecogResult(id="precog_c", name="Dashiell", model="m3", role="Role C", decision="ADOPT", confidence=0.85)

    verdict = aggregate_precog_votes([r1, r2, r3], topic="Test", veto_roles=[])
    assert verdict.majority_decision == "ADOPT"
    assert verdict.is_unanimous is True
    assert verdict.minority_report is None
    assert verdict.is_vetoed is False


def test_aggregate_split_with_minority():
    r1 = PrecogResult(id="precog_a", name="Agatha", model="m1", role="Role A", decision="ADOPT", confidence=0.8)
    r2 = PrecogResult(
        id="precog_b",
        name="Arthur",
        model="m2",
        role="Security Auditor",
        decision="REJECT",
        confidence=0.95,
        risk_factors=["SQL Injection"],
    )
    r3 = PrecogResult(id="precog_c", name="Dashiell", model="m3", role="Role C", decision="ADOPT", confidence=0.7)

    verdict = aggregate_precog_votes([r1, r2, r3], topic="Test", veto_roles=[])
    assert verdict.majority_decision == "ADOPT"
    assert verdict.is_unanimous is False
    assert verdict.minority_report is not None
    assert verdict.minority_report.name == "Arthur"
    assert "SQL Injection" in verdict.minority_report.risk_factors


def test_aggregate_veto_override():
    r1 = PrecogResult(id="precog_a", name="Agatha", model="m1", role="Role A", decision="ADOPT", confidence=0.8)
    r2 = PrecogResult(
        id="precog_b",
        name="Arthur",
        model="m2",
        role="Security Auditor",
        decision="REJECT",
        confidence=0.95,
        risk_factors=["Exploit"],
    )
    r3 = PrecogResult(id="precog_c", name="Dashiell", model="m3", role="Role C", decision="ADOPT", confidence=0.7)

    # Arthur has veto power
    verdict = aggregate_precog_votes([r1, r2, r3], topic="Test", veto_roles=["Security Auditor"])
    assert verdict.is_vetoed is True
    assert verdict.final_decision == "REJECT"  # Overridden by veto!
    assert verdict.majority_decision == "ADOPT"


def test_parse_model_response():
    raw = '```json\n{"decision": "REJECT", "confidence": 0.88, "risk_factors": ["Leak"]}\n```'
    res = parse_model_response(raw, precog_id="a", model_name="m1")
    assert res.decision == "REJECT"
    assert res.confidence == 0.88
    assert "Leak" in res.risk_factors
