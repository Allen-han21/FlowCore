#!/usr/bin/env bash
set -euo pipefail

QUERY=""
FORMAT="table"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --query)
      QUERY="$2"
      shift 2
      ;;
    --format)
      FORMAT="$2"
      shift 2
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 1
      ;;
  esac
done

if [[ -z "$QUERY" ]]; then
  echo "Usage: $0 --query '<slack query>' [--format table|json]" >&2
  exit 1
fi

if ! command -v claude >/dev/null 2>&1; then
  echo "claude CLI not found" >&2
  exit 1
fi

PROMPT=$(cat <<EOP
Use Slack MCP tools to search Slack with this query:
$QUERY

Rules:
- If private scope is required, use the private-capable search path with consent handling.
- Return only factual search results.
- If no tool access, say exactly: SLACK_MCP_UNAVAILABLE.

Output format:
- If format is table: columns = date | channel | author | key_sentence | permalink
- If format is json: array objects with keys date, channel, author, key_sentence, permalink

Requested format: $FORMAT
EOP
)

claude -p --permission-mode bypassPermissions "$PROMPT"
