#!/usr/bin/env python3
"""Compatibility wrappers for Jira bootstrap using the shared external-access-bootstrap skill."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jira_auth import JiraError

COMMON_SCRIPTS = Path.home() / ".codex" / "skills" / "external-access-bootstrap" / "scripts"
if str(COMMON_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(COMMON_SCRIPTS))

from bootstrap_common import BootstrapError  # type: ignore  # noqa: E402
from onepassword_provider import (  # type: ignore  # noqa: E402
    build_bootstrap_summary as build_common_bootstrap_summary,
    build_env_lines as build_common_env_lines,
    build_secret_ref,
    resolve_item as resolve_common_item,
    write_env_file as write_common_env_file,
    write_temp_env_file as write_common_temp_env_file,
)

DEFAULT_VAULT = "Personal"
DEFAULT_ITEM = "JIRA - Kidsnote Atlassian"


@dataclass(frozen=True)
class OnePasswordItem:
    account: str | None
    vault_name: str
    vault_id: str
    item_name: str
    item_id: str
    base_url: str
    username_ref: str
    api_token_ref: str


def _wrap_bootstrap_error(exc: BootstrapError) -> JiraError:
    return JiraError(str(exc))


def _to_common_lines(item: OnePasswordItem) -> list[str]:
    return [
        f"JIRA_BASE_URL={item.base_url}",
        f"JIRA_EMAIL={item.username_ref}",
        f"JIRA_API_TOKEN={item.api_token_ref}",
    ]


def resolve_item(
    *,
    vault_name: str = DEFAULT_VAULT,
    item_name: str = DEFAULT_ITEM,
    base_url: str | None = None,
    account: str | None = None,
) -> OnePasswordItem:
    try:
        resolved = resolve_common_item(
            vault_name=vault_name,
            item_name=item_name,
            base_url=base_url,
            account=account,
        )
    except BootstrapError as exc:
        raise _wrap_bootstrap_error(exc) from exc
    return OnePasswordItem(
        account=resolved.account,
        vault_name=resolved.vault_name,
        vault_id=resolved.vault_id,
        item_name=resolved.item_name,
        item_id=resolved.item_id,
        base_url=resolved.base_url,
        username_ref=build_secret_ref(resolved.vault_id, resolved.item_id, "username"),
        api_token_ref=build_secret_ref(resolved.vault_id, resolved.item_id, "credential"),
    )


def build_env_lines(item: OnePasswordItem) -> list[str]:
    try:
        return build_common_env_lines(
            resolve_common_item(
                vault_name=item.vault_name,
                item_name=item.item_name,
                base_url=item.base_url,
                account=item.account,
            ),
            field_env={"JIRA_EMAIL": "username", "JIRA_API_TOKEN": "credential"},
            literal_env={"JIRA_BASE_URL": "@base_url"},
        )
    except BootstrapError:
        return _to_common_lines(item)


def write_temp_env_file(item: OnePasswordItem) -> str:
    try:
        return write_common_temp_env_file(build_env_lines(item), prefix="jira-op-run-", suffix=".env")
    except BootstrapError as exc:
        raise _wrap_bootstrap_error(exc) from exc


def write_env_file(path: Path, item: OnePasswordItem) -> Path:
    try:
        return write_common_env_file(path, build_env_lines(item))
    except BootstrapError as exc:
        raise _wrap_bootstrap_error(exc) from exc


def build_bootstrap_summary(item: OnePasswordItem) -> dict[str, Any]:
    try:
        summary = build_common_bootstrap_summary(
            resolved_item := resolve_common_item(
                vault_name=item.vault_name,
                item_name=item.item_name,
                base_url=item.base_url,
                account=item.account,
            ),
            field_env={"JIRA_EMAIL": "username", "JIRA_API_TOKEN": "credential"},
            literal_env={"JIRA_BASE_URL": "@base_url"},
        )
    except BootstrapError as exc:
        raise _wrap_bootstrap_error(exc) from exc
    summary["recommended_flow"] = [
        "Use op run once per Jira batch command.",
        "Fetch multiple issues in one process.",
        "Do not export revealed secrets into repo-local files.",
    ]
    summary["item"] = resolved_item.item_name
    return summary
