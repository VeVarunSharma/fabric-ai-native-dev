"""Show Copy Job table mappings that were added, removed, or changed."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, order=True)
class TableMapping:
    """A source-to-destination table mapping."""

    source: str
    destination: str


def extract_mappings(document: Any) -> set[TableMapping]:
    """Extract table mappings from nested Copy Job JSON.

    Fabric definitions can evolve, so this intentionally recognizes common
    source/destination and tableMappings shapes instead of requiring one preview schema.
    """
    mappings: set[TableMapping] = set()

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            source = _table_identifier(node.get("source"))
            destination = _table_identifier(node.get("destination"))
            if source and destination:
                mappings.add(TableMapping(source, destination))

            table_mappings = node.get("tableMappings")
            if isinstance(table_mappings, list):
                for mapping in table_mappings:
                    if isinstance(mapping, dict):
                        source = _table_identifier(
                            mapping.get("source") or mapping.get("sourceTable")
                        )
                        destination = _table_identifier(
                            mapping.get("destination") or mapping.get("destinationTable")
                        )
                        if source and destination:
                            mappings.add(TableMapping(source, destination))
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)

    visit(document)
    return mappings


def compare_mappings(
    before: set[TableMapping],
    after: set[TableMapping],
) -> dict[str, list[TableMapping]]:
    """Return deterministic added and removed mapping lists."""
    return {
        "added": sorted(after - before),
        "removed": sorted(before - after),
    }


def _table_identifier(node: Any) -> str | None:
    if isinstance(node, str):
        return node
    if not isinstance(node, dict):
        return None

    for key in ("table", "tableName", "objectName"):
        value = node.get(key)
        if isinstance(value, str) and value:
            schema = node.get("schema") or node.get("schemaName")
            return f"{schema}.{value}" if isinstance(schema, str) and schema else value

    for key in ("typeProperties", "properties", "datasetSettings"):
        nested = _table_identifier(node.get(key))
        if nested:
            return nested
    return None


def render_diff(diff: dict[str, list[TableMapping]]) -> str:
    lines: list[str] = []
    for label in ("added", "removed"):
        mappings = diff[label]
        lines.append(f"{label.title()} mappings ({len(mappings)}):")
        if mappings:
            lines.extend(
                f"- {mapping.source} -> {mapping.destination}" for mapping in mappings
            )
        else:
            lines.append("- none")
    return "\n".join(lines)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare table mappings in two Copy Job JSON definitions."
    )
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument(
        "--fail-on-removal",
        action="store_true",
        help="Return exit code 2 when a mapping was removed.",
    )
    return parser


def main() -> int:
    args = _parser().parse_args()
    before = extract_mappings(json.loads(args.before.read_text(encoding="utf-8")))
    after = extract_mappings(json.loads(args.after.read_text(encoding="utf-8")))
    diff = compare_mappings(before, after)
    print(render_diff(diff))
    return 2 if args.fail_on_removal and diff["removed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
