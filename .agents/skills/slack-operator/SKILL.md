---
name: slack-operator
description: Unified Slack skill for search and messaging. Use Claude MCP directly in Claude Code sessions; use claude -p --permission-mode bypassPermissions bridge scripts from non-Claude agents (e.g., Codex) to execute Slack MCP workflows.
---

# Slack Operator

## Overview

This skill unifies two capabilities in one place:
- Slack search (`slack-search`)
- Slack message drafting (`slack-messaging`)

Primary runtime policy:
- Claude Code session: use Slack MCP tools directly.
- Non-Claude agent session (Codex, etc.): call Claude non-interactively with `claude -p --permission-mode bypassPermissions` bridge scripts in `scripts/`.

## Goal

Provide one repeatable entrypoint for Slack context discovery and Slack-ready communication text.

## Workflow

### 1) Choose mode

- Search mode: find messages/files/channels/users.
- Messaging mode: draft well-formatted mrkdwn output.

### 2) Choose runtime path

- If current agent is Claude Code:
  - Use MCP tools directly (`slack_search_*`, `slack_read_*`, `slack_send_message*`).
- If current agent is not Claude Code:
  - Use `scripts/run_claude_slack_search.sh` or `scripts/run_claude_slack_message.sh`.
  - These scripts delegate execution to `claude -p --permission-mode bypassPermissions` so Slack MCP remains in Claude runtime.

### 3) Produce artifact

- Search outputs should include:
  - date
  - channel
  - author
  - key sentence
  - permalink
- Messaging outputs should be pure mrkdwn with concise structure.

## Search Guidance

### Recommended query strategy

1. Start broad keyword query.
2. Narrow with modifiers:
- `in:channel-name`
- `from:username`
- `after:YYYY-MM-DD`
- `before:YYYY-MM-DD`
- `"exact phrase"`
3. Split large questions into multiple focused searches.

### Useful modifiers

- Location: `in:`, `-in:`
- User: `from:`, `to:me`
- Content: `is:thread`, `has:link`, `has:file`
- Date: `after:`, `before:`, `on:`

### Common pitfalls

- Slack search does not support boolean operators like `AND/OR/NOT`.
- Slack search is not fully real-time for just-posted messages.
- Private/DM search requires proper permission and consent path.

## Messaging Guidance

Use Slack mrkdwn (not standard Markdown):
- Bold: `*text*`
- Italic: `_text_`
- Link: `<url|text>`
- Mention user: `<@U123456>`
- Mention channel: `<#C123456>`

Avoid:
- `**bold**`
- `[text](url)`
- Markdown headers like `##`

Message structure:
- first line = key point
- short paragraphs
- bullet list for 3+ items
- clear CTA/action items

## Commands

Search via Claude bridge (non-Claude agents, bypassPermissions):

```bash
bash scripts/run_claude_slack_search.sh \
  --query 'URLCache offline "stale data" after:2026-05-04 before:2026-05-19' \
  --format table
```

Message draft via Claude bridge (non-Claude agents, bypassPermissions):

```bash
bash scripts/run_claude_slack_message.sh \
  --channel '#ios-core' \
  --purpose 'discovery summary' \
  --input-file ai/discovery.md
```

## Constraints

- Do not claim Slack results if MCP/tool execution did not run.
- For non-Claude agents, do not directly fabricate MCP calls; use `claude -p --permission-mode bypassPermissions` bridge.
- Keep sensitive Slack content minimal in persisted files unless user requested archival.

## Resources

### scripts/

  - `scripts/run_claude_slack_search.sh`
  - Delegates Slack discovery prompt to Claude (`claude -p --permission-mode bypassPermissions`).
- `scripts/run_claude_slack_message.sh`
  - Delegates Slack message drafting prompt to Claude (`claude -p --permission-mode bypassPermissions`).

### references/

- `references/query-cheatsheet.md`
  - Query modifiers and ready-to-run examples.
