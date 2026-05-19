# Review Current

현재 작업 diff를 리뷰한다. 리뷰 대상은 로컬 변경 또는 현재 브랜치에서 진행 중인 변경이다.

## Inputs

우선 가능한 범위에서 아래 문서를 읽는다.

- `ai/discovery.md`
- `ai/spec.md`
- `ai/plan.md`
- `AGENTS.md`

파일이 없으면 없는 상태를 간단히 기록하고, 현재 git diff와 주변 코드 컨텍스트를 기준으로 리뷰한다.

## Workflow

1. 현재 git 상태와 diff 범위를 확인한다.
2. `ai/plan.md`가 있으면 작업 유형을 판정한다.
3. 작업 유형에 맞는 리뷰 프로필을 적용한다.
4. 현재 git diff를 리뷰한다.
5. 결과를 `ai/review.md`에 한국어로 작성한다.

리뷰 중 구현을 직접 수정하지 않는다. Critical 수준의 결함이 있어도 수정 제안까지만 작성한다.

## Review Profiles

### 신규 기능

신규 기능 구현 diff를 리뷰할 때 적용한다.

Review responsibilities:

- detect architecture drift
- detect unintended side effects
- detect unnecessary complexity
- verify repository conventions
- verify scope discipline
- verify test coverage adequacy

Focus on:

- correctness
- maintainability
- runtime risk
- implementation consistency

### 버그 수정

버그 수정 diff를 리뷰할 때 적용한다.

Review responsibilities:

- verify the bug root cause from `ai/plan.md` is actually addressed
- detect architecture drift
- detect unintended side effects
- detect unnecessary complexity
- verify repository conventions
- verify scope discipline
- verify regression risk
- verify test coverage adequacy
- verify the fix has minimal blast radius

Focus on:

- correctness
- root-cause alignment
- regression prevention
- runtime risk
- implementation consistency
- minimal fix scope
- maintainability

Verify:

- the fix addresses the reported bug, not just the symptom
- no unrelated refactors were introduced
- no scope expansion exists
- existing behavior is preserved outside the bug path
- stacked PR integrity is preserved if applicable
- UIKit-only direction is preserved if applicable
- no accidental dependency or file leakage exists

### 크래시 수정

크래시 수정 diff를 리뷰할 때 적용한다.

Review responsibilities:

- verify the actual crash root cause is addressed
- detect crash masking or symptom-only fixes
- detect unintended side effects
- detect unnecessary complexity
- verify repository conventions
- verify scope discipline
- verify regression risk
- verify lifecycle/thread safety
- verify the fix has minimal blast radius

Focus on:

- crash prevention correctness
- root-cause alignment
- nilability / optional safety
- lifecycle timing safety
- thread/main-thread safety
- async callback safety if relevant
- Objective-C / Swift bridging safety if relevant
- regression prevention
- runtime risk
- implementation consistency
- minimal fix scope
- maintainability

Verify:

- the fix addresses the reported crash, not just the symptom
- no crash masking was introduced
- no unrelated refactors were introduced
- no scope expansion exists
- existing runtime behavior is preserved outside the crash path
- no new lifecycle/race-condition risks were introduced
- stacked PR integrity is preserved if applicable
- UIKit-only direction is preserved if applicable
- no accidental dependency or file leakage exists

### 버그 + UI 수정

버그 수정과 UI 변경이 함께 있는 diff를 리뷰할 때 적용한다.

Review responsibilities:

- verify only the current fix item was implemented
- detect unintended side effects
- detect unnecessary complexity
- verify repository conventions
- verify scope discipline
- verify minimal blast radius
- verify runtime/layout safety
- verify regression risk

Focus on:

- correctness
- root-cause alignment if this is a bug fix
- Figma/UI alignment if this is a UI adjustment
- layout consistency
- runtime behavior preservation
- implementation consistency
- minimal diff size
- reviewable commit scope

Verify:

- no future fix items were included
- no unrelated refactors were introduced
- no unrelated visual cleanup exists
- existing runtime behavior outside the target area is preserved
- UIKit-only direction is preserved if applicable
- modified files match the planned scope from `ai/plan.md`

## Finding Classification

Classify findings as:

- `BLOCKING`: 반드시 수정해야 하는 정확성, 크래시, 데이터 손실, 보안, 심각한 회귀 위험
- `SHOULD FIX`: 병합 전 수정 권장. 유지보수성, 범위 이탈, 테스트 공백, 중간 수준 회귀 위험
- `OPTIONAL`: 개선 제안. 현재 변경의 안전성에는 직접 영향이 작음

## Do Not Run

리뷰 세션에서는 아래 명령을 실행하지 않는다.

- builds
- compile checks
- tests
- simulators
- `xcodebuild`
- `fastlane`
- `pod install`
- `bundle install`
- dependency installation
- runtime commands

Human performs runtime/build validation separately.

## Output

`ai/review.md`를 한국어로 작성한다. 기술 식별자는 필요할 때 English를 유지한다.

권장 형식:

```markdown
# 코드 리뷰 결과

## 검토 범위
- 대상: 현재 git diff
- 기준 문서: ai/discovery.md, ai/spec.md, ai/plan.md, AGENTS.md

## Findings

### 이슈 1: {한 줄 제목}
- **위치**: [{파일}:{라인}]
- **관점**: Security/Performance/Maintainability/Dependency
- **심각도**: Critical/High/Medium/Low

**현재 상태 (무엇이 문제인가)**

> 현재 코드가 어떻게 동작하는지 설명. 변경된 코드를 인용하며 구체적으로 작성.
> swift
> // 문제가 되는 코드 인용
> 

**왜 문제인가**

> 어떤 시나리오에서 어떤 부작용이 발생하는지 구체적으로 설명.
> 예: "사용자가 A 화면에서 B를 탭했을 때, C 때문에 D가 발생할 수 있습니다."

**수정 제안**

> 구체적인 수정 방향과 가능하면 코드 예시 제공.
> swift
> // 수정 예시
> 

---

(이슈 반복)

---
```

각 finding에는 다음 내용을 포함한다.

- 현재 상태
- 문제점과 위험
- 수정 제안