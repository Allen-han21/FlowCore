# Template Catalog

## Common Blocks

- `COMMON_USE`: `AGENTS.md`, 기존 패턴, 현재 아키텍처
- `COMMON_DISCOVER_RULES`: discovery 단계의 비구현/비추측/열린 질문 규칙
- `COMMON_NO_RUN`: build/test/simulator/xcodebuild/fastlane/runtime 실행 금지
- `COMMON_IMPLEMENT_RULES`: minimal scope, no unrelated refactor, no redesign
- `COMMON_REVIEW_CLASSIFICATION`: BLOCKING / SHOULD FIX / OPTIONAL
- `COMMON_ADVISORY_CLASSIFICATION`: SHOULD FIX / OPTIONAL

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
