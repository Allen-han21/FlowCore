#!/usr/bin/env python3
"""Create child Jira issues from a JSON file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from jira_auth import JiraClient, JiraError, add_auth_arguments, load_adf_document, resolve_auth_args


def load_items(path: Path) -> tuple[list[dict[str, Any]], Path]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise JiraError(f"Invalid JSON in {path}: {exc}") from exc

    if isinstance(payload, list):
        items = payload
    elif isinstance(payload, dict) and isinstance(payload.get("items"), list):
        items = payload["items"]
    else:
        raise JiraError("Items file must be a JSON array or an object with an 'items' array.")

    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise JiraError(f"Item #{index} must be a JSON object.")
        summary = item.get("summary")
        if not isinstance(summary, str) or not summary.strip():
            raise JiraError(f"Item #{index} is missing a non-empty 'summary'.")
        normalized.append(item)
    return normalized, path.parent


def load_item_description(item: dict[str, Any], base_dir: Path) -> dict[str, Any] | None:
    if "description_adf_file" in item:
        return load_adf_document(adf_file=str((base_dir / item["description_adf_file"]).resolve()))
    if "description_file" in item:
        return load_adf_document(text_file=str((base_dir / item["description_file"]).resolve()))
    if "description" in item:
        return load_adf_document(text=item["description"])
    return None


def build_fields(
    *,
    item: dict[str, Any],
    parent_key: str,
    project_key: str,
    default_issue_type: str,
    base_dir: Path,
) -> dict[str, Any]:
    fields: dict[str, Any] = {
        "project": {"key": project_key},
        "parent": {"key": parent_key},
        "issuetype": {"name": item.get("issue_type") or default_issue_type},
        "summary": item["summary"].strip(),
    }
    description = load_item_description(item, base_dir)
    if description:
        fields["description"] = description
    labels = item.get("labels")
    if labels is not None:
        if not isinstance(labels, list) or not all(isinstance(label, str) for label in labels):
            raise JiraError(f"Invalid labels for item {item['summary']!r}. Expected a string array.")
        fields["labels"] = labels
    extra_fields = item.get("extra_fields")
    if extra_fields is not None:
        if not isinstance(extra_fields, dict):
            raise JiraError(f"Invalid extra_fields for item {item['summary']!r}. Expected an object.")
        fields.update(extra_fields)
    return fields


def resolve_project_key(
    *,
    client: JiraClient | None,
    parent_key: str,
    project_key: str | None,
) -> str:
    if project_key:
        return project_key
    if client is None:
        raise JiraError("--project-key is required for --dry-run when Jira is not queried.")
    parent = client.get_issue(parent_key, fields=["project"])
    resolved = ((parent.get("fields") or {}).get("project") or {}).get("key")
    if not resolved:
        raise JiraError(f"Could not resolve project key from parent issue {parent_key}.")
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(description="Create child Jira issues from a JSON file.")
    add_auth_arguments(parser)
    parser.add_argument("parent_key", help="Parent issue key such as PK-12345.")
    parser.add_argument("--items-file", required=True, help="JSON file that defines child issues.")
    parser.add_argument("--issue-type", default="Sub-task", help="Default issue type name.")
    parser.add_argument("--project-key", help="Project key. Optional when Jira can infer it from parent.")
    parser.add_argument("--dry-run", action="store_true", help="Print payloads without creating issues.")
    args = parser.parse_args()

    try:
        items, base_dir = load_items(Path(args.items_file))
        client = None if args.dry_run and args.project_key else JiraClient(resolve_auth_args(args))
        project_key = resolve_project_key(
            client=client,
            parent_key=args.parent_key,
            project_key=args.project_key,
        )
        payloads = [
            build_fields(
                item=item,
                parent_key=args.parent_key,
                project_key=project_key,
                default_issue_type=args.issue_type,
                base_dir=base_dir,
            )
            for item in items
        ]

        if args.dry_run:
            print(json.dumps(payloads, ensure_ascii=False, indent=2))
            return 0

        assert client is not None
        created = []
        for fields in payloads:
            result = client.create_issue(fields)
            created.append({
                "summary": fields["summary"],
                "issue_key": result.get("key"),
                "issue_id": result.get("id"),
            })
        print(json.dumps(created, ensure_ascii=False, indent=2))
    except JiraError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
