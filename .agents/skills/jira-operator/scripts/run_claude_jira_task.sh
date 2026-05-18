#!/usr/bin/env bash
set -euo pipefail

TASK=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --task)
      TASK="$2"
      shift 2
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 1
      ;;
  esac
done

if [[ -z "$TASK" ]]; then
  echo "Usage: $0 --task '<jira task description>'" >&2
  exit 1
fi

if ! command -v claude >/dev/null 2>&1; then
  echo "claude CLI not found" >&2
  exit 1
fi

PROMPT=$(cat <<EOP
Execute this Jira task using available Jira tools (MCP if connected; otherwise explain missing access):
$TASK

Rules:
- Return factual results only.
- If access is unavailable, return exact blocker and required setup.
EOP
)

claude -p --permission-mode bypassPermissions "$PROMPT"
