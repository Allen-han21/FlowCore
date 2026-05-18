---
name: prompt-factory
description: Generate standardized prompts for discover/spec/plan/implement/review/advisory/reconcile/git stages using reusable template IDs and variable substitution. Use when a team needs consistent workflow prompts (for Codex, Claude, or Gemini), strict role boundaries, minimal-scope instructions, and artifact-centric outputs such as ai/discovery.md, ai/spec.md, ai/plan.md, ai/review.md, and ai/gemini-review.md.
---

# Prompt Factory

## Overview

Use this skill to create high-consistency prompts from template IDs instead of manually writing long prompts.
It standardizes role boundaries (discover/spec/plan/implement/review/git), output artifacts, and "do-not-run" constraints.

Recommended workflow for short natural-language requests:
- `discover.*` -> `spec.*` -> `plan.*` -> `implement.*` -> `review.*`

## Workflow

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

### references/

- `references/template-catalog.md`: consolidated prompt templates and placeholder guide.
