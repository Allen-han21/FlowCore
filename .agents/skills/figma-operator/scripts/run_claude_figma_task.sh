#!/usr/bin/env bash
set -euo pipefail

URL=""
TASK=""
INPUT_FILE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --url)
      URL="$2"
      shift 2
      ;;
    --task)
      TASK="$2"
      shift 2
      ;;
    --input-file)
      INPUT_FILE="$2"
      shift 2
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 1
      ;;
  esac
done

if [[ -z "$TASK" ]]; then
  echo "Usage: $0 --task '<figma task description>' [--url '<figma url>'] [--input-file <path>]" >&2
  exit 1
fi

if ! command -v claude >/dev/null 2>&1; then
  echo "claude CLI not found" >&2
  exit 1
fi

EXTRA_CONTEXT=""
if [[ -n "$INPUT_FILE" ]]; then
  if [[ ! -f "$INPUT_FILE" ]]; then
    echo "Input file not found: $INPUT_FILE" >&2
    exit 1
  fi
  EXTRA_CONTEXT=$(cat "$INPUT_FILE")
fi

PROMPT=$(
  printf '%s\n\n' "Execute this Figma task using Claude connected Figma MCP tools:"
  printf '%s\n\n' "$TASK"
  printf '%s\n%s\n\n' "Figma URL (optional):" "$URL"
  printf '%s\n%s\n\n' "Additional context (optional):" "$EXTRA_CONTEXT"
  printf '%s\n' "Rules:"
  printf '%s\n' "- Return factual tool-based results only."
  printf '%s\n' "- Prefer Figma MCP tools for data retrieval and analysis."
  printf '%s\n' "- If MCP access is unavailable, respond exactly with:"
  printf '%s\n' "  FIGMA_MCP_UNAVAILABLE"
  printf '%s\n' "  and include one-line blocker reason."
)

claude -p --permission-mode bypassPermissions "$PROMPT"
