#!/usr/bin/env python3
"""Initialize a Stage 3 experiment registry for autonomous-scientific-research."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


HEADER = (
    "run_order\tcampaign\trun_id\tparent_run_id\trole\tchange_axis\tchange_summary\t"
    "scope_version\tstatus\tdecision\tprimary_metric\tprimary_value\tguardrail_summary\t"
    "artifacts\treport_ref\tnotes\n"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a Stage 3 experiment registry with the standard header."
    )
    parser.add_argument(
        "project_root",
        help="Project root that contains or should contain the active report directory.",
    )
    parser.add_argument(
        "--reports-dir",
        default="reports",
        help="Report directory relative to project_root, for example reports or 方法文档.",
    )
    parser.add_argument(
        "--filename",
        default="stage3_experiment_registry.tsv",
        help="Registry filename to create inside the report directory.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing registry file.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).expanduser().resolve()
    reports_dir = project_root / args.reports_dir
    reports_dir.mkdir(parents=True, exist_ok=True)

    registry_path = reports_dir / args.filename
    if registry_path.exists() and not args.force:
        print(f"Registry already exists: {registry_path}", file=sys.stderr)
        return 1

    registry_path.write_text(HEADER, encoding="utf-8")
    print(registry_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
