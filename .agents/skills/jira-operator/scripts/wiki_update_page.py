#!/usr/bin/env python3
"""Update Confluence page storage body with safe version increment."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from wiki_auth import ConfluenceClient, ConfluenceError, add_auth_arguments, resolve_auth_args


def load_storage_value(*, body: str | None, body_file: str | None) -> str:
    if body and body_file:
        raise ConfluenceError("Provide only one body source: --body or --body-file.")
    if body_file:
        return Path(body_file).read_text(encoding="utf-8")
    if body is not None:
        return body
    raise ConfluenceError("One body source is required: --body or --body-file.")


def build_preview_payload(
    *,
    page: dict[str, Any],
    storage_value: str,
    title_override: str | None,
    minor_edit: bool,
) -> dict[str, Any]:
    page_id = str(page.get("id") or "")
    if not page_id:
        raise ConfluenceError("Page payload does not include id.")

    title = title_override or page.get("title")
    if not title:
        raise ConfluenceError("Page title could not be resolved.")

    version = page.get("version") or {}
    current_version = version.get("number")
    if not isinstance(current_version, int):
        raise ConfluenceError("Could not resolve current page version number.")

    payload: dict[str, Any] = {
        "id": page_id,
        "type": "page",
        "title": title,
        "body": {
            "storage": {
                "value": storage_value,
                "representation": "storage",
            }
        },
        "version": {
            "number": current_version + 1,
            "minorEdit": minor_edit,
        },
    }

    space_key = ((page.get("space") or {}).get("key"))
    if space_key:
        payload["space"] = {"key": space_key}

    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Update a Confluence page body.storage safely.")
    add_auth_arguments(parser)
    parser.add_argument("page_id", help="Confluence page id.")
    parser.add_argument("--title", help="Optional new title. Defaults to current title.")
    parser.add_argument("--body", help="New body.storage value (HTML/XHTML storage format).")
    parser.add_argument("--body-file", help="File path containing new body.storage value.")
    parser.add_argument("--minor-edit", action="store_true", help="Mark update as minor edit.")
    parser.add_argument("--dry-run", action="store_true", help="Print payload without updating page.")
    parser.add_argument(
        "--fetch-expand",
        default="version,space,title",
        help="Expand fields used while reading current page state.",
    )
    args = parser.parse_args()

    try:
        storage_value = load_storage_value(body=args.body, body_file=args.body_file)
        client = ConfluenceClient(resolve_auth_args(args))
        page = client.get_page(args.page_id, expand=args.fetch_expand)
        payload = build_preview_payload(
            page=page,
            storage_value=storage_value,
            title_override=args.title,
            minor_edit=args.minor_edit,
        )

        if args.dry_run:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0

        updated = client.update_page_storage(
            page_id=payload["id"],
            title=payload["title"],
            storage_value=payload["body"]["storage"]["value"],
            next_version=payload["version"]["number"],
            space_key=(payload.get("space") or {}).get("key"),
            minor_edit=payload["version"].get("minorEdit", False),
        )
    except ConfluenceError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "page_id": updated.get("id") or payload["id"],
                "title": updated.get("title") or payload["title"],
                "version": (updated.get("version") or {}).get("number") or payload["version"]["number"],
                "base_url": client.credentials.base_url,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
