# Slack Query Cheatsheet

## Core pattern

`<keywords> after:YYYY-MM-DD before:YYYY-MM-DD`

## Examples

- `URLCache offline "stale data" after:2026-05-04 before:2026-05-19`
- `"cache policy" in:ios-core after:2026-05-01`
- `offline retry has:link after:2026-05-01`

## Narrowing sequence

1. broad keywords
2. add date filter
3. add `in:` channel
4. add `from:` user if needed

## Output contract for discovery

- date
- channel
- author
- key sentence
- permalink
