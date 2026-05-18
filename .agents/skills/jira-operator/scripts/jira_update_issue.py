#!/usr/bin/env python3
"""Update Jira issue fields with API-first workflow."""

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
    parser = argparse.ArgumentParser(description="Update Jira issue fields.")
    add_auth_arguments(parser)

    parser.add_argument("issue_key", help="Issue key such as PK-12345.")
    parser.add_argument("--summary", help="New summary.")

    source_group = parser.add_mutually_exclusive_group()
    source_group.add_argument("--description", help="Plain-text description.")
    source_group.add_argument("--description-file", help="Plain-text description file.")
    source_group.add_argument("--description-adf-file", help="ADF JSON/markdown file for description.")
    parser.add_argument("--clear-description", action="store_true", help="Clear description field.")

    parser.add_argument("--assignee", help="Assignee accountId/email. Empty string unassigns.")
    parser.add_argument("--priority", help="Priority name.")
    parser.add_argument("--labels", help="Comma-separated labels.")
    parser.add_argument("--components", help="Comma-separated component names.")

    parser.add_argument("--dry-run", action="store_true", help="Print payload only.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.clear_description and any([args.description, args.description_file, args.description_adf_file]):
        print("[ERROR] --clear-description cannot be used with description source options.", file=sys.stderr)
        return 1

    try:
        client = JiraClient(resolve_auth_args(args))
        fields: dict[str, Any] = {}

        if args.summary is not None:
            fields["summary"] = args.summary

        if args.clear_description:
            fields["description"] = None
        elif args.description is not None:
            fields["description"] = load_adf_document(text=args.description)
        elif args.description_file is not None:
            fields["description"] = load_adf_document(text_file=args.description_file)
        elif args.description_adf_file is not None:
            fields["description"] = load_adf_document(adf_file=args.description_adf_file)

        if args.assignee is not None:
            if args.assignee == "":
                fields["assignee"] = None
            else:
                fields["assignee"] = {"accountId": resolve_assignee_account_id(client, args.assignee)}

        if args.priority is not None:
            fields["priority"] = {"name": args.priority}

        labels = parse_csv(args.labels)
        if labels is not None:
            fields["labels"] = labels

        components = parse_csv(args.components)
        if components is not None:
            fields["components"] = [{"name": c} for c in components]

        if not fields:
            raise JiraError("No update fields provided.")

        payload = {"fields": fields}
        if args.dry_run:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0

        client.update_issue_fields(args.issue_key, fields)
        issue = client.get_issue(args.issue_key, fields=["summary", "updated"])
    except JiraError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    print(json.dumps(
        {
            "issue_key": args.issue_key,
            "summary": issue.get("fields", {}).get("summary"),
            "updated": issue.get("fields", {}).get("updated"),
        },
        ensure_ascii=False,
        indent=2,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
