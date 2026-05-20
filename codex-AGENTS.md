# Agent Workflow

Use this workflow strictly.

---

# Workflow

1. Codex normalizes raw request context in `ai/context.md` when input comes from Slack, Jira, screenshot, voice-like text, or mixed notes.
2. Codex creates discovery/spec artifacts in `ai/discovery.md` and `ai/spec.md` when context is broad, risky, or unclear.
3. Codex creates architecture and implementation plan in `ai/plan.md`.
4. Human approves `ai/plan.md` before implementation starts.
5. Claude Code implements strictly according to `ai/plan.md`.
6. Codex performs primary review in `ai/review.md`.
7. Gemini performs advisory review only in `ai/gemini-review.md`.
8. Codex reconciles review feedback and decides which comments are actionable.
9. Blocking review findings go to Fix Implementation, then back to Primary Review.
10. Human performs runtime validation and functional verification.
11. Runtime failures are recorded in `ai/runtime-findings.md`.
12. Runtime failures with unclear root cause go back to Discover; clear implementation defects go to Fix Implementation, then back to Primary Review.
13. ECC/CI quality gate must pass before merge.
14. Human performs final approval and merge.

---

# Roles

## Codex

Responsibilities:

- context normalization
- discovery and spec drafting
- architecture design
- implementation planning
- primary code review
- review reconciliation
- runtime finding triage
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
- runtime failure routing
- merge readiness

---

## Claude Code

Role:

- implementer only

Claude Code must:

- implement only what is defined in `ai/plan.md`
- implement accepted fixes from `ai/review.md` / reconciliation only when explicitly routed to Fix Implementation
- implement runtime fixes from `ai/runtime-findings.md` only when root cause is clear and within approved scope
- preserve existing architecture and repository patterns
- keep changes minimal and focused
- update/add tests when necessary
- summarize modified files and implementation details

Claude Code must not:

- redesign architecture
- resolve unclear runtime failures by guessing
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

# Context Normalize

Use `ai/context.md` before discovery when the input is raw or mixed-context:

- Slack thread
- Jira ticket
- screenshot or Figma note
- voice-like natural language
- pasted conversation
- ambiguous product/runtime request

`ai/context.md` must separate:

- original request
- source/evidence
- confirmed facts
- inferred assumptions
- product/runtime expectation
- open questions
- suggested discovery targets

Context Normalize must not create architecture decisions or implementation plans.

---

# Loop Rules

## Review Loop

The review loop is:

```text
Primary Review
→ Advisory Review
→ Reconciliation
→ Blocking?
→ Fix Implementation
→ Primary Review
```

Reconciliation is a decision step only. It must not be treated as the implementation fix.

## Runtime Failure Loop

The runtime failure loop is:

```text
Runtime Validation
→ Runtime Findings
→ Root cause unclear?
→ Discover or Fix Implementation
→ Primary Review
```

Runtime failures must be written to `ai/runtime-findings.md` before routing.

Route runtime failure to Discover when:

- API contract assumptions are wrong or incomplete
- lifecycle/timing assumptions are wrong
- cache invalidation or async ordering assumptions are wrong
- product/runtime expectation is unclear
- fixing would require scope expansion beyond `ai/plan.md`

Route runtime failure to Fix Implementation when:

- root cause is clear
- fix stays within approved plan/spec scope
- no architecture or product decision is required

---

# State Machine Direction

FlowCore state should be represented as explicit workflow state, not inferred from chat history.

Recommended shape:

```yaml
state:
  current: review
  previous: implementation
  blocked: false
  plan_approved: true
  runtime_verified: false
  merge_approved: false
artifacts:
  context: ai/context.md
  discovery: ai/discovery.md
  spec: ai/spec.md
  plan: ai/plan.md
  review: ai/review.md
  advisory_review: ai/gemini-review.md
  runtime_findings: ai/runtime-findings.md
```

Future `fc next` behavior should choose the next command from explicit state and artifact availability.

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
- clear runtime findings that remain inside approved scope

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
- runtime findings remain unresolved
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
