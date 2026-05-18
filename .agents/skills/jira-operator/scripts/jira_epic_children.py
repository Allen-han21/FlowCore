#!/usr/bin/env python3
"""Get an Epic and its child issues."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from jira_auth import JiraClient, JiraError, add_auth_arguments, resolve_auth_args

DEFAULT_EPIC_FIELDS = ["summary", "status", "issuetype", "updated", "project"]
DEFAULT_CHILD_FIELDS = ["summary", "status", "assignee", "priority", "updated"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch epic and child issues.")
    add_auth_arguments(parser)
    parser.add_argument("epic_key", help="Epic key such as PK-30299.")
    parser.add_argument("--limit", type=int, default=100, help="Max child issues.")
    parser.add_argument("--raw", action="store_true", help="Print raw JSON.")
    return parser.parse_args()


def print_human(epic: dict[str, Any], children: list[dict[str, Any]], total: int) -> None:
    fields = epic.get("fields", {})
    print(f"Epic: {epic.get('key')}")
    print(f"Summary: {fields.get('summary') or '-'}")
    print(f"Status: {(fields.get('status') or {}).get('name') or '-'}")
    print(f"Updated: {fields.get('updated') or '-'}")
    print(f"Children: {len(children)} / Total: {total}")
    print()

    for child in children:
        cfields = child.get("fields", {})
        assignee_obj = cfields.get("assignee") or {}
        assignee = assignee_obj.get("displayName") or assignee_obj.get("emailAddress") or "Unassigned"
        status = (cfields.get("status") or {}).get("name") or "-"
        priority = (cfields.get("priority") or {}).get("name") or "-"
        summary = cfields.get("summary") or "-"
        print(f"{child.get('key', '-'):<12} {status:<15} {priority:<8} {assignee:<20} {summary}")


def main() -> int:
    args = parse_args()

    try:
        client = JiraClient(resolve_auth_args(args))
        epic = client.get_issue(args.epic_key, fields=DEFAULT_EPIC_FIELDS)

        payload: dict[str, Any] = {
            "jql": f"parent = {args.epic_key}",
            "maxResults": min(max(args.limit, 1), 100),
            "fields": DEFAULT_CHILD_FIELDS,
        }
        search = client.request_json("POST", "/rest/api/3/search/jql", payload=payload)
        children = search.get("issues", [])
        total = search.get("total", len(children))
    except JiraError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    if args.raw:
        print(json.dumps({"epic": epic, "children": children, "total_children": total}, ensure_ascii=False, indent=2))
    else:
        print_human(epic, children, total)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
