---
name: jira-operator
description: Unified Jira + Confluence operator skill for Codex and Claude. API-first execution with reusable Python scripts, 1Password bootstrap, optional MCP path, and safe write workflow (verify -> dry-run -> apply).
---

# Jira Operator

## Overview

이 스킬은 Jira + Confluence(사내 위키) 작업을 하나의 진입점으로 통합한다.

통합 대상:
- `kidsnote-jira-operator`의 검증된 Python 스크립트 워크플로
- Jira 운영 가이드(조회/코멘트/전환/검색) 패턴

Primary runtime policy:
- API-first: `scripts/*.py`를 기본 실행 경로로 사용한다.
- Claude + Jira MCP가 이미 연결된 경우에만 MCP 도구를 선택적으로 사용한다.
- Non-Claude agent에서 Claude 브리지가 필요하면 `claude -p --permission-mode bypassPermissions`를 사용한다.

Confluence wiki base URL:
- `https://kidsnote.atlassian.net/wiki`

## Goal

Codex와 Claude 모두에서 동일한 구조로 Atlassian 작업을 안전하게 수행한다:
- 읽기: 이슈 확인/배치 조회
- 쓰기: description 업데이트, child task 생성
- 운영: 코멘트/전환/요구사항 분석
- 위키: 페이지 조회/검색/업데이트

## Execution Paths

### 1) API-first (권장)

아래 스크립트를 직접 실행한다.
- `scripts/jira_auth.py`
- `scripts/jira_verify_issue.py`
- `scripts/jira_batch_fetch.py`
- `scripts/jira_query_issues.py`
- `scripts/jira_update_issue_description.py`
- `scripts/jira_update_issue.py`
- `scripts/jira_create_issue.py`
- `scripts/jira_add_comment.py`
- `scripts/jira_transition_issue.py`
- `scripts/jira_epic_children.py`
- `scripts/jira_create_child_tasks.py`
- `scripts/jira_op_run.py`
- `scripts/wiki_auth.py`
- `scripts/wiki_verify_page.py`
- `scripts/wiki_search_pages.py`
- `scripts/wiki_update_page.py`

인증 입력:
- `JIRA_BASE_URL`
- `JIRA_EMAIL`
- `JIRA_API_TOKEN`
- `CONFLUENCE_BASE_URL` (미설정 시 `https://kidsnote.atlassian.net/wiki` 기본값 사용)
- `CONFLUENCE_EMAIL` / `CONFLUENCE_API_TOKEN` (미설정 시 Jira 자격증명 fallback)

### 2) 1Password bootstrap + single op run (권장)

반복 명령마다 secret reveal 하지 않는다.
- 한 번의 `jira_op_run.py`로 환경 주입
- 동일 프로세스에서 배치 실행

### 3) MCP (선택)

Claude에서 Jira MCP가 활성화돼 있으면 `jira_get_issue`, `jira_search`, `jira_add_comment`, `jira_transition_issue` 등을 사용할 수 있다.
Confluence MCP가 활성화돼 있으면 페이지 검색/조회/수정 경로도 선택적으로 사용할 수 있다.

### 4) Non-Claude -> Claude bridge (선택)

MCP 경로를 써야 하는 non-Claude 환경에서는 `scripts/run_claude_jira_task.sh`를 사용한다.
위키 작업은 `scripts/run_claude_wiki_task.sh`를 사용한다.

## Safe Workflow

항상 아래 순서를 지킨다.
1. `verify` (인증/대상 이슈 확인)
2. `dry-run` (쓰기 payload 확인 가능 시)
3. `apply` (실제 반영)
4. `verify` (반영 결과 재확인)

## Commands

```bash
# 1) 인증 확인
python3 scripts/jira_auth.py --verify
```

```bash
# 2) 단일 이슈 확인
python3 scripts/jira_verify_issue.py PK-12345
```

```bash
# 3) 1Password 기반 단일 op run + 배치 조회
python3 scripts/jira_op_run.py \
  --vault Personal \
  --item "JIRA - Kidsnote Atlassian" \
  --base-url https://kidsnote.atlassian.net \
  -- \
  python3 scripts/jira_batch_fetch.py PK-12345 PK-12346 --with-description
```

