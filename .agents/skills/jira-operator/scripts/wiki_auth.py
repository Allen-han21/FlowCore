#!/usr/bin/env python3
"""Shared Confluence (wiki) authentication helpers and verifier."""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
from dataclasses import dataclass
from typing import Any
from urllib import error, parse, request

ENV_BASE_URL = "CONFLUENCE_BASE_URL"
ENV_EMAIL = "CONFLUENCE_EMAIL"
ENV_API_TOKEN = "CONFLUENCE_API_TOKEN"

FALLBACK_ENV_BASE_URL = "JIRA_BASE_URL"
FALLBACK_ENV_EMAIL = "JIRA_EMAIL"
FALLBACK_ENV_API_TOKEN = "JIRA_API_TOKEN"

DEFAULT_BASE_URL = "https://kidsnote.atlassian.net/wiki"
DEFAULT_TIMEOUT = 30.0


class ConfluenceError(RuntimeError):
    """Raised when Confluence credentials or API requests fail."""


@dataclass(frozen=True)
class ConfluenceCredentials:
    base_url: str
    email: str
    api_token: str


def normalize_base_url(base_url: str) -> str:
    value = base_url.strip().rstrip("/")
    if not value.startswith(("http://", "https://")):
        raise ConfluenceError(
            f"Confluence base URL must include http:// or https://: {base_url!r}"
        )
    parsed = parse.urlparse(value)
    path = parsed.path.rstrip("/")
    if path == "":
        path = "/wiki"
    elif path != "/wiki":
        # Keep explicit non-default path, but for standard Atlassian root enforce /wiki.
        if parsed.netloc.endswith("atlassian.net") and path == "":
            path = "/wiki"
    rebuilt = parse.urlunparse((parsed.scheme, parsed.netloc, path, "", "", ""))
    return rebuilt


def derive_wiki_base_url_from_jira(jira_base_url: str) -> str:
    jira = jira_base_url.strip().rstrip("/")
    if jira.endswith("/wiki"):
        return jira
    return f"{jira}/wiki"


def load_credentials(
    *,
    base_url: str | None = None,
    email: str | None = None,
    api_token: str | None = None,
) -> ConfluenceCredentials:
    resolved_base_url = base_url or os.environ.get(ENV_BASE_URL)
    if not resolved_base_url:
        jira_base = os.environ.get(FALLBACK_ENV_BASE_URL)
        if jira_base:
            resolved_base_url = derive_wiki_base_url_from_jira(jira_base)
    if not resolved_base_url:
        resolved_base_url = DEFAULT_BASE_URL

    resolved_email = email or os.environ.get(ENV_EMAIL) or os.environ.get(FALLBACK_ENV_EMAIL)
    resolved_api_token = (
        api_token
        or os.environ.get(ENV_API_TOKEN)
        or os.environ.get(FALLBACK_ENV_API_TOKEN)
    )

    missing = []
    if not resolved_email:
        missing.append(f"{ENV_EMAIL} (or {FALLBACK_ENV_EMAIL})")
    if not resolved_api_token:
        missing.append(f"{ENV_API_TOKEN} (or {FALLBACK_ENV_API_TOKEN})")

    if missing:
        raise ConfluenceError(
            "Missing Confluence credentials: "
            + ", ".join(missing)
            + ". Set environment variables or pass --email/--api-token."
        )

    return ConfluenceCredentials(
        base_url=normalize_base_url(resolved_base_url),
        email=resolved_email.strip(),
        api_token=resolved_api_token.strip(),
    )


