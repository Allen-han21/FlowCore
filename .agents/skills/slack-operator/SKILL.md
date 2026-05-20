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
  - source message: date, channel, author, text, permalink
  - thread replies: date, channel, author, text, permalink
- Messaging outputs should be pure mrkdwn with concise structure.

## Search Guidance

### Source + thread lookup policy

Slack 조회의 기본 목표는 "원문 메시지와 그 원문에 달린 thread"를 확인하는 것이다.

1. Slack permalink 또는 message URL이 있으면 검색하지 말고 해당 원문 메시지와 thread만 읽는다.
2. permalink가 없고 keyword query만 있으면 검색은 원문 후보를 찾기 위한 1회로 제한한다.
3. 원문 후보를 고른 뒤에는 해당 메시지와 같은 thread만 읽는다.
4. 최근 유사 대화, 주변 주제, 추가 키워드 재검색은 사용자가 명시적으로 요청한 경우에만 수행한다.

원문 식별에 필요한 경우에만 query modifier를 사용한다.

- `in:channel-name`
- `from:username`
- `after:YYYY-MM-DD`
- `before:YYYY-MM-DD`
- `"exact phrase"`

### Useful modifiers

- Location: `in:`, `-in:`
- User: `from:`, `to:me`
- Content: `is:thread`, `has:link`, `has:file`
- Date: `after:`, `before:`, `on:`

### Common pitfalls

- Broad keyword search can pull recent similar conversations and slow down lookup. Do not use it after the source message is identified.
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
  --query 'https://workspace.slack.com/archives/C123/p1711111111111111' \
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