```bash
# 4) description 변경 dry-run
python3 scripts/jira_update_issue_description.py \
  PK-12345 \
  --adf-file references/jira-adf-template.md \
  --dry-run
```

```bash
# 5) 이슈 검색 (typed filter)
python3 scripts/jira_query_issues.py --project PK --status "In Progress" --days 7 --limit 20
```

```bash
# 6) 이슈 생성
python3 scripts/jira_create_issue.py \
  --project PK \
  --type Task \
  --summary "API 성능 개선" \
  --description "쿼리 최적화 작업"
```

```bash
# 7) 이슈 업데이트
python3 scripts/jira_update_issue.py PK-12345 --priority High --labels "ios,performance"
```

```bash
# 8) 코멘트 추가
python3 scripts/jira_add_comment.py PK-12345 --text "PR 생성 완료: https://github.com/..."
```

```bash
# 9) 상태 전환
python3 scripts/jira_transition_issue.py PK-12345 --status "In Review" --comment "리뷰 요청드립니다."
```

```bash
# 10) Epic + 하위 이슈 조회
python3 scripts/jira_epic_children.py PK-30299
```

```bash
# 11) child task 생성
python3 scripts/jira_create_child_tasks.py \
  PK-12345 \
  --items-file /tmp/jira-children.json
```

```bash
# 12) Non-Claude 환경에서 Claude bridge 사용 (선택)
bash scripts/run_claude_jira_task.sh --task "PK-12345 이슈 요약과 테스트 시나리오 정리"
```

```bash
# 13) 위키 인증 확인 (기본 URL: https://kidsnote.atlassian.net/wiki)
python3 scripts/wiki_auth.py --verify
```

```bash
# 14) 위키 페이지 조회
python3 scripts/wiki_verify_page.py 123456789
```

```bash
# 15) 위키 CQL 검색
python3 scripts/wiki_search_pages.py --cql "type = page AND title ~ \"offline cache\" ORDER BY lastmodified DESC" --limit 10
```

```bash
# 16) 위키 페이지 업데이트 dry-run
python3 scripts/wiki_update_page.py 123456789 --body-file /tmp/new-body.html --dry-run
```

```bash
# 17) Non-Claude 환경에서 Confluence bridge 사용 (선택)
bash scripts/run_claude_wiki_task.sh --task "최근 2주 URLCache 관련 위키 문서 검색 후 링크 목록 정리"
```

## Constraints

- 실행하지 않은 Jira 결과를 추측/생성하지 않는다.
- 쓰기 작업은 verify/dry-run 없이 바로 수행하지 않는다.
- secret을 repo/.ai/커밋/로그에 남기지 않는다.

## Resources

### scripts/
- `jira_auth.py`: Jira auth verify
- `jira_verify_issue.py`: 단일 이슈 조회
- `jira_batch_fetch.py`: 다중 이슈 조회
- `jira_query_issues.py`: JQL/typed filter 이슈 검색
- `jira_update_issue_description.py`: description 업데이트(ADF)
- `jira_update_issue.py`: summary/assignee/priority/labels/components 업데이트
- `jira_create_issue.py`: 일반 이슈 생성(Task/Bug/Story/Sub-task)
- `jira_add_comment.py`: 이슈 코멘트 추가
- `jira_transition_issue.py`: 상태 전환(전환명 기반)
- `jira_epic_children.py`: Epic + 하위 이슈 조회
- `jira_create_child_tasks.py`: child/sub-task 일괄 생성
- `jira_op_run.py`: 1Password `op run` wrapper
- `jira_bootstrap_1password.py`: bootstrap summary/env mapping
- `jira_1password.py`: 1Password provider wrapper
- `run_claude_jira_task.sh`: non-Claude -> Claude bridge
- `wiki_auth.py`: Confluence auth verify
- `wiki_verify_page.py`: 위키 페이지 단일 조회
- `wiki_search_pages.py`: 위키 CQL 검색
- `wiki_update_page.py`: 위키 페이지 body.storage 업데이트
- `run_claude_wiki_task.sh`: non-Claude -> Claude bridge for wiki

### references/
- `jira-adf-template.md`: description용 ADF 템플릿
- `wiki-cql-cheatsheet.md`: 위키 CQL 쿼리 예시
