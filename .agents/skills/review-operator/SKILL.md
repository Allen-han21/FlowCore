---
name: review-operator
description: 코드 리뷰 스킬. 현재 작업 diff 리뷰 또는 PR 리뷰를 수행할 때 사용. "review-operator", "리뷰해줘", "코드 리뷰", "현재 diff 리뷰", "PR 리뷰", PR URL(github.com/.../pull/N), PR 번호가 포함된 요청에서 사용.
---

# Review Operator

코드 리뷰를 수행하는 스킬이다. 요청의 대상에 따라 아래 레퍼런스를 읽고 진행한다.

## Mode Selection

- 현재 작업 또는 현재 브랜치 diff 리뷰: [references/review-current.md](references/review-current.md)
- 다른 사람 PR, PR 번호, PR URL 리뷰: [references/review-pr.md](references/review-pr.md)

요청이 모호하면 리뷰 대상이 현재 작업인지 PR인지 먼저 확인한다.

## Common Rules

- 기본 출력 언어는 한국어다.
- 리뷰는 findings first로 작성한다.
- 발견 사항은 재현 가능한 파일/라인 근거와 함께 제시한다.
- 구현을 직접 수정하지 않는다. 단, 사용자가 명시적으로 수정까지 요청한 경우에만 별도 작업으로 전환한다.
- secret, token, credential을 출력하거나 파일에 남기지 않는다.
