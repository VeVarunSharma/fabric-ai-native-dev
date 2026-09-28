from __future__ import annotations

import json
from pathlib import Path

from scripts.validate_copy_job_diff import TableMapping, compare_mappings, extract_mappings

FIXTURES = Path(__file__).parent / "fixtures"


def _fixture(name: str) -> object:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_copy_job_diff_exposes_added_and_removed_tables() -> None:
    before = extract_mappings(_fixture("copy_job_before.json"))
    after = extract_mappings(_fixture("copy_job_after.json"))

    diff = compare_mappings(before, after)

    assert diff["added"] == [TableMapping("sales.Customers", "bronze.Customers")]
    assert diff["removed"] == [
        TableMapping("sales.LegacyCustomers", "bronze.LegacyCustomers")
    ]
