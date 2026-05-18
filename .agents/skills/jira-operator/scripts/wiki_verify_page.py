#!/usr/bin/env python3
"""Fetch a Confluence page and print a concise summary."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from wiki_auth import ConfluenceClient, ConfluenceError, add_auth_arguments, resolve_auth_args

DEFAULT_EXPAND = "version,space,history.lastUpdated"


def render_summary(page: dict[str, Any], *, base_url: str) -> str:
    page_id = page.get("id") or "-"
    title = page.get("title") or "-"
    page_type = page.get("type") or "-"
    status = page.get("status") or "-"

    space = page.get("space") or {}
    space_key = space.get("key") or "-"

    version = page.get("version") or {}
    version_number = version.get("number") or "-"

    history = page.get("history") or {}
    updated = ((history.get("lastUpdated") or {}).get("when")) or version.get("when") or "-"

    links = page.get("_links") or {}
    webui = links.get("webui")
    permalink = f"{base_url}{webui}" if webui else "-"

    lines = [
        f"Page ID: {page_id}",
        f"Title: {title}",
        f"Type: {page_type}",
        f"Status: {status}",
        f"Space: {space_key}",
        f"Version: {version_number}",
        f"Updated: {updated}",
        f"Permalink: {permalink}",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch a Confluence page and print a concise summary.")
    add_auth_arguments(parser)
    parser.add_argument("page_id", help="Confluence page id.")
    parser.add_argument("--expand", default=DEFAULT_EXPAND, help="Expand fields for page details.")
    parser.add_argument("--raw", action="store_true", help="Print the raw response JSON.")
    args = parser.parse_args()

    try:
        client = ConfluenceClient(resolve_auth_args(args))
        page = client.get_page(args.page_id, expand=args.expand)
    except ConfluenceError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    if args.raw:
        print(json.dumps(page, ensure_ascii=False, indent=2))
    else:
        print(render_summary(page, base_url=client.credentials.base_url))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
