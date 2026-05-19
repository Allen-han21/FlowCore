---
name: review
description: 코드 리뷰. 내 작업(현재 브랜치 vs develop) 또는 남의 PR(번호/URL 지정)을 리뷰. "리뷰해줘", "리뷰", "코드 리뷰", PR URL(github.com/.../pull/N), "PR 리뷰" 요청 시 사용.
allowed-tools: Bash(git:*), Bash(gemini *), Read, Grep, Glob, Agent
---

# Skill: iOS 코드 리뷰 (/review)

## 공통 입력

리뷰 시작 전 프로젝트 루트의 `AGENTS.md`를 반드시 읽고 따른다.

## 모드 선택 [필수, 최우선]

인자에 모드가 명시되지 않으면 **반드시 사용자에게 먼저 질문**한다:

> **리뷰 모드를 선택해주세요:**
> - **Light** — Codex/Claude 단독, Critical/High만, 빠르게
> - **Full** — Codex/Claude + Gemini 병렬, 전체 심각도, 상세하게

| 인자 | 동작 |
|------|------|
| `/review` | 모드 질문 |
| `/review light` 또는 `/review light #7634` | Light 모드 바로 실행 |
| `/review full` 또는 `/review full #7634` | Full 모드 바로 실행 |
| `/review #7634` | 모드 질문 (PR 번호 기억 후 진행) |

---

## Light 모드

Codex/Claude 단독으로 **Critical/High 이슈만** 빠르게 찾습니다. Medium/Low는 무시.
리뷰는 반드시 Codex, Claude 고성능 Agent를 실행한다.

### Phase 2 (Light): Codex/Claude 단독 리뷰

```
Agent(
  description: "code review codex claude light",
  mode: "plan",
  prompt: """
  iOS 코드 리뷰를 수행하라.
  프로젝트 루트의 AGENTS.md를 반드시 읽고 따른다.
  review-diff.patch 파일을 읽어라.

  [모드: Light — Critical/High만]
  아래 4개 관점에서 **Critical 또는 High 심각도 이슈만** 찾아라.
  Medium/Low는 무시하라.

  1. Security  2. Performance  3. Maintainability  4. Dependency

  버그, 크래시, 보안 취약점, 데이터 손실 위험에 집중하라.
  접근 금지: Pods/, DerivedData/, Tuist/Dependencies/, ExternalLibraries/, Libraries/
  필요하면 실제 소스 파일도 읽어서 컨텍스트를 파악하라.

  출력은 한국어. 이슈가 없으면 "Critical/High 이슈 없음 ✅"으로 끝내라.
  이슈가 있으면 [{파일}:{라인}] 형식으로 간결하게 나열하되,
  각 이슈에 (1) 현재 상태, (2) 문제점, (3) 수정 제안을 포함하라.
  """
)
```

### Phase 3 (Light): 결과 출력

Codex/Claude 결과를 바로 출력한다. 종합 과정 없음.

```markdown
# 코드 리뷰 결과 (Light)

## 검토 범위
- 브랜치: {branch_name}
- 리뷰어: Codex/Claude (Light 모드)

## Critical/High 이슈
(이슈 나열 또는 "Critical/High 이슈 없음 ✅")

## 요약
| 관점 | Critical | High |
|------|----------|------|
| Security | 0 | 0 |
| Performance | 0 | 0 |
| Maintainability | 0 | 0 |
| Dependency | 0 | 0 |
```

---

## Full 모드

현재 브랜치에서 작업한 내역을 **Codex/Claude + Gemini 병렬 리뷰**로 검토합니다.

## PR 번호 지정 리뷰 (다른 사람 PR)

`/review #7534 #7533` 처럼 PR 번호가 인자로 전달된 경우:

### diff 수집
```bash
# PR별 diff를 하나의 파일로 합침
gh pr diff {PR번호} --repo kidsnote/kidsnote_ios > review-diff.patch
# 여러 PR이면 append
gh pr diff {PR번호2} --repo kidsnote/kidsnote_ios >> review-diff.patch
```

