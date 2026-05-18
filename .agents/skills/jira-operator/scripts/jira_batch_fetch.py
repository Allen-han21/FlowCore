#!/usr/bin/env python3
"""Fetch multiple Jira issues in one authenticated process."""

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


def adf_to_text(node: Any) -> str:
    if node is None:
        return ""
    if isinstance(node, list):
        return "".join(adf_to_text(item) for item in node)
    if not isinstance(node, dict):
        return ""
    node_type = node.get("type")
    if node_type == "text":
        return node.get("text", "")
    if node_type == "hardBreak":
        return "\n"
    if node_type in {"paragraph", "heading"}:
        return adf_to_text(node.get("content", [])) + "\n"
    if node_type in {"bulletList", "orderedList"}:
        lines = []
        for item in node.get("content", []):
            text = adf_to_text(item).strip()
            if text:
                lines.append(f"- {text}")
        return "\n".join(lines) + ("\n" if lines else "")
    if node_type == "listItem":
        return "".join(adf_to_text(item) for item in node.get("content", []))
    if node_type == "codeBlock":
        return "```\n" + adf_to_text(node.get("content", [])) + "\n```\n"
    if node_type == "table":
        rows = []
        for row in node.get("content", []):
            rows.append(" | ".join(adf_to_text(cell).strip() for cell in row.get("content", [])))
        return "\n".join(rows) + ("\n" if rows else "")
    return "".join(adf_to_text(item) for item in node.get("content", []))


def render_issue(issue: dict[str, Any], *, description_chars: int = 0) -> str:
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
        lines.append("Subtasks: " + ", ".join(task.get("key", "?") for task in subtasks))
    else:
        lines.append("Subtasks: -")

    if description_chars > 0:
        text = adf_to_text(fields.get("description")).strip()
        if text:
            snippet = text[:description_chars]
            lines.append("Description:")
            lines.append(snippet)
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch multiple Jira issues in one authenticated batch process."
    )
    add_auth_arguments(parser)
    parser.add_argument("issue_keys", nargs="+", help="Issue keys such as PK-12345 PK-12346.")
    parser.add_argument(
        "--fields",
        default=",".join(DEFAULT_FIELDS),
        help="Comma-separated Jira fields to request.",
    )
    parser.add_argument(
        "--with-description",
        action="store_true",
        help="Include a description snippet converted from ADF.",
    )
    parser.add_argument(
        "--description-chars",
        type=int,
        default=1200,
        help="Description snippet length when --with-description is used.",
    )
    parser.add_argument("--raw", action="store_true", help="Print raw JSON objects.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        client = JiraClient(resolve_auth_args(args))
        fields = [item.strip() for item in args.fields.split(",") if item.strip()]
        if args.with_description and "description" not in fields:
            fields.append("description")
    except JiraError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    issues = []
    try:
        for issue_key in args.issue_keys:
            issues.append(client.get_issue(issue_key, fields=fields))
    except JiraError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    if args.raw:
        print(json.dumps(issues, ensure_ascii=False, indent=2))
        return 0

    rendered = [
        render_issue(
            issue,
            description_chars=args.description_chars if args.with_description else 0,
        )
        for issue in issues
    ]
    print("\n\n".join(rendered))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
