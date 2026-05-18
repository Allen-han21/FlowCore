# Agent Workflow

Use this workflow strictly.

---

# Workflow

1. Codex creates architecture and implementation plan in `ai/plan.md`.
2. Claude Code implements strictly according to `ai/plan.md`.
3. Human performs runtime validation and functional verification.
4. Codex performs primary review in `ai/review.md`.
5. Gemini performs advisory review only in `ai/gemini-review.md`.
6. Codex decides which Gemini comments are actionable.
7. ECC/CI quality gate must pass before merge.
8. Human performs final approval and merge.

---

# Roles

## Codex

Responsibilities:

- architecture design
- implementation planning
- primary code review
- final verification
- architectural consistency validation
- drift detection

Codex review must verify:

- implementation matches `ai/plan.md`
- no architectural drift exists
- no unintended side effects exist
- no unnecessary complexity was introduced
- existing project conventions are preserved
- runtime risk is acceptable
- tests adequately cover modified behavior

Codex has final authority on:

- architecture decisions
- implementation scope
- review acceptance
- merge readiness

---

## Claude Code

Role:

- implementer only

Claude Code must:

- implement only what is defined in `ai/plan.md`
- preserve existing architecture and repository patterns
- keep changes minimal and focused
- update/add tests when necessary
- summarize modified files and implementation details

Claude Code must not:

- redesign architecture
- introduce unrelated refactors
- modify files outside planned scope
- change public APIs without explicit approval
- add dependencies unless planned
- introduce large abstractions without justification
- perform speculative optimization
- expand scope beyond `ai/plan.md`

---

## Gemini

Role:

- advisory reviewer only

Gemini responsibilities:

- edge case detection
- regression risk suggestions
- broad consistency review
- alternative implementation observations

Gemini feedback:

- is advisory only
- must not override Codex architectural decisions
- must not directly change implementation scope

Codex decides whether Gemini feedback is actionable.

---

## ECC / CI

Role:

- automated quality gate

ECC/CI must validate:

- lint
- typecheck
- tests
- formatting
- repository rules
- predefined hooks/checklists

ECC/CI failure blocks merge.

---

## Human

Human validation is required for:

- runtime behavior
- UI/UX correctness
- production-sensitive flows
- architecture changes
- business logic validation
- release readiness

Human has final merge authority.

---

# Development Principles

## Small Iterative Changes

Prefer:

- small diffs
- incremental improvements
- isolated feature changes
- short review cycles

Avoid:

- large multi-feature implementations
- broad refactors without explicit planning
- mixed-scope pull requests

---

## Architecture Preservation

Implementation must preserve:

- existing repository conventions
- existing architectural boundaries
- existing dependency structure
- existing runtime behavior unless explicitly planned

---

## Scope Discipline

Implementation scope is defined only by:

- `ai/plan.md`
- approved follow-up review decisions

Any additional scope requires explicit approval.

---

# Merge Blocking Conditions

Do not merge if:

- tests fail
- lint/typecheck fails
- ECC/CI fails
- Codex review has blocking issues
- implementation deviates from `ai/plan.md`
- runtime behavior is unverified
- reviewer scope is incomplete
- unexplained complexity was introduced
- architecture drift is detected
- production risk is unclear

---

# Source of Truth

The following order defines execution authority:

1. Current task prompt
2. `ai/plan.md`
3. Project repository conventions
4. Project-local agent/rules configuration
5. Global tool configuration

If conflicts occur, follow the highest-priority source.

---

# Operational Philosophy

This workflow is designed for:

- controlled AI-assisted engineering
- architecture stability
- deterministic review flow
- minimal implementation drift
- production-safe iteration

This is not a fully autonomous coding system.

Human oversight remains mandatory.
