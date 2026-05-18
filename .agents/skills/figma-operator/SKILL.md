---
name: figma-operator
description: Unified Figma operator skill. Uses the Framelink Figma Context MCP (`figma-developer` server, https://github.com/GLips/Figma-Context-MCP) for all Figma operations. Triggered when a Figma URL is provided or when the user asks for Figma metadata/spec/asset extraction.
---

# Figma Operator

## Overview

키즈노트 환경에서 **유일하게 사용하는 Figma 스킬**이다.
다른 figma 관련 스킬/MCP는 모두 비활성화되어 있으며, 본 스킬만이 Figma 작업의 진입점이다.

**MCP 백엔드:** `figma-developer` (Framelink Figma Context MCP / glips/figma-context-mcp)
- 토큰: 1Password 항목 `"Figma - Personal Access Token"` → `~/.claude/bin/figma-developer-wrapper.sh`가 자동 로드
- 도구: `mcp__figma-developer__get_figma_data`, `mcp__figma-developer__download_figma_images`

## Execution Paths

### 1) Claude direct path (기본)

Claude 세션에서 `figma-developer` MCP가 연결되어 있으면 도구를 직접 호출한다.

### 2) Codex bridge path

Codex 등 비-Claude 에이전트에서는 다음 브리지 스크립트를 사용한다:

**중요: 상대경로(`scripts/...`) 호출 금지. 아래 절대경로를 고정 사용한다.**

```bash
FIGMA_OPERATOR_SCRIPT="/Users/allen/Dev/Repo/FlowCore/.agents/skills/figma-operator/scripts/run_claude_figma_task.sh"

bash "$FIGMA_OPERATOR_SCRIPT" \
  --url "https://www.figma.com/design/FILE_KEY/NAME?node-id=123-456&m=dev" \
  --task "이 화면 구현에 필요한 컴포넌트/토큰/간격 규칙 요약"
```

내부적으로 `claude -p --permission-mode bypassPermissions`로 Claude를 호출하고, Claude가 본 스킬을 실행한다.

실사용 예시(고정 경로 + 실제 URL):

```bash
FIGMA_OPERATOR_SCRIPT="/Users/allen/Dev/Repo/FlowCore/.agents/skills/figma-operator/scripts/run_claude_figma_task.sh"

bash "$FIGMA_OPERATOR_SCRIPT" \
  --url "https://www.figma.com/design/2OLkZ7WFyuazD9LEoJmXUn/MO-%EC%95%8C%EB%A6%BC%EC%9E%A5?node-id=15396-205417&m=dev" \
  --task "이 노드의 구현에 필요한 컴포넌트 구조, 레이아웃 값, 타이포, 컬러/보더/이펙트 토큰, 간격 규칙을 표로 정리"
```

## Workflow

### Step 1: URL 파싱

Figma URL에서 다음 정보 추출:
- **fileKey**: `/design/` 뒤 segment
- **nodeId**: `node-id=` 쿼리 파라미터 (URL에서는 `-`, MCP 호출 시 `:`로 변환)

예시:
```
URL: https://www.figma.com/design/2OLkZ7WFyuazD9LEoJmXUn/MO-알림장?node-id=15396-205417
→ fileKey: 2OLkZ7WFyuazD9LEoJmXUn
→ nodeId: 15396:205417
```

### Step 2: 메타데이터/디자인 컨텍스트 조회

`mcp__figma-developer__get_figma_data` 호출:

```
fileKey: <추출한 fileKey>
nodeId: <추출한 nodeId>  # 선택 — 특정 노드만 조회 시
depth: <number>          # 선택 — 트리 깊이 제한 (대용량 파일에서 유용)
```

반환 데이터:
- 노드 계층 구조 (id, name, type, children)
- 레이아웃 (layout mode, padding, gap, sizing)
- 스타일 (fill, stroke, effects, typography)
- 컴포넌트 인스턴스 정보

### Step 3: (필요 시) 이미지/에셋 다운로드

`mcp__figma-developer__download_figma_images` 호출:

```
fileKey: <fileKey>
nodes: [
  { nodeId: "<id>", fileName: "<name>.png" },
  ...
]
localPath: <절대 경로 — 저장할 디렉터리>
pngScale: 1|2|3  # 선택
```

### Step 4: 결과 정리

추출한 정보를 다음 형식으로 출력:

```markdown
## 디자인 스펙: {화면/컴포넌트 이름}

### 컴포넌트 목록
| 이름 | Node ID | 크기 | 타입 |

### Design Tokens
#### Colors / Typography / Spacing

### 컴포넌트 상세
#### {Component Name}
- Size, Layout, Style
```

## Constraints

- 실제 MCP 호출 결과 없이 디자인 스펙을 추측/생성하지 않는다.
- MCP 접근 실패 시 정확한 blocker를 반환한다 (네트워크/토큰/노드 존재 여부 등).
- URL/노드 파싱이 애매하면 모호함을 명시하고 사용자에게 재확인 요청한다.
- 다른 figma 관련 도구(`mcp__figma__*`, `mcp__figma-ocaml__*`)는 비활성화 상태이므로 호출하지 않는다.

## Resources

### scripts/
- `/Users/allen/Dev/Repo/FlowCore/.agents/skills/figma-operator/scripts/run_claude_figma_task.sh`: non-Claude → Claude bridge (절대경로 고정)

### 관련 설정
- MCP wrapper: `~/.claude/bin/figma-developer-wrapper.sh`
- 비활성화된 figma 스킬 백업: `~/.claude/.disabled-skills/`
- 비활성화된 figma 커맨드 백업: `~/.claude/.disabled-commands/`
