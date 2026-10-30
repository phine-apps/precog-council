"""Tests for CLI arguments and strict mode exit code."""

from unittest.mock import patch

import pytest

from precog_council.cli import main
from precog_council.council import CouncilVerdict


def test_cli_strict_mode_exit_code_on_reject():
    dummy_verdict = CouncilVerdict(
        topic="Test",
        domain="code",
        majority_decision="REJECT",
        final_decision="REJECT",
        vote_count={"ADOPT": 0, "REJECT": 3},
        is_unanimous=True,
        is_vetoed=False,
        veto_reason=None,
        results=[],
        consensus_score=0.9,
    )

    with patch("sys.argv", ["precog", "Test Topic", "--strict", "--format", "json"]):
        with patch("precog_council.cli.run_council", return_value=dummy_verdict):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1


def test_cli_normal_mode_exit_code_zero_on_reject():
    dummy_verdict = CouncilVerdict(
        topic="Test",
        domain="code",
        majority_decision="REJECT",
        final_decision="REJECT",
        vote_count={"ADOPT": 0, "REJECT": 3},
        is_unanimous=True,
        is_vetoed=False,
        veto_reason=None,
        results=[],
        consensus_score=0.9,
    )

    with patch("sys.argv", ["precog", "Test Topic", "--format", "json"]):
        with patch("precog_council.cli.run_council", return_value=dummy_verdict):
            # Should not raise SystemExit
            main()
