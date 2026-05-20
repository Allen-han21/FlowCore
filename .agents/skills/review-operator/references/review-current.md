# Review Current

`/review current`는 현재 작업 diff를 FlowCore 문서 기준으로 리뷰하고 `ai/review.md`를 작성하는 읽기 중심 자동화다.

이 모드는 GitHub 제출, commit, push, PR 생성, 구현 수정을 수행하지 않는다.

## Inputs

아래 입력을 순서대로 확인한다.

1. `ai/context.md`가 있으면 읽는다.
2. `ai/discovery.md`가 있으면 읽는다.
3. `ai/spec.md`가 있으면 읽는다.
4. `ai/plan.md`는 반드시 읽는다.
5. `AGENTS.md`를 읽는다.
6. 현재 git 상태와 diff를 확인한다.

`ai/plan.md`가 없으면 리뷰 기준이 없으므로 일반 코드 리뷰를 진행하지 않는다. 이 경우 `ai/review.md`에 `BLOCKING` 사전조건 실패로 기록하고 중단한다.

`ai/discovery.md`, `ai/spec.md`, `AGENTS.md`가 없으면 `ai/review.md`의 입력 상태에 누락 사실을 기록하고, 남은 입력만으로 리뷰한다.

## Workflow

1. 입력 문서 상태를 확인한다.
2. `ai/plan.md`에서 구현 범위, out-of-scope, root cause, verification contract를 추출한다.
3. `ai/spec.md`가 있으면 runtime contract와 expected behavior를 추출한다.
4. `ai/discovery.md`가 있으면 known risk, 기존 제약, 확인된 원인을 추출한다.
5. `ai/context.md`가 있으면 normalized request, product expectation, confirmed facts를 추출한다.
6. `AGENTS.md`가 있으면 repo-local 실행 규칙과 금지 사항을 추출한다.
7. 현재 git 상태와 diff 범위를 확인한다.
8. context / spec / plan / discovery 기준으로 현재 diff를 리뷰한다.
9. 결과를 `ai/review.md`에 한국어로 작성한다.

리뷰 중 구현을 직접 수정하지 않는다. Critical 수준의 결함이 있어도 수정 제안까지만 작성한다.

## Git Context

현재 diff 확인에는 아래 정보를 사용한다.

- `git status --short`
- `git diff --stat`
- `git diff --cached --stat`
- `git diff`
- `git diff --cached`

staged 변경과 unstaged 변경을 모두 리뷰한다. 변경이 없으면 `ai/review.md`에 리뷰 대상 없음으로 기록한다.

## Review Contract

반드시 확인한다.

- `ai/context.md` normalized request / product expectation 위반 여부
- `ai/spec.md` runtime contract 준수 여부
- `ai/plan.md` 구현 범위 준수 여부
- `ai/discovery.md` known risk 위반 여부
- root cause 해결 여부
- scope expansion 여부
- unrelated refactor 여부
- runtime behavior 보존 여부

문서가 없는 기준은 추측으로 보완하지 않는다. 누락된 기준은 `Input Status` 또는 `Residual Risk`에 명시한다.

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

- Claude CLI 자동 구현 실행
- Gemini 자동 실행
- commit 자동화
- PR 생성 자동화
- GitHub review 제출 자동화
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

## Input Status
- `ai/context.md`: found | missing
- `ai/discovery.md`: found | missing
- `ai/spec.md`: found | missing
- `ai/plan.md`: found | missing
- `AGENTS.md`: found | missing

## 검토 범위
- 대상: 현재 git diff
- 기준 문서: ai/context.md, ai/discovery.md, ai/spec.md, ai/plan.md, AGENTS.md
- 변경 파일:
  - {파일 경로}

## 기준 요약
- Plan scope: {ai/plan.md에서 확인한 범위}
- Normalized context: {ai/context.md에서 확인한 요청 또는 missing}
- Runtime contract: {ai/spec.md에서 확인한 계약 또는 missing}
- Known risk: {ai/discovery.md에서 확인한 위험 또는 missing}

## 결론
- Blocking: {count}
- Should Fix: {count}
- Optional: {count}
- Merge readiness: ready | not ready | blocked by missing input

## Findings

### 이슈 1: {한 줄 제목}
- **위치**: [{파일}:{라인}]
- **관점**: Correctness/Runtime Risk/Scope/Architecture/Test/Dependency
- **심각도**: BLOCKING/SHOULD FIX/OPTIONAL

**현재 상태 (무엇이 문제인가)**

현재 코드가 어떻게 동작하는지 설명. 변경된 코드를 필요한 만큼만 짧게 인용한다.

**왜 문제인가**

어떤 기준 문서와 충돌하는지, 어떤 시나리오에서 어떤 부작용이 발생할 수 있는지 구체적으로 설명한다.

**수정 제안**

구체적인 수정 방향을 제안한다. 직접 수정하지 않는다.

---

(이슈 반복)

---

## Residual Risk
- 실행하지 않은 검증:
- 누락된 입력:
- 사람이 확인해야 할 runtime/UI 항목:
```

각 finding에는 다음 내용을 포함한다.

- 현재 상태
- 문제점과 위험
- 수정 제안
