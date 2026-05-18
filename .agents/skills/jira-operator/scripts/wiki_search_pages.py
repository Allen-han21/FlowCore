#!/usr/bin/env python3
"""Search Confluence pages with CQL and print concise results."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from wiki_auth import ConfluenceClient, ConfluenceError, add_auth_arguments, resolve_auth_args


def extract_rows(payload: dict[str, Any], *, base_url: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for item in payload.get("results", []):
        content = item.get("content") or {}
        links = content.get("_links") or {}
        webui = links.get("webui")
        permalink = f"{base_url}{webui}" if webui else (item.get("url") or "-")

        rows.append(
            {
                "id": str(content.get("id") or "-"),
                "title": str(content.get("title") or item.get("title") or "-"),
                "space": str((content.get("space") or {}).get("key") or "-"),
                "updated": str(((content.get("version") or {}).get("when")) or item.get("lastModified") or "-"),
                "url": permalink,
            }
        )
    return rows


def print_rows(rows: list[dict[str, str]]) -> None:
    if not rows:
        print("No results.")
        return
    for idx, row in enumerate(rows, start=1):
        print(f"[{idx}] {row['id']} | {row['space']} | {row['updated']}")
        print(f"  {row['title']}")
        print(f"  {row['url']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Search Confluence pages with CQL.")
    add_auth_arguments(parser)
    parser.add_argument("--cql", required=True, help="Confluence CQL query.")
    parser.add_argument("--limit", type=int, default=10, help="Result size (default: 10).")
    parser.add_argument("--start", type=int, default=0, help="Pagination start offset.")
    parser.add_argument("--expand", help="Optional expand expression.")
    parser.add_argument("--raw", action="store_true", help="Print full raw JSON.")
    args = parser.parse_args()

    try:
        client = ConfluenceClient(resolve_auth_args(args))
        payload = client.search(cql=args.cql, limit=args.limit, start=args.start, expand=args.expand)
    except ConfluenceError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    if args.raw:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    rows = extract_rows(payload, base_url=client.credentials.base_url)
    print_rows(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
