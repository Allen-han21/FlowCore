# FlowCore

> 계획 기반 AI 엔지니어링 워크플로우 오케스트레이션 시스템

FlowCore는 AI를 활용한 소프트웨어 개발을 위한 workflow architecture 입니다.

핵심 목표는:
- workflow orchestration
- agent 역할 분리
- review governance
- sequential PR integrity
- runtime-risk-oriented validation
- prompt compilation

입니다.

FlowCore의 목표는 AI를 “더 똑똑하게” 만드는 것이 아닙니다.

대신 엔지니어링 workflow를:
- 재현 가능하게
- 리뷰 가능하게
- 안정적으로
- low-risk 하게
- 운영 가능하게

만드는 것입니다.

---

# Philosophy

FlowCore는 하나의 핵심 원칙 위에서 설계되었습니다.

> 좋은 AI 엔지니어링은  
> 좋은 프롬프트가 아니라  
> 좋은 workflow architecture 에서 나온다.

FlowCore는 다음을 중요하게 생각합니다.

- 구현보다 계획 우선
- 역할 분리
- strict scope discipline
- runtime safety
- review quality
- orchestration consistency

FlowCore는 프롬프트를 단순 채팅 입력이 아니라:

```text
execution artifact
```

로 다룹니다.

---

# Core Concepts

## 1. Plan-Driven Development

모든 구현은 계획(plan)에서 시작됩니다.

```text
plan
→ implement
→ review
→ advisory review
→ reconciliation
→ runtime validation
→ commit
→ PR
```

구현 agent는:
- 계획 범위를 벗어나지 않고
- scope expansion 을 피하며
- architecture drift 를 방지하고
- speculative refactoring 을 하지 않아야 합니다.

---

## 2. Agent Responsibility Separation

각 agent는 서로 다른 역할을 가집니다.

| 역할 | 책임 |
|---|---|
| Architect | 계획 및 workflow 설계 |
| Implementer | 구현 |
| Reviewer | correctness/runtime validation |
| Advisory Reviewer | edge-case/runtime inconsistency 탐지 |
| Reconciliation Authority | 최종 판단 |

예시 orchestration:

```text
Codex
→ architecture planning

Claude
→ implementation

Codex
→ review validation

Gemini
→ advisory runtime review

Codex
→ final reconciliation
```

---

## 3. Workflow State as Files

FlowCore는 파일 자체를 workflow state 로 사용합니다.

```text
ai/
  plan.md
  review.md
  gemini-review.md
  review-summary.md
  pr-review-plan.md
```

workflow는 chat history 가 아니라:
- 계획 문서
- 리뷰 결과
- review queue
- execution state

를 기반으로 동작합니다.

---

## 4. Prompt Compilation

사람이 긴 프롬프트를 반복 작성하지 않도록 설계합니다.

FlowCore는:
- workflow state
- current PR
- current task
- review queue
- execution context

를 기반으로 프롬프트를 자동 생성하는 방향을 목표로 합니다.

예시 command:

```bash
fc plan
fc implement
fc review
fc gemini
fc reconcile
fc summary
fc commit
```

workflow compiler 는:
- template 선택
- context 주입
- execution rule 유지
- workflow boundary enforcement

를 담당합니다.

---

# Review Architecture

FlowCore는 리뷰 역할을 강하게 분리합니다.

## Primary Review

중점:
- correctness
- architecture consistency
- runtime safety
- regression prevention

---

## Advisory Review

중점:
- edge cases
- runtime inconsistencies
- lifecycle issues
- sequential PR risks
- hidden coupling

---

## Final Reconciliation

중점:
- actionable decisions
- severity validation
- merge readiness
- review governance

---

# Sequential PR Support

FlowCore는:
- stacked PR
- sequential feature delivery
- migration workflow
- dependency-aware review execution

을 고려하여 설계되었습니다.

시스템은:
- PR isolation
- runtime consistency
- review ordering
- cross-PR validation

을 유지하려고 합니다.

---

# Design Principles

## Scope Discipline

다음을 방지하는 것을 중요하게 생각합니다.

- mixed-scope commit
- speculative cleanup
- architecture drift
- unnecessary abstraction
- hidden coupling

---

## Runtime Safety First

리뷰는 다음을 우선 검증합니다.

- lifecycle correctness
- async timing stability
- rendering consistency
- state synchronization
- performance-sensitive flow
- regression prevention

---

## Human-in-the-Loop

사람은 여전히 다음 책임을 가집니다.

- runtime validation
- product decision
- merge approval
- workflow supervision

FlowCore는 엔지니어링 workflow를 보조합니다.

사람의 엔지니어링 판단을 대체하지 않습니다.

---

# Current Focus Areas

현재 주요 관심 영역:

- iOS UIKit workflow
- AI-assisted review system
- sequential PR orchestration
- workflow-driven development
- prompt compilation
- runtime-risk-oriented review pipeline

---

# Future Directions

향후 방향성:

- workflow DSL
- command runtime
- prompt compiler
- PR dependency graph
- automated review queue orchestration
- runtime validation checklist
- workflow state engine
- multi-agent execution runtime

---

# Example Workflow

## Bug Fix Workflow

```text
Slack request
→ normalize task
→ architecture planning
→ implementation
→ review
→ advisory review
→ reconciliation
→ runtime validation
→ commit
→ PR
```

---

## Sequential UI Workflow

```text
UI item 1
→ plan
→ implement
→ review
→ commit

UI item 2
→ repeat
```

원칙:
- one item per commit
- one review lifecycle per PR

---

# Non-Goals

FlowCore는 다음을 목표로 하지 않습니다.

- autonomous coding agent
- no-human coding system
- prompt collection repository
- architecture replacement tool

FlowCore는:

```text
engineering workflow system
```

입니다.

---

# License

MIT
