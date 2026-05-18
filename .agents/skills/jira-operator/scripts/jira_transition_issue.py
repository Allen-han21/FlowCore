#!/usr/bin/env python3
"""Transition Jira issue status by transition name."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from jira_auth import JiraClient, JiraError, add_auth_arguments, load_adf_document, resolve_auth_args


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Transition Jira issue status.")
    add_auth_arguments(parser)
    parser.add_argument("issue_key", help="Issue key such as PK-12345.")
    parser.add_argument("--status", help="Target transition name, e.g. In Progress, Done.")
    parser.add_argument("--list", action="store_true", help="List available transitions and exit.")

    source_group = parser.add_mutually_exclusive_group()
    source_group.add_argument("--comment", help="Optional comment while transitioning.")
    source_group.add_argument("--comment-file", help="Plain-text comment file.")
    source_group.add_argument("--comment-adf-file", help="ADF JSON/markdown comment file.")

    parser.add_argument("--dry-run", action="store_true", help="Print transition payload only.")
    return parser.parse_args()


def find_transition_id(transitions: list[dict[str, Any]], status_name: str) -> str | None:
    lowered = status_name.lower()
    for trans in transitions:
        name = str(trans.get("name") or "")
        if name.lower() == lowered:
            return str(trans.get("id"))
    return None


def print_transitions(transitions: list[dict[str, Any]]) -> None:
    if not transitions:
        print("No transitions available.")
        return
    for item in transitions:
        print(f"{item.get('id')}\t{item.get('name')}\t-> {(item.get('to') or {}).get('name', '-')}")


def main() -> int:
    args = parse_args()

    if not args.list and not args.status:
        print("[ERROR] --status is required unless --list is used.", file=sys.stderr)
        return 1

    try:
        client = JiraClient(resolve_auth_args(args))
        endpoint = f"/rest/api/3/issue/{args.issue_key}/transitions"
        transitions_response = client.request_json("GET", endpoint)
        transitions = transitions_response.get("transitions", [])

        if args.list:
            print_transitions(transitions)
            return 0

        transition_id = find_transition_id(transitions, args.status or "")
        if not transition_id:
            names = ", ".join(str(t.get("name")) for t in transitions) or "(none)"
            raise JiraError(f"Transition '{args.status}' not found. Available: {names}")

        payload: dict[str, Any] = {"transition": {"id": transition_id}}

        if args.comment is not None:
            comment_adf = load_adf_document(text=args.comment)
            payload["update"] = {"comment": [{"add": {"body": comment_adf}}]}
        elif args.comment_file is not None:
            comment_adf = load_adf_document(text_file=args.comment_file)
            payload["update"] = {"comment": [{"add": {"body": comment_adf}}]}
        elif args.comment_adf_file is not None:
            comment_adf = load_adf_document(adf_file=args.comment_adf_file)
            payload["update"] = {"comment": [{"add": {"body": comment_adf}}]}

        if args.dry_run:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0

        client.request_json("POST", endpoint, payload=payload)
    except JiraError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    print(json.dumps(
        {
            "issue_key": args.issue_key,
            "status": args.status,
            "transition_id": transition_id,
        },
        ensure_ascii=False,
        indent=2,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
