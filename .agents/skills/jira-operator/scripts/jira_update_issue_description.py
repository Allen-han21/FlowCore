#!/usr/bin/env python3
"""Update a Jira issue description with an ADF or plain-text source."""

from __future__ import annotations

import argparse
import json
import sys

from jira_auth import JiraClient, JiraError, add_auth_arguments, load_adf_document, resolve_auth_args


def main() -> int:
    parser = argparse.ArgumentParser(description="Update the description field of a Jira issue.")
    add_auth_arguments(parser)
    parser.add_argument("issue_key", help="Issue key such as PK-12345.")
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--adf-file", help="ADF JSON file or markdown file with a fenced json block.")
    source_group.add_argument("--text", help="Plain-text description. Converted into paragraph ADF.")
    source_group.add_argument("--text-file", help="Plain-text file. Converted into paragraph ADF.")
    parser.add_argument("--dry-run", action="store_true", help="Print the update payload without sending it.")
    args = parser.parse_args()

    try:
        description = load_adf_document(
            adf_file=args.adf_file,
            text=args.text,
            text_file=args.text_file,
        )
        payload = {"fields": {"description": description}}
        if args.dry_run:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0

        client = JiraClient(resolve_auth_args(args))
        client.update_issue_fields(args.issue_key, {"description": description})
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