### 이후 절차
- Phase 2 (병렬 리뷰), Phase 3 (결과 종합)은 동일
- **결과는 반드시 사용자에게 먼저 보여주고, 승인 후에만 GitHub에 등록한다** (바로 올리지 않는다)
- 리뷰 코멘트를 GitHub에 올리기 전 **기존 코멘트 중복 여부 체크** 필수:
  ```bash
  gh api repos/kidsnote/kidsnote_ios/pulls/{PR번호}/comments
  # 또는
  gh pr view {PR번호} --repo kidsnote/kidsnote_ios --comments
  ```
- 중복이 없으면 `gh pr review {PR번호} --repo kidsnote/kidsnote_ios --comment --body "..."`로 등록
- **이슈가 없는 PR은 approve까지 진행**: `gh pr review {PR번호} --repo kidsnote/kidsnote_ios --approve --body "수고하셨습니다 👍"`

---

## 현재 브랜치 리뷰 (내 작업)

아래는 PR 번호 없이 `/review`만 실행한 경우의 절차입니다.

## 리뷰 범위 결정 (중요)

### 1단계: Base 브랜치 결정

브랜치 형식에 따라 base 브랜치를 결정합니다:

```
현재 브랜치: feature/{부모브랜치명}/PK-xxxxx
```

| 조건 | Base 브랜치 |
|------|-------------|
| `feature/{부모}/main` 브랜치가 존재 | `feature/{부모}/main` |
| 위 브랜치 없음 | `develop` |

```bash
# 현재 브랜치 확인
git branch --show-current

# 부모 main 브랜치 존재 여부 확인
git branch -a | grep "feature/{부모브랜치명}/main"
```

### 2단계: 커밋 필터링

현재 브랜치의 PK 번호와 일치하는 커밋만 리뷰합니다.

```bash
# 예시: 브랜치가 feature/ad-benefit-260120/PK-32227 인 경우
# PK-32227 커밋만 필터링
git log {base}..HEAD --oneline | grep "\[PK-32227\]"
```

### 3단계: 변경 내역 확인

```bash
# 변경된 파일 목록
git diff {base}...HEAD --name-only -- "*.swift"

# 코드 변경 내역
git diff {base}...HEAD -- "*.swift"
```

### 예시

```
브랜치: feature/ad-benefit-260120/PK-32227
  ↓
feature/ad-benefit-260120/main 존재? → Yes
  ↓
Base: feature/ad-benefit-260120/main
  ↓
커밋 필터: [PK-32227] 포함된 커밋만 리뷰
```

## 실행 절차: 병렬 리뷰

### Phase 1: diff 수집

리뷰 범위 결정(위 섹션) 후, diff를 **프로젝트 루트**에 임시 저장한다:

```bash
git diff {base}...HEAD -- "*.swift" > review-diff.patch
git log {base}..HEAD --oneline > review-commits.txt
```

> `/tmp/`는 Gemini CLI가 접근 불가. 반드시 프로젝트 루트에 저장.
> 리뷰 완료 후 `rm review-diff.patch review-commits.txt`로 정리.

### Phase 2: 병렬 리뷰 실행

두 리뷰어를 **반드시 동시에(하나의 메시지에서)** 호출한다:

**리뷰어 A — Codex/Claude**
```
Agent(
  description: "code review codex claude",
  mode: "plan",   # 읽기 전용
  prompt: """
  iOS 코드 리뷰를 수행하라.
  프로젝트 루트의 AGENTS.md를 반드시 읽고 따른다.
  review-diff.patch 파일을 읽고, 아래 4개 관점으로 리뷰하라:
  1. Security  2. Performance  3. Maintainability  4. Dependency

  심각도: Critical/High/Medium/Low
  출력은 한국어, 관점별로 [{파일}:{라인}] 형식으로 이슈를 나열하라.
  이슈가 없는 관점은 "이슈 없음"으로 표시.
  접근 금지: Pods/, DerivedData/, Tuist/Dependencies/, ExternalLibraries/, Libraries/
  필요하면 실제 소스 파일도 읽어서 컨텍스트를 파악하라.

  [중요] 각 이슈는 초보 개발자도 이해할 수 있도록 상세하게 작성하라:
  - "무엇이 문제인지" (현재 코드가 어떻게 동작하는지)
  - "왜 문제인지" (어떤 상황에서 어떤 부작용이 발생하는지, 구체적 시나리오 포함)
  - "어떻게 고치면 되는지" (수정 방향과 예시 코드 스니펫)
  한 줄 요약이 아니라 2~5줄의 설명을 포함하라.
  """
)
```

