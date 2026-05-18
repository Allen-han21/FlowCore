#!/usr/bin/env python3
"""Create a Jira issue with API-first workflow."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from jira_auth import JiraClient, JiraError, add_auth_arguments, load_adf_document, resolve_auth_args


def parse_csv(value: str | None) -> list[str] | None:
    if value is None:
        return None
    items = [item.strip() for item in value.split(",") if item.strip()]
    return items if items else []


def resolve_assignee_account_id(client: JiraClient, assignee: str) -> str:
    if "@" not in assignee:
        return assignee

    users = client.request_json(
        "GET",
        "/rest/api/3/user/search",
        params={"query": assignee, "maxResults": 10},
    )
    if not isinstance(users, list) or not users:
        raise JiraError(f"Could not resolve assignee from email: {assignee}")

    exact = next((u for u in users if (u.get("emailAddress") or "").lower() == assignee.lower()), None)
    selected = exact or users[0]
    account_id = selected.get("accountId")
    if not account_id:
        raise JiraError(f"User search result does not contain accountId for assignee: {assignee}")
    return account_id


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a new Jira issue.")
    add_auth_arguments(parser)

    parser.add_argument("--project", required=True, help="Project key, e.g. PK.")
    parser.add_argument("--type", required=True, help="Issue type, e.g. Task, Bug, Story, Sub-task.")
    parser.add_argument("--summary", required=True, help="Issue summary.")

    source_group = parser.add_mutually_exclusive_group()
    source_group.add_argument("--description", help="Plain-text description.")
    source_group.add_argument("--description-file", help="Plain-text description file.")
    source_group.add_argument("--description-adf-file", help="ADF JSON/markdown file for description.")

    parser.add_argument("--assignee", help="Assignee accountId or email.")
    parser.add_argument("--priority", help="Priority name, e.g. High.")
    parser.add_argument("--labels", help="Comma-separated labels.")
    parser.add_argument("--components", help="Comma-separated component names.")
    parser.add_argument("--parent", help="Parent issue key (for sub-task).")

    parser.add_argument("--dry-run", action="store_true", help="Print payload only.")
    parser.add_argument("--raw", action="store_true", help="Print raw create response JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        client = JiraClient(resolve_auth_args(args))

        fields: dict[str, Any] = {
            "project": {"key": args.project},
            "issuetype": {"name": args.type},
            "summary": args.summary,
        }

        if args.description is not None:
            fields["description"] = load_adf_document(text=args.description)
        elif args.description_file is not None:
            fields["description"] = load_adf_document(text_file=args.description_file)
        elif args.description_adf_file is not None:
            fields["description"] = load_adf_document(adf_file=args.description_adf_file)

        if args.assignee:
            fields["assignee"] = {"accountId": resolve_assignee_account_id(client, args.assignee)}

        if args.priority:
            fields["priority"] = {"name": args.priority}

        labels = parse_csv(args.labels)
        if labels is not None:
            fields["labels"] = labels

        components = parse_csv(args.components)
        if components is not None:
            fields["components"] = [{"name": c} for c in components]

        if args.parent:
            fields["parent"] = {"key": args.parent}

        payload = {"fields": fields}
        if args.dry_run:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0

        created = client.create_issue(fields)
    except JiraError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    if args.raw:
        print(json.dumps(created, ensure_ascii=False, indent=2))
    else:
        issue_key = created.get("key") or "-"
        print(json.dumps({
            "issue_key": issue_key,
            "issue_id": created.get("id"),
            "url": f"{client.credentials.base_url}/browse/{issue_key}" if issue_key != "-" else None,
        }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
