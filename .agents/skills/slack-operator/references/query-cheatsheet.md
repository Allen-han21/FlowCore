# Slack Query Cheatsheet

## Core pattern

Prefer a Slack permalink or message URL when available:

`https://workspace.slack.com/archives/CHANNEL/pTIMESTAMP`

If a permalink is unavailable, use the narrowest query that can identify the original source message:

`<keywords> after:YYYY-MM-DD before:YYYY-MM-DD`

## Examples

- `https://workspace.slack.com/archives/C123/p1711111111111111`
- `URLCache offline "stale data" after:2026-05-04 before:2026-05-19`
- `"cache policy" in:ios-core after:2026-05-01`
- `offline retry has:link after:2026-05-01`

## Lookup sequence

1. Use permalink or message URL if available.
2. If not available, run one narrow search to identify the original message.
3. Read the original message.
4. Read only the original message thread.
5. Do not search recent similar conversations unless explicitly requested.

## Output contract for discovery

- source message: date, channel, author, text, permalink
- thread replies: date, channel, author, text, permalink
