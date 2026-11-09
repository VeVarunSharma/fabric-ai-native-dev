"""Execute the self-contained Fabric notebook without a Spark dependency."""

import json
import runpy
from pathlib import Path
from uuid import UUID

NOTEBOOK_DIRECTORY = (
    Path(__file__).resolve().parents[1] / "workspace" / "QuickCiDemo.Notebook"
)


def test_notebook_sales_summary() -> None:
    result = runpy.run_path(str(NOTEBOOK_DIRECTORY / "notebook-content.py"))

    assert result["summary"] == {
        "input_rows": 5,
        "valid_rows": 4,
        "rejected_rows": 1,
        "total_revenue_cents": 26000,
    }
    assert result["revenue_by_region"] == {"North": 15500, "South": 10500}
    assert result["rejected_orders"] == [
        {"order_id": 5, "region": "North", "amount_cents": -500}
    ]


def test_notebook_platform_metadata() -> None:
    platform = json.loads((NOTEBOOK_DIRECTORY / ".platform").read_text(encoding="utf-8"))

    assert platform["metadata"]["type"] == "Notebook"
    assert platform["metadata"]["displayName"] == "QuickCiDemo"
    assert platform["config"]["version"] == "2.0"
    assert str(UUID(platform["config"]["logicalId"])) == platform["config"]["logicalId"]
