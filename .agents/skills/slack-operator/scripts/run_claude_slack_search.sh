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
Use Slack MCP tools to look up the original Slack message and its thread for this input:
$QUERY

Rules:
- If private scope is required, use the private-capable search path with consent handling.
- If the input is a Slack permalink or message URL, do not run broad search. Read that exact original message and its thread only.
- If the input is a keyword query, run at most one Slack search to identify the original source message, then read that message and its thread only.
- Do not search for recent similar conversations, related discussions, surrounding topics, or extra keyword variants unless the user explicitly asked for them.
- Return only factual results from the original message and its thread.
- If no tool access, say exactly: SLACK_MCP_UNAVAILABLE.

Output format:
- If format is table: include source_message and thread_replies sections. For each message, columns = date | channel | author | text | permalink
- If format is json: object with keys source_message and thread_replies. source_message has date, channel, author, text, permalink. thread_replies is an array with the same keys.

Requested format: $FORMAT
EOP
)

claude -p --permission-mode bypassPermissions "$PROMPT"
