#!/usr/bin/env bash
set -euo pipefail

CHANNEL=""
PURPOSE=""
INPUT_FILE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --channel)
      CHANNEL="$2"
      shift 2
      ;;
    --purpose)
      PURPOSE="$2"
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

if [[ -z "$CHANNEL" || -z "$PURPOSE" || -z "$INPUT_FILE" ]]; then
  echo "Usage: $0 --channel '#channel' --purpose '<purpose>' --input-file <path>" >&2
  exit 1
fi

if [[ ! -f "$INPUT_FILE" ]]; then
  echo "Input file not found: $INPUT_FILE" >&2
  exit 1
fi

if ! command -v claude >/dev/null 2>&1; then
  echo "claude CLI not found" >&2
  exit 1
fi

CONTENT=$(cat "$INPUT_FILE")

PROMPT=$(cat <<EOP
Draft one Slack message in mrkdwn.

Context channel: $CHANNEL
Purpose: $PURPOSE

Source content:
$CONTENT

Rules:
- Output message text only.
- Use Slack mrkdwn.
- Keep concise and actionable.
- Include clear CTA.
EOP
)

claude -p --permission-mode bypassPermissions "$PROMPT"
