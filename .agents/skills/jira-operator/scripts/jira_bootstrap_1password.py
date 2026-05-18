#!/usr/bin/env python3
"""Prepare a safe Jira 1Password bootstrap without revealing secrets."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from jira_1password import DEFAULT_ITEM, DEFAULT_VAULT, build_bootstrap_summary, resolve_item, write_env_file
from jira_auth import JiraError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resolve Jira secret references from 1Password and optionally write an env file for op run."
    )
    parser.add_argument("--account", help="1Password account selector for op CLI.")
    parser.add_argument("--vault", default=DEFAULT_VAULT, help="1Password vault name.")
    parser.add_argument("--item", default=DEFAULT_ITEM, help="1Password item title.")
    parser.add_argument("--base-url", help="Explicit Jira base URL override.")
    parser.add_argument("--write-env-file", help="Write a dotenv file containing safe secret references.")
    parser.add_argument("--json", action="store_true", help="Print bootstrap summary as JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        item = resolve_item(
            vault_name=args.vault,
            item_name=args.item,
            base_url=args.base_url,
            account=args.account,
        )
    except JiraError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    summary = build_bootstrap_summary(item)
    if args.write_env_file:
        path = write_env_file(Path(args.write_env_file).expanduser(), item)
        summary["env_file"] = str(path)

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0

    print(f"vault: {summary['vault']}")
    print(f"item: {summary['item']}")
    print(f"base_url: {summary['base_url']}")
    if summary.get("env_file"):
        print(f"env_file: {summary['env_file']}")
    print("capabilities:")
    for key, value in summary["capabilities"].items():
        print(f"- {key}: {str(value).lower()}")
    print("recommended_flow:")
    for line in summary["recommended_flow"]:
        print(f"- {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
