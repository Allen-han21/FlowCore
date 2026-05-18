# Confluence CQL Cheatsheet

Base wiki URL:
- https://kidsnote.atlassian.net/wiki

Common queries:
- `type = page AND title ~ "키워드" ORDER BY lastmodified DESC`
- `space = "ENG" AND type = page ORDER BY lastmodified DESC`
- `label = "incident" AND type = page`
- `creator = currentUser() AND type = page ORDER BY created DESC`

Notes:
- Use `wiki_search_pages.py --cql "..." --limit 10` for API-first search.
- Increase `--start` for pagination.
