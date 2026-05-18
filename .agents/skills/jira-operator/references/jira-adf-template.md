# Jira ADF Template

Jira Cloud description 필드는 ADF(Atlassian Document Format) JSON을 기대한다.

이 reference는 description 본문을 만들 때 복사해서 쓰는 최소 템플릿이다.

사용 규칙:

1. `version`은 `1`을 유지한다.
2. 최상위 `type`은 `doc`으로 유지한다.
3. heading, paragraph, bulletList 정도만 우선 사용한다.
4. 이 markdown 파일을 `--adf-file`에 넘기면 첫 번째 fenced `json` block만 읽힌다.

```json
{
  "version": 1,
  "type": "doc",
  "content": [
    {
      "type": "heading",
      "attrs": {
        "level": 2
      },
      "content": [
        {
          "type": "text",
          "text": "요약"
        }
      ]
    },
    {
      "type": "paragraph",
      "content": [
        {
          "type": "text",
          "text": "문제와 기대 결과를 한 문단으로 정리한다."
        }
      ]
    },
    {
      "type": "heading",
      "attrs": {
        "level": 2
      },
      "content": [
        {
          "type": "text",
          "text": "작업 항목"
        }
      ]
    },
    {
      "type": "bulletList",
      "content": [
        {
          "type": "listItem",
          "content": [
            {
              "type": "paragraph",
              "content": [
                {
                  "type": "text",
                  "text": "현재 현상을 재현하고 범위를 확인한다."
                }
              ]
            }
          ]
        },
        {
          "type": "listItem",
          "content": [
            {
              "type": "paragraph",
              "content": [
                {
                  "type": "text",
                  "text": "수정 방향과 검증 방법을 명시한다."
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

plain text만 있으면 `jira_update_issue_description.py --text` 또는 `--text-file`을 사용해 자동으로 paragraph ADF로 감싼다.
