#!/usr/bin/env python3
"""Add a comment to a Jira issue."""

from __future__ import annotations

import argparse
import json
import sys

from jira_auth import JiraClient, JiraError, add_auth_arguments, load_adf_document, resolve_auth_args


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Add a Jira issue comment.")
    add_auth_arguments(parser)
    parser.add_argument("issue_key", help="Issue key such as PK-12345.")

    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--text", help="Plain-text comment.")
    source_group.add_argument("--text-file", help="Plain-text comment file.")
    source_group.add_argument("--adf-file", help="ADF JSON/markdown file for comment body.")

    parser.add_argument("--dry-run", action="store_true", help="Print payload without sending it.")
    parser.add_argument("--raw", action="store_true", help="Print raw comment create response.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        client = JiraClient(resolve_auth_args(args))
        body = load_adf_document(adf_file=args.adf_file, text=args.text, text_file=args.text_file)
        payload = {"body": body}

        if args.dry_run:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0

        result = client.request_json("POST", f"/rest/api/3/issue/{args.issue_key}/comment", payload=payload)
    except JiraError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    if args.raw:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(
            {
                "issue_key": args.issue_key,
                "comment_id": result.get("id"),
                "created": result.get("created"),
            },
            ensure_ascii=False,
            indent=2,
        ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
