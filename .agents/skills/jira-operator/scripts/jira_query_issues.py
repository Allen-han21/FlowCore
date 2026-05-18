#!/usr/bin/env python3
"""Query Jira issues with JQL or typed filters."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from jira_auth import JiraClient, JiraError, add_auth_arguments, resolve_auth_args

DEFAULT_FIELDS = [
    "summary",
    "status",
    "assignee",
    "priority",
    "issuetype",
    "updated",
]


class JQLQueryBuilder:
    def __init__(self) -> None:
        self.conditions: list[str] = []
        self.order: tuple[str, str] | None = None

    def project(self, key: str) -> "JQLQueryBuilder":
        self.conditions.append(f"project = {key}")
        return self

    def assignee(self, value: str) -> "JQLQueryBuilder":
        if value.lower() == "me":
            self.conditions.append("assignee = currentUser()")
        else:
            self.conditions.append(f'assignee = "{value}"')
        return self

    def status(self, value: str) -> "JQLQueryBuilder":
        self.conditions.append(f'status = "{value}"')
        return self

    def priority(self, value: str) -> "JQLQueryBuilder":
        self.conditions.append(f'priority = "{value}"')
        return self

    def issue_type(self, value: str) -> "JQLQueryBuilder":
        self.conditions.append(f'type = "{value}"')
        return self

    def component(self, value: str) -> "JQLQueryBuilder":
        self.conditions.append(f'component = "{value}"')
        return self

    def label(self, value: str) -> "JQLQueryBuilder":
        self.conditions.append(f'labels = "{value}"')
        return self

    def parent(self, key: str) -> "JQLQueryBuilder":
        self.conditions.append(f"parent = {key}")
        return self

    def period(self, field: str, days: int) -> "JQLQueryBuilder":
        self.conditions.append(f"{field} >= -{days}d")
        return self

    def order_by(self, field: str, direction: str) -> "JQLQueryBuilder":
        self.order = (field, direction)
        return self

    def build(self) -> str:
        if not self.conditions:
            return ""
        jql = " AND ".join(self.conditions)
        if self.order:
            jql += f" ORDER BY {self.order[0]} {self.order[1]}"
        return jql


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query Jira issues with JQL or typed filters.")
    add_auth_arguments(parser)

    parser.add_argument("--jql", help="Raw JQL query.")
    parser.add_argument("--days", type=int, help="Filter by period: field >= -Nd.")
    parser.add_argument(
        "--field",
        default="updated",
        choices=["updated", "created", "resolved"],
        help="Time field used with --days.",
    )
    parser.add_argument("--project", help="Project key filter.")
    parser.add_argument("--assignee", help="Assignee email or 'me'.")
    parser.add_argument("--status", help="Status filter.")
    parser.add_argument("--priority", help="Priority filter.")
    parser.add_argument("--type", dest="issue_type", help="Issue type filter.")
    parser.add_argument("--component", help="Component filter.")
    parser.add_argument("--label", help="Label filter.")
    parser.add_argument("--parent", help="Parent issue key filter.")
    parser.add_argument("--order-by", default="updated", help="Order by field.")
    parser.add_argument("--order-dir", default="DESC", choices=["ASC", "DESC"], help="Order direction.")

    parser.add_argument("--limit", type=int, default=20, help="Max results to return.")
    parser.add_argument("--start-at", type=int, default=0, help="Pagination offset.")
    parser.add_argument("--fields", default=",".join(DEFAULT_FIELDS), help="Comma-separated Jira fields.")
    parser.add_argument("--raw", action="store_true", help="Print raw JSON response.")
    return parser.parse_args()


def build_jql(args: argparse.Namespace) -> str:
    if args.jql:
        return args.jql

    builder = JQLQueryBuilder()
    if args.project:
        builder.project(args.project)
    if args.assignee:
        builder.assignee(args.assignee)
    if args.status:
        builder.status(args.status)
    if args.priority:
        builder.priority(args.priority)
    if args.issue_type:
        builder.issue_type(args.issue_type)
    if args.component:
        builder.component(args.component)
    if args.label:
        builder.label(args.label)
    if args.parent:
        builder.parent(args.parent)
    if args.days is not None:
        builder.period(args.field, args.days)
    builder.order_by(args.order_by, args.order_dir)
    return builder.build()


def print_human(payload: dict[str, Any]) -> None:
    issues = payload.get("issues", [])
    total = payload.get("total", 0)
    print(f"Total: {total}, Showing: {len(issues)}")
    for issue in issues:
        fields = issue.get("fields", {})
        key = issue.get("key", "-")
        summary = fields.get("summary", "-")
        status = (fields.get("status") or {}).get("name", "-")
        assignee_obj = fields.get("assignee") or {}
        assignee = assignee_obj.get("displayName") or assignee_obj.get("emailAddress") or "Unassigned"
        priority = (fields.get("priority") or {}).get("name", "-")
        print(f"{key:<12} {status:<15} {priority:<8} {assignee:<20} {summary}")


def main() -> int:
    args = parse_args()

    try:
        jql = build_jql(args)
        if not jql:
            raise JiraError("Provide --jql or at least one typed filter option.")

        client = JiraClient(resolve_auth_args(args))
        fields = [item.strip() for item in args.fields.split(",") if item.strip()]

        payload: dict[str, Any] = {
            "jql": jql,
            "maxResults": min(max(args.limit, 1), 100),
            "fields": fields,
        }
        if args.start_at > 0:
            payload["startAt"] = args.start_at

        result = client.request_json("POST", "/rest/api/3/search/jql", payload=payload)
    except JiraError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    if args.raw:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"JQL: {jql}")
        print_human(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
