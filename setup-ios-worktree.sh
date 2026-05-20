#!/usr/bin/env bash
#
# iOS 워크트리 셋업: Tuist 빌드 캐시 + AI 워크플로우 구조 + Xcode 오픈
#
# Usage:
#   setup-ios-worktree.sh [worktree_path]
#   (인자 생략 시 현재 디렉토리 사용)
#
# 실행 순서 (중요):
#   1. Tuist 패치 + make icp + git restore + git clean
#   2. AI 워크플로우 디렉토리/파일 생성
#   3. FlowCore 스킬 복사
#   4. ECC 룰/커맨드/에이전트 복사
#   5. Xcode 워크스페이스 오픈
#
set -euo pipefail

PATCH="${TUIST_CACHE_PATCH:-$HOME/Downloads/tuist-install-build-cache/tuist-install-build-cache.patch}"
ECC="${ECC_HOME:-$HOME/.ecc}"
WORKTREE="${1:-$PWD}"

log() { printf '\n\033[1;34m▶\033[0m %s\n' "$*"; }
ok()  { printf '\033[1;32m✓\033[0m %s\n' "$*"; }

cd "$WORKTREE"

# ── 1. Tuist 셋업 (수 분 소요) ────────────────────────────
log "[1/5] Tuist 패치 적용 + make icp + 원복 (수 분 소요)"
# git apply "$PATCH"
# make icp
# git restore .
# git clean -fd
ok "Tuist 캐시 빌드 완료"

# ── 2. AI 워크플로우 구조 ─────────────────────────────────
log "[2/5] AI 워크플로우 디렉토리/파일 생성"
mkdir -p .codex .claude/agents .claude/commands .claude/rules .claude/skills .codex/skills .gemini .github/workflows ai
touch AGENTS.md ai/plan.md ai/review.md ai/gemini-review.md ai/compiled-prompt.txt

cp ~/Dev/Repo/FlowCore/codex-AGENTS.md .codex/AGENTS.md
ok "AI 워크플로우 구조 생성 완료"

# ── 3. FlowCore 스킬 복사 ─────────────────────────────────
log "[3/5] FlowCore 스킬 복사"
cp -R ~/Dev/Repo/FlowCore/.agents/skills/. .claude/skills/
cp -R ~/Dev/Repo/FlowCore/.agents/skills/. .codex/skills/
ok "FlowCore 스킬 복사 완료 (.claude/skills, .codex/skills)"

# ── 4. ECC 자산 복사 ──────────────────────────────────────
log "[4/5] ECC 룰/커맨드/에이전트 복사"
cp    "$ECC"/agents/*.md    .claude/agents/
cp    "$ECC"/commands/*.md  .claude/commands/
cp -r "$ECC"/rules/common/. .claude/rules/
cp -r "$ECC"/rules/swift/.  .claude/rules/
ok "ECC 자산 복사 완료"

# ── 5. Xcode 오픈 ─────────────────────────────────────────
log "[5/5] Xcode 워크스페이스 오픈"
# open KidsNote.xcworkspace
ok "KidsNote.xcworkspace 오픈됨"
