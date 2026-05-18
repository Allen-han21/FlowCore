#!/usr/bin/env python3
"""Run a Jira command once under op run using safe secret references."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

from jira_1password import DEFAULT_ITEM, DEFAULT_VAULT, resolve_item, write_temp_env_file
from jira_auth import JiraError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Wrap a Jira command in one op run invocation so repeated secret fetches are avoided."
    )
    parser.add_argument("--account", help="1Password account selector for op CLI.")
    parser.add_argument("--vault", default=DEFAULT_VAULT, help="1Password vault name.")
    parser.add_argument("--item", default=DEFAULT_ITEM, help="1Password item title.")
    parser.add_argument("--base-url", help="Explicit Jira base URL override.")
    parser.add_argument("--dry-run", action="store_true", help="Print the resolved command without running it.")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to execute after --")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        print("[ERROR] Provide a command after -- to run inside op run.", file=sys.stderr)
        return 2

    try:
        item = resolve_item(
            vault_name=args.vault,
            item_name=args.item,
            base_url=args.base_url,
            account=args.account,
        )
        env_file = write_temp_env_file(item)
    except JiraError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    op_command = ["op"]
    if args.account:
        op_command.extend(["--account", args.account])
    op_command.extend(["run", f"--env-file={env_file}", "--", *command])

    try:
        if args.dry_run:
            preview = list(op_command)
            preview = [
                value if not value.startswith("--env-file=") else "--env-file=<temp-env-file>"
                for value in preview
            ]
            print(f"base_url: {item.base_url}")
            print("env_strategy: temp op run env-file")
            print("command:")
            print(" ".join(preview))
            return 0

        completed = subprocess.run(op_command)
        return completed.returncode
    finally:
        try:
            os.unlink(env_file)
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