**리뷰어 B — Gemini**

모델 fallback 순서: `gemini-3.1-pro-preview` → `gemini-3-pro-preview` → `gemini-2.5-pro`

```bash
# diff 내용을 프롬프트에 직접 포함 (Gemini CLI가 파일을 못 찾는 문제 방지)
DIFF_CONTENT=$(cat review-diff.patch)

# 1차 시도
gemini -p "iOS 코드 리뷰를 수행하라. 아래 diff 내용을 검토하라.

--- diff 시작 ---
$DIFF_CONTENT
--- diff 끝 ---

아래 4개 관점으로 리뷰하라:
1. Security  2. Performance  3. Maintainability  4. Dependency

심각도: Critical/High/Medium/Low
출력은 한국어, 관점별로 [{파일}:{라인}] 형식으로 이슈를 나열하라.
이슈가 없는 관점은 이슈 없음으로 표시.

[중요] 각 이슈는 초보 개발자도 이해할 수 있도록 상세하게 작성하라:
- 무엇이 문제인지 (현재 코드가 어떻게 동작하는지)
- 왜 문제인지 (어떤 상황에서 어떤 부작용이 발생하는지, 구체적 시나리오 포함)
- 어떻게 고치면 되는지 (수정 방향과 예시 코드 스니펫)
한 줄 요약이 아니라 2~5줄의 설명을 포함하라." -m gemini-2.5-pro --approval-mode plan --allowed-mcp-server-names none -o text 2>&1

# --allowed-mcp-server-names none: MCP 서버 초기화 건너뛰기 (리뷰에 불필요, 동시 실행 시 충돌 방지)
# 기본 모델: gemini-2.5-pro (3.1-pro-preview는 용량 부족 빈번)
# 실패 시(Error, 429 등): 사용자에게 보고 후 Codex/Claude 단독 진행
```

### Phase 2.5: Gemini 실패 처리

Gemini CLI 실행 결과에 에러가 포함된 경우 (`Error`, `ModelNotFoundError`, exit code != 0 등):
1. **에러 내용을 사용자에게 즉시 보고**한다 (조용히 넘어가지 않는다)
2. 사용자에게 "Gemini 실패로 Codex/Claude 단독 리뷰로 진행할까요?" 확인
3. 승인 시 Codex/Claude 단독 결과로 Phase 3 진행

stderr를 `2>/dev/null`로 숨기지 않는다. 반드시 `2>&1`로 에러를 캡처하여 확인한다.

### Phase 3: 결과 종합

두 리뷰 결과를 받은 후:
1. **공통 발견**: 두 리뷰어가 모두 지적한 이슈 (신뢰도 높음)
2. **Codex/Claude 단독**: Codex/Claude만 지적한 이슈
3. **Gemini 단독**: Gemini만 지적한 이슈
4. **의견 불일치**: 한쪽은 문제라 하고 다른 쪽은 괜찮다고 한 경우

최종 출력은 아래 "출력 형식"을 따르되, 각 이슈에 `[Codex/Claude+Gemini]`, `[Codex/Claude]`, `[Gemini]` 태그를 붙인다.

---

## 리뷰 관점

### 1. Security (보안)
- 인젝션 취약점 (SQL, Command, XSS 등)
- 인증/인가 우회 가능성
- 민감 정보 노출 (API 키, 토큰, 개인정보)
- 암호화 미적용 또는 취약한 암호화
- 안전하지 않은 데이터 저장
- 하드코딩된 비밀값

### 2. Performance (성능)
- N+1 쿼리 문제
- 메모리 누수 (순환 참조, retain cycle)
- 불필요한 재렌더링
- 비효율적인 알고리즘 (O(n²) 등)
- 무거운 작업의 메인 스레드 실행
- 과도한 네트워크 요청
- 대용량 데이터 처리 이슈

### 3. Maintainability (유지보수성)
- 높은 순환 복잡도 (Cyclomatic Complexity)
- 과도한 결합도 (Coupling)
- 낮은 응집도 (Cohesion)
- 중복 코드
- 매직 넘버/스트링
- 불명확한 네이밍
- 긴 함수/클래스
- SOLID 원칙 위반

