# Template Catalog

## Common Blocks

- `COMMON_USE`: `AGENTS.md`, 기존 패턴, 현재 아키텍처
- `COMMON_DISCOVER_RULES`: discovery 단계의 비구현/비추측/열린 질문 규칙 + Product Context 선조회 규칙
- `COMMON_NO_RUN`: build/test/simulator/xcodebuild/fastlane/runtime 실행 금지
- `COMMON_IMPLEMENT_RULES`: minimal scope, no unrelated refactor, no redesign
- `COMMON_REVIEW_CLASSIFICATION`: BLOCKING / SHOULD FIX / OPTIONAL
- `COMMON_ADVISORY_CLASSIFICATION`: SHOULD FIX / OPTIONAL

## Product Context Precheck Policy (Discover)

- 사용자에게 추가 입력을 요청하기 전에 먼저 Slack/Jira/wiki/PRD/Figma/screenshot evidence를 repo/doc context에서 탐색한다.
- Product Context에서는 최근 2주 관련 대화(Slack thread, Jira comment, design discussion log)를 먼저 찾는다.
- Slack 링크 조회가 필요하면 해당 message와 thread reply를 함께 조회한다.
- 대화 내용에 URL 링크/첨부 파일이 있으면 추출 후 실제 artifact를 조회해 확인한다.
- 접근 가능한 근거는 `Confirmed Facts`로 반영한다.
- 링크 부재/권한 제한으로 확인 불가한 항목은 `Blocked`로 이유를 명시한다.
- discovery 산출물에는 "무엇을 먼저 확인했는지(검색 패턴/경로)"를 로그로 남긴다.

## DISCOVER First Gate

아래 중 하나라도 해당하면 DISCOVER가 먼저다.

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

권장 체인:
- `discover.*` -> `spec.from-discovery` -> `plan.from-discovery`

## Template IDs

### Discover / Spec

- `discover.general` (required: `task`)
- `discover.ios-cache` (required: `task`)
- `discover.symbols` (required: `task`)
- `spec.from-discovery` (required: `task`)

### Plan

- `plan.from-discovery` (required: `task`)
- `plan.feature` (required: `task`)
- `plan.bug` (required: `task`)
- `plan.crash` (required: `crash_symptom`, optional: `crash_context`)
- `plan.build-failure` (required: `build_error`)
- `plan.pr-split` (required: `task`, `context`)
- `plan.ui-sequential` (required: `task`, `items`)
- `plan.bug-ui` (required: `task`, `items`, `base_branch`, `working_branch`)
- `plan.redesign` (required: `task`, `items`, `context`)

### Ticket

- `ticket.from-plan` (required: `task`)

### Implement

- `implement.feature` (required: `task`)
- `implement.bug`
- `implement.crash`
- `implement.ui-sequential` (required: `current_item`)
- `implement.redesign` (required: `current_item`)

### Review / Advisory / Reconcile

- `review.feature`
- `review.bug`
- `review.crash`
- `advisory.general`
- `reconcile.general`
- `rereview.general`

### Git

- `git.commit` (required: `base_branch`, `new_branch`, `ticket`; optional: `commit_subject`)

## Usage Examples

```bash
python3 scripts/list_templates.py
```

```bash
python3 scripts/route_prompt.py \
  "iOS 앱 URL 캐시로 안정성 향상 - 네트워크 불안정 상황에서도 기존 데이터로 안정적인 서비스 제공"
```

```bash
python3 scripts/render_prompt.py \
  --template-id discover.general \
  --var task="iOS 앱 URL 캐시로 안정성 향상"
```

```bash
python3 scripts/render_prompt.py \
  --template-id spec.from-discovery \
  --var task="iOS 앱 URL 캐시로 안정성 향상"
```

```bash
python3 scripts/render_prompt.py \
  --template-id discover.symbols \
  --var task="iOS 앱 URL 캐시로 안정성 향상"
```

```bash
python3 scripts/render_prompt.py \
  --template-id plan.crash \
  --var crash_symptom="특정 화면 진입 시 SIGABRT 발생" \
  --var crash_context="stack trace: ... / repro: ..."
```

```bash
python3 scripts/render_prompt.py \
  --template-id plan.bug \
  --var task="출석부 삭제 팝업 문구 수정" \
  --improve \
  --print-improve-report
```

```bash
python3 scripts/render_prompt.py \
  --template-id ticket.from-plan \
  --var task="iOS 앱 URL 캐시 안정성 향상 협업 티켓 초안 작성"
```

```bash
python3 scripts/render_prompt.py \
  --template-id git.commit \
  --var base_branch="feature/freezing-2026.513.0/main" \
  --var new_branch="feature/freezing-2026.513.0/PK-35723" \
  --var ticket="PK-35723" \
  --var commit_subject="출석부 삭제 팝업 문구 수정"
```

## Improvement Validation Policy

- Improvement is optional (`--improve`).
- Output file is fixed to `compiled-prompt.txt`.
- Candidate prompt is accepted only if it preserves:
  - required section headers
  - safety guard lines (`do not ...`)
  - `Do not run` command block entries
  - artifact path mentions like `ai/plan.md`
- Validation failure triggers automatic fallback to base template output.
- Use `--strict-improve` when CI must fail on invalid improvements.
