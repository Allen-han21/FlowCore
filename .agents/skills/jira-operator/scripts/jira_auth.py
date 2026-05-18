#!/usr/bin/env python3
"""Shared Jira authentication helpers and a basic auth verifier."""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error, parse, request

ENV_BASE_URL = "JIRA_BASE_URL"
ENV_EMAIL = "JIRA_EMAIL"
ENV_API_TOKEN = "JIRA_API_TOKEN"
DEFAULT_TIMEOUT = 30.0


class JiraError(RuntimeError):
    """Raised when Jira credentials or API requests fail."""


@dataclass(frozen=True)
class JiraCredentials:
    base_url: str
    email: str
    api_token: str


def normalize_base_url(base_url: str) -> str:
    value = base_url.strip().rstrip("/")
    if not value.startswith(("http://", "https://")):
        raise JiraError(f"Jira base URL must include http:// or https://: {base_url!r}")
    return value


def load_credentials(
    *,
    base_url: str | None = None,
    email: str | None = None,
    api_token: str | None = None,
) -> JiraCredentials:
    resolved_base_url = base_url or os.environ.get(ENV_BASE_URL)
    resolved_email = email or os.environ.get(ENV_EMAIL)
    resolved_api_token = api_token or os.environ.get(ENV_API_TOKEN)

    missing = []
    if not resolved_base_url:
        missing.append(ENV_BASE_URL)
    if not resolved_email:
        missing.append(ENV_EMAIL)
    if not resolved_api_token:
        missing.append(ENV_API_TOKEN)

    if missing:
        raise JiraError(
            "Missing Jira credentials: "
            + ", ".join(missing)
            + ". Set environment variables or pass --base-url/--email/--api-token."
        )

    return JiraCredentials(
        base_url=normalize_base_url(resolved_base_url),
        email=resolved_email.strip(),
        api_token=resolved_api_token.strip(),
    )


class JiraClient:
    """Small Jira REST API client that avoids external dependencies."""

    def __init__(self, credentials: JiraCredentials, timeout: float = DEFAULT_TIMEOUT) -> None:
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
            raise JiraError(f"Jira API {exc.code} {method.upper()} {url}: {detail or exc.reason}") from exc
        except error.URLError as exc:
            raise JiraError(f"Could not reach Jira at {url}: {exc.reason}") from exc

    def get_issue(self, issue_key: str, *, fields: list[str] | None = None) -> dict[str, Any]:
        params = {}
        if fields:
            params["fields"] = ",".join(fields)
        encoded_key = parse.quote(issue_key, safe="")
        return self.request_json("GET", f"/rest/api/3/issue/{encoded_key}", params=params)

    def update_issue_fields(self, issue_key: str, fields: dict[str, Any]) -> None:
        encoded_key = parse.quote(issue_key, safe="")
        self.request_json("PUT", f"/rest/api/3/issue/{encoded_key}", payload={"fields": fields})

    def create_issue(self, fields: dict[str, Any]) -> dict[str, Any]:
        return self.request_json("POST", "/rest/api/3/issue", payload={"fields": fields})

    def verify_auth(self) -> dict[str, Any]:
        return self.request_json("GET", "/rest/api/3/myself")


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


def text_to_adf(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if not stripped:
        raise JiraError("Description text is empty.")

    content = []
    for chunk in re.split(r"\n\s*\n", stripped):
        nodes: list[dict[str, Any]] = []
        for index, line in enumerate(chunk.splitlines()):
            if index:
                nodes.append({"type": "hardBreak"})
            if line:
                nodes.append({"type": "text", "text": line})
        content.append({"type": "paragraph", "content": nodes})

    return {
        "version": 1,
        "type": "doc",
        "content": content,
    }


def load_adf_document(
    *,
    adf_file: str | None = None,
    text: str | None = None,
    text_file: str | None = None,
) -> dict[str, Any]:
    sources = [value for value in (adf_file, text, text_file) if value is not None]
    if len(sources) != 1:
        raise JiraError("Provide exactly one description source: --adf-file, --text, or --text-file.")

    if adf_file:
        return parse_adf_file(Path(adf_file))
    if text_file:
        return text_to_adf(Path(text_file).read_text(encoding="utf-8"))
    return text_to_adf(text or "")


def parse_adf_file(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    candidate = extract_json_code_block(raw) if path.suffix.lower() in {".md", ".markdown"} else raw
    if candidate is None:
        raise JiraError(f"No fenced json block found in markdown file: {path}")

    try:
        document = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise JiraError(f"Invalid JSON in {path}: {exc}") from exc

    validate_adf(document, source=str(path))
    return document


def extract_json_code_block(raw: str) -> str | None:
    match = re.search(r"```json\s*(\{.*?\})\s*```", raw, flags=re.DOTALL)
    if match:
        return match.group(1)
    stripped = raw.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return stripped
    return None


def validate_adf(document: Any, *, source: str) -> None:
    if not isinstance(document, dict):
        raise JiraError(f"ADF payload from {source} must be a JSON object.")
    if document.get("type") != "doc":
        raise JiraError(f"ADF payload from {source} must have type='doc'.")
    if document.get("version") != 1:
        raise JiraError(f"ADF payload from {source} must have version=1.")
    content = document.get("content")
    if not isinstance(content, list) or not content:
        raise JiraError(f"ADF payload from {source} must contain a non-empty content array.")


def resolve_auth_args(args: argparse.Namespace) -> JiraCredentials:
    return load_credentials(
        base_url=args.base_url,
        email=args.email,
        api_token=args.api_token,
    )


def add_auth_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--base-url", help=f"Jira site URL. Falls back to ${ENV_BASE_URL}.")
    parser.add_argument("--email", help=f"Jira account email. Falls back to ${ENV_EMAIL}.")
    parser.add_argument("--api-token", help=f"Jira API token. Falls back to ${ENV_API_TOKEN}.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Jira credentials against the /myself API.")
    add_auth_arguments(parser)
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Explicit flag for readability. Auth verification is the default action.",
    )
    args = parser.parse_args()

    try:
        client = JiraClient(resolve_auth_args(args))
        user = client.verify_auth()
    except JiraError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    account = user.get("emailAddress") or user.get("displayName") or user.get("accountId")
    print(json.dumps(
        {
            "base_url": client.credentials.base_url,
            "account": account,
            "display_name": user.get("displayName"),
            "account_id": user.get("accountId"),
        },
        ensure_ascii=False,
        indent=2,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