### 4. ~~Testing (테스트)~~ — 리뷰 제외
> 테스트 관련 이슈는 리뷰에 포함하지 않는다. (테스트 커버리지, 테스트 부재 등 지적하지 않음)

### 5. Dependency (의존성) - 모듈화 대비
- 순환 의존성 (Circular Dependency)
- 잘못된 레이어 의존 방향 (상위 → 하위만 허용)
  - Presentation → Domain → Data (O)
  - Data → Domain (X)
- 구체 타입 직접 의존 (프로토콜 추상화 부재)
- 모듈 경계 위반 (다른 Feature 모듈 직접 참조)
- 과도한 의존성 (하나의 파일이 너무 많은 import)
- Singleton 남용
- 전역 상태 의존
- 암묵적 의존성 (명시적 주입 없이 내부에서 생성)

## 접근 금지 경로
- `Pods/`, `DerivedData/`, `Tuist/Dependencies/`
- `ExternalLibraries/`, `Libraries/`, `fastlane/`, `BuildScripts/`

## 출력 형식

리뷰 결과는 **한국어**로, **초보 개발자도 이해할 수 있는 상세한 설명**으로 작성합니다.

### 작성 원칙
- 각 이슈는 반드시 **3가지 요소**를 포함: (1) 현재 상태, (2) 문제점/위험, (3) 수정 제안
- "순환 참조 가능성" 같은 한 줄 요약이 아니라, **왜 문제인지 구체적 시나리오**와 함께 설명
- 코드 스니펫(변경 전/후)을 가능한 한 포함하여 수정 방향을 명확히 제시
- 전문 용어 사용 시 괄호로 간단한 설명 추가 (예: "retain cycle(순환 참조, 메모리가 해제되지 않는 문제)")

```markdown
# 코드 리뷰 결과 (병렬 리뷰)

## 검토 범위
- 브랜치: {branch_name}
- Base: {base_branch}
- 커밋 수: {count}개
- 변경 파일: {count}개
- 리뷰어: Codex/Claude, Gemini 3.1 Pro

## PR 변경 요약
> PR이 무엇을 하는 코드인지 2~3문장으로 요약. 비개발자도 이해할 수 있는 수준으로 작성.

---

## 이슈 목록

### 이슈 1: {한 줄 제목}
- **위치**: [{파일}:{라인}]
- **관점**: Security/Performance/Maintainability/Dependency
- **심각도**: Critical/High/Medium/Low
- **발견**: [Codex/Claude+Gemini] / [Codex/Claude] / [Gemini]

**현재 상태 (무엇이 문제인가)**
> 현재 코드가 어떻게 동작하는지 설명. 변경된 코드를 인용하며 구체적으로 작성.
> ```swift
> // 문제가 되는 코드 인용
> ```

**왜 문제인가**
> 어떤 시나리오에서 어떤 부작용이 발생하는지 구체적으로 설명.
> 예: "사용자가 A 화면에서 B를 탭했을 때, C 때문에 D가 발생할 수 있습니다."

**수정 제안**
> 구체적인 수정 방향과 가능하면 코드 예시 제공.
> ```swift
> // 수정 예시
> ```

---

(이슈 반복)

---

## 의견 불일치 (있을 경우)
### [{파일}:{라인}] {이슈 설명}
- **Codex/Claude 의견**: {의견과 근거}
- **Gemini 의견**: {의견과 근거}
- **최종 판단**: {아키텍트의 판단과 이유}

## 요약 테이블
| 관점 | Critical | High | Medium | Low |
|------|----------|------|--------|-----|
| Security | 0 | 0 | 0 | 0 |
| Performance | 0 | 0 | 0 | 0 |
| Maintainability | 0 | 0 | 0 | 0 |
| Dependency | 0 | 0 | 0 | 0 |

## 총평
> 전체적인 코드 품질에 대한 평가와 가장 우선적으로 확인/수정해야 할 사항 요약.
```

## 심각도 기준

- **Critical**: 즉시 수정 필요 (보안 취약점, 데이터 손실 가능)
- **High**: 배포 전 수정 필요
- **Medium**: 수정 권장
- **Low**: 개선 제안

---

## 완료 시 runtime 갱신 [필수]
`.claude/skills/common/completion-rules.md`를 읽고 따른다.
