---
name: review-operator
description: 코드 리뷰 스킬. 현재 작업 diff 리뷰 또는 PR 리뷰를 수행할 때 사용. "review-operator", "리뷰해줘", "코드 리뷰", "현재 diff 리뷰", "PR 리뷰", PR URL(github.com/.../pull/N), PR 번호가 포함된 요청에서 사용.
---

# Review Operator

코드 리뷰를 수행하는 스킬이다. 요청의 대상에 따라 아래 레퍼런스를 읽고 진행한다.

## Mode Selection

- `/review current`: 현재 작업 diff를 FlowCore 문서 기준으로 리뷰한다. GitHub 제출 없음. `ai/review.md`를 생성한다. [references/review-current.md](references/review-current.md)
- `/review pr`: 다른 사람 PR 또는 지정 PR을 리뷰한다. `gh pr diff` 기반으로 `ai/review.md`와 `ai/review-summary.md`를 생성한다. GitHub review 제출은 사용자 승인 후에만 가능하다. [references/review-pr.md](references/review-pr.md)

요청이 모호하면 리뷰 대상이 현재 작업인지 PR인지 먼저 확인한다.

## Automation Boundary

자동화해도 되는 범위:

- discover 문서 참조
- spec draft 문서 참조
- plan draft 문서 참조
- review
- summary
- 결과 파일 생성

사람 승인 없이 하지 않는 작업:

- code implement
- commit
- push
- PR 생성
- GitHub review 제출
- merge

## Common Rules

- 기본 출력 언어는 한국어다.
- 리뷰는 findings first로 작성한다.
- 발견 사항은 재현 가능한 파일/라인 근거와 함께 제시한다.
- FlowCore workflow 문서를 리뷰 기준으로 사용한다.
- 구현을 직접 수정하지 않는다. 단, 사용자가 명시적으로 수정까지 요청한 경우에만 별도 작업으로 전환한다.
- secret, token, credential을 출력하거나 파일에 남기지 않는다.
