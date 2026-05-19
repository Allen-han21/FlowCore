---
name: prompt-factory
description: Generate standardized prompts for discover/spec/plan/ticket/implement/review/advisory/reconcile/git stages using reusable template IDs and variable substitution. Use when a team needs consistent workflow prompts (for Codex, Claude, or Gemini), strict role boundaries, minimal-scope instructions, and artifact-centric outputs such as ai/discovery.md, ai/spec.md, ai/plan.md, ai/ticket.md, ai/review.md, and ai/gemini-review.md.
---

# Prompt Factory

## Overview

Use this skill to create high-consistency prompts from template IDs instead of manually writing long prompts.
It standardizes role boundaries (discover/spec/plan/ticket/implement/review/git), output artifacts, and "do-not-run" constraints.

Recommended workflow for short natural-language requests:
- `discover.*` -> `spec.*` -> `plan.*` -> `ticket.*` -> `implement.*` -> `review.*`

For semantic risk-heavy tasks, run symbol pass before planning:
- `discover.symbols` -> `spec.*` -> `plan.*`

## DISCOVER 선행 게이트

아래 중 하나라도 해당하면 `plan.*`로 바로 가지 말고 `discover.*`를 먼저 실행한다.

1. 기존 대형 프로젝트 영향 범위가 넓다
2. 요청이 1~3줄 자연어 수준이다
3. 관련 파일/화면/도메인이 명확하지 않다
4. 서버/API/캐시/인증/보안/오프라인/성능이 관련된다
5. 기존 아키텍처를 먼저 파악해야 한다
6. "안정성 향상", "성능 개선", "구조 개선", "캐시 개선"처럼 추상도가 높다
7. 여러 레이어가 걸릴 가능성이 있다
8. Slack/Jira/Figma/스크린샷 같은 외부 맥락이 필요하다
9. 잘못 설계하면 변경 범위가 커질 수 있다
10. 사용자가 구체 수정 위치보다 개선 목표만 제시했다

게이트 충족 시 기본 순서:
- `discover.*` -> `spec.from-discovery` -> `plan.from-discovery`

Product Context precheck 기본 원칙:
- Slack/Jira/wiki/PRD/Figma/스크린샷 근거를 보기 전에, 최근 2주 관련 대화부터 우선 확인한다.
- Slack 링크 조회가 필요하면 parent message만 보지 말고 thread reply까지 전체 확인한다.
- 대화 내 URL 링크/첨부 파일이 있으면 추출해서 해당 artifact까지 조회하고 확인 결과를 기록한다.

## Workflow

### Step 0: Route from natural-language request (recommended)

When input is a short or ambiguous request, route by context sufficiency first:

```bash
python3 scripts/route_prompt.py \
  "iOS 앱 URL 캐시로 안정성 향상 - 네트워크 불안정 상황에서도 기존 데이터로 안정적인 서비스 제공"
```

- Router priority: `DISCOVER` -> `REVIEW` -> `TICKET` -> `IMPLEMENT` -> `SPEC` -> `PLAN`
- If any DISCOVER gate condition matches, router forces `discover.*` first
- Router prints `intent`, `template_id`, and `reason`, then renders prompt automatically

### Step 1: Pick the stage template ID

Use `scripts/list_templates.py` to discover template IDs.

```bash
python3 scripts/list_templates.py
```

### Step 2: Render the prompt with variables

Use `scripts/render_prompt.py` with required variables.

```bash
python3 scripts/render_prompt.py \
  --template-id plan.bug \
  --var task="초등 타입 원장 계정 출석부 삭제 팝업 문구 수정" \
  --var base_branch="feature/freezing-2026.513.0/main" \
  --var working_branch="feature/freezing-2026.513.0/PK-35750"
```

Validated auto-improvement (optional):

```bash
python3 scripts/render_prompt.py \
  --template-id plan.bug \
  --var task="초등 타입 원장 계정 출석부 삭제 팝업 문구 수정" \
  --improve \
  --print-improve-report
```

- `--improve`: LLM이 문구를 개선 시도
- 검증 통과 시에만 개선본 채택
- 검증 실패 시 원본 템플릿으로 자동 폴백
- `--strict-improve`: 실패 시 폴백하지 않고 에러로 종료

### Step 3: Use the output in the target harness

- Codex: paste the output prompt as the task input.
- Claude: paste the output prompt into the session or a command wrapper.
- Gemini: use advisory/review templates only.

## Template Groups

- Planning: `plan.*`
- Discovery/Spec: `discover.*`, `spec.*`
- Ticket: `ticket.*`
- Implementation: `implement.*`
- Review: `review.*`
- Advisory review: `advisory.*`
- Reconciliation / re-review: `reconcile.*`, `rereview.*`
- Git: `git.*`

Detailed content and placeholders are in `references/template-catalog.md`.

## Constraints

- Keep Korean prose for explanations.
- Keep technical identifiers in English.
- Enforce minimal blast radius and no scope expansion unless explicitly requested.
- Do not include runtime/build command execution unless the template explicitly allows it.
- In discovery/spec stages, do not implement code and do not finalize architecture plan.
- Improvement mode must preserve required sections and safety guards; otherwise fallback.

## Resources

### scripts/

- `scripts/list_templates.py`: print available template IDs and required vars.
- `scripts/render_prompt.py`: render a template into final prompt text using `--var key=value`.
  - Output file is fixed to `compiled-prompt.txt`.
- `scripts/route_prompt.py`: route natural language request by context sufficiency and render the selected template.

### references/

- `references/template-catalog.md`: consolidated prompt templates and placeholder guide.
