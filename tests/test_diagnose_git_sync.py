from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from scripts.diagnose_git_sync import analyze_status

FIXTURES = Path(__file__).parent / "fixtures"


def _fixture(name: str) -> dict[str, object]:
    return cast(
        dict[str, object],
        json.loads((FIXTURES / name).read_text(encoding="utf-8")),
    )


def test_synced_status_requires_no_action() -> None:
    analysis = analyze_status(_fixture("git_status_synced.json"))

    assert analysis["categories"] == {}
    assert analysis["nextStep"].startswith("No action required")


def test_independent_changes_are_not_reported_as_conflict() -> None:
    analysis = analyze_status(_fixture("git_status_mixed.json"))

    assert "conflict" not in analysis["categories"]
    assert len(analysis["categories"]["workspace-only"]) == 1
    assert len(analysis["categories"]["remote-only"]) == 1
    assert "independent changes" in analysis["nextStep"]


def test_same_item_change_stops_for_review() -> None:
    analysis = analyze_status(_fixture("git_status_conflict.json"))

    assert len(analysis["categories"]["conflict"]) == 1
    assert analysis["nextStep"].startswith("Stop and review")