class ConfluenceClient:
    """Small Confluence REST API client without external dependencies."""

    def __init__(self, credentials: ConfluenceCredentials, timeout: float = DEFAULT_TIMEOUT) -> None:
        self.credentials = credentials
        self.timeout = timeout
        token = f"{credentials.email}:{credentials.api_token}".encode("utf-8")
        self.authorization = base64.b64encode(token).decode("ascii")

    def request_json(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        payload: dict[str, Any] | None = None,
    ) -> Any:
        url = build_url(self.credentials.base_url, path, params=params)
        body = None
        headers = {
            "Accept": "application/json",
            "Authorization": f"Basic {self.authorization}",
        }
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        req = request.Request(url, data=body, headers=headers, method=method.upper())
        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
                if not raw.strip():
                    return {}
                return json.loads(raw)
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace").strip()
            if detail:
                try:
                    parsed = json.loads(detail)
                    detail = json.dumps(parsed, ensure_ascii=False)
                except json.JSONDecodeError:
                    pass
            raise ConfluenceError(
                f"Confluence API {exc.code} {method.upper()} {url}: {detail or exc.reason}"
            ) from exc
        except error.URLError as exc:
            raise ConfluenceError(f"Could not reach Confluence at {url}: {exc.reason}") from exc

    def verify_auth(self) -> dict[str, Any]:
        return self.request_json("GET", "/rest/api/user/current")

    def get_page(self, page_id: str, *, expand: str | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if expand:
            params["expand"] = expand
        encoded = parse.quote(str(page_id), safe="")
        return self.request_json("GET", f"/rest/api/content/{encoded}", params=params)

    def search(self, *, cql: str, limit: int = 10, start: int = 0, expand: str | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {
            "cql": cql,
            "limit": limit,
            "start": start,
        }
        if expand:
            params["expand"] = expand
        return self.request_json("GET", "/rest/api/search", params=params)

    def update_page_storage(
        self,
        *,
        page_id: str,
        title: str,
        storage_value: str,
        next_version: int,
        space_key: str | None = None,
        minor_edit: bool = False,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "id": str(page_id),
            "type": "page",
            "title": title,
            "body": {
                "storage": {
                    "value": storage_value,
                    "representation": "storage",
                }
            },
            "version": {
                "number": int(next_version),
                "minorEdit": bool(minor_edit),
            },
        }
        if space_key:
            payload["space"] = {"key": space_key}
        encoded = parse.quote(str(page_id), safe="")
        return self.request_json("PUT", f"/rest/api/content/{encoded}", payload=payload)


def build_url(base_url: str, path: str, *, params: dict[str, Any] | None = None) -> str:
    url = f"{base_url}{path}"
    if not params:
        return url
    normalized: dict[str, str] = {}
    for key, value in params.items():
        if value is None:
            continue
        normalized[key] = str(value)
    query = parse.urlencode(normalized)
    return f"{url}?{query}" if query else url


def resolve_auth_args(args: argparse.Namespace) -> ConfluenceCredentials:
    return load_credentials(
        base_url=args.base_url,
        email=args.email,
        api_token=args.api_token,
    )


def add_auth_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--base-url",
        help=(
            f"Confluence base URL. Falls back to ${ENV_BASE_URL}, "
            f"then ${FALLBACK_ENV_BASE_URL}+ '/wiki', then {DEFAULT_BASE_URL}."
        ),
    )
    parser.add_argument(
        "--email",
        help=f"Confluence account email. Falls back to ${ENV_EMAIL} or ${FALLBACK_ENV_EMAIL}.",
    )
    parser.add_argument(
        "--api-token",
        help=f"Confluence API token. Falls back to ${ENV_API_TOKEN} or ${FALLBACK_ENV_API_TOKEN}.",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Confluence credentials against /user/current.")
    add_auth_arguments(parser)
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Explicit flag for readability. Auth verification is the default action.",
    )
    args = parser.parse_args()

    try:
        client = ConfluenceClient(resolve_auth_args(args))
        user = client.verify_auth()
    except ConfluenceError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    account = user.get("email") or user.get("displayName") or user.get("accountId") or "-"
    print(
        json.dumps(
            {
                "base_url": client.credentials.base_url,
                "account": account,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
