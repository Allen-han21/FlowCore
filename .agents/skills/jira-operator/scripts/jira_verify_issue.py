#!/usr/bin/env python3
"""Verify a Jira issue and print a concise summary."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from jira_auth import JiraClient, JiraError, add_auth_arguments, resolve_auth_args

DEFAULT_FIELDS = [
    "summary",
    "status",
    "issuetype",
    "assignee",
    "parent",
    "subtasks",
    "project",
    "updated",
]


def render_summary(issue: dict[str, Any]) -> str:
    fields = issue.get("fields", {})
    assignee = fields.get("assignee") or {}
    parent = fields.get("parent") or {}
    subtasks = fields.get("subtasks") or []
    lines = [
        f"Issue: {issue.get('key')}",
        f"Summary: {fields.get('summary') or '-'}",
        f"Type: {(fields.get('issuetype') or {}).get('name') or '-'}",
        f"Status: {(fields.get('status') or {}).get('name') or '-'}",
        f"Project: {(fields.get('project') or {}).get('key') or '-'}",
        f"Assignee: {assignee.get('displayName') or assignee.get('emailAddress') or '-'}",
        f"Parent: {parent.get('key') or '-'}",
        f"Updated: {fields.get('updated') or '-'}",
    ]
    if subtasks:
        joined = ", ".join(task.get("key", "?") for task in subtasks)
        lines.append(f"Subtasks: {joined}")
    else:
        lines.append("Subtasks: -")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch a Jira issue and print a concise summary.")
    add_auth_arguments(parser)
    parser.add_argument("issue_key", help="Issue key such as PK-12345.")
    parser.add_argument(
        "--fields",
        default=",".join(DEFAULT_FIELDS),
        help="Comma-separated Jira fields to request.",
    )
    parser.add_argument("--raw", action="store_true", help="Print the raw Jira response as JSON.")
    args = parser.parse_args()

    try:
        client = JiraClient(resolve_auth_args(args))
        fields = [item.strip() for item in args.fields.split(",") if item.strip()]
        issue = client.get_issue(args.issue_key, fields=fields)
    except JiraError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    if args.raw:
        print(json.dumps(issue, ensure_ascii=False, indent=2))
    else:
        print(render_summary(issue))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
