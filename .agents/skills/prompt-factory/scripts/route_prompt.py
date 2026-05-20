#!/usr/bin/env python3
"""Route natural-language requests to a prompt-factory template."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


DISCOVER_KEYWORDS = [
    "안정성 향상",
    "성능 개선",
    "캐시",
    "오프라인",
    "네트워크 불안정",
    "구조 개선",
    "아키텍처 검토",
    "기존 프로젝트 분석",
    "영향 범위 확인",
    "어디를 봐야",
    "조사",
    "파악",
]

BROAD_SYSTEM_CONCERNS = [
    "캐시",
    "성능",
    "안정성",
    "오프라인",
    "보안",
    "인증",
    "네트워크",
    "api",
    "서버",
]

MULTI_LAYER_KEYWORDS = [
    "네트워크",
    "urlcache",
    "캐시",
    "offline",
    "오프라인",
    "stale",
    "보안",
    "인증",
    "api",
    "서버",
    "성능",
]

EXTERNAL_CONTEXT_KEYWORDS = [
    "slack",
    "jira",
    "figma",
    "스크린샷",
    "위키",
    "wiki",
    "prd",
]

NORMALIZE_KEYWORDS = [
    "slack",
    "jira",
    "figma",
    "스크린샷",
    "위키",
    "wiki",
    "prd",
    "캡처",
    "이미지",
    "첨부",
    "대화",
    "스레드",
    "thread",
    "음성",
    "받아쓰기",
]

ABSTRACT_GOAL_KEYWORDS = [
    "안정성 향상",
    "성능 개선",
    "구조 개선",
    "캐시 개선",
    "개선",
    "향상",
]

REVIEW_KEYWORDS = ["리뷰", "검토", "review", "코드리뷰", "code review", "pr 리뷰", "pr review"]
TICKET_KEYWORDS = ["티켓", "ticket", "jira 생성", "jira 발행", "이슈 생성", "issue draft", "ticket draft"]
IMPLEMENT_KEYWORDS = ["구현", "수정", "개발", "고쳐", "fix", "implement"]
SPEC_KEYWORDS = ["스펙", "spec", "명세", "요구사항"]
PLAN_KEYWORDS = ["계획", "설계", "plan"]


@dataclass
class RoutingDecision:
    intent: str
    template_id: str
    reasons: list[str]
    matched_discover_rules: list[int]


def normalize(text: str) -> str:
    lowered = text.lower()
    lowered = re.sub(r"\s+", " ", lowered).strip()
    return lowered


def contains_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def count_matches(text: str, keywords: list[str]) -> int:
    return sum(1 for keyword in keywords if keyword in text)


def is_short_request(task: str) -> bool:
    lines = [line for line in task.splitlines() if line.strip()]
    return len(lines) <= 3 and len(task.strip()) <= 240


def has_target_file(text: str) -> bool:
    file_pattern = re.compile(r"[A-Za-z0-9_./-]+\.(swift|m|mm|h|kt|java|ts|tsx|js|jsx|py|rb|go|cs|cpp)")
    return bool(file_pattern.search(text))


def has_target_screen(text: str) -> bool:
    screen_keywords = ["화면", "screen", "viewcontroller", "vc", "페이지", "팝업", "시트", "탭", "scene"]
    return contains_any(text, screen_keywords)


def has_exact_api(text: str) -> bool:
    api_patterns = [
        r"\b(get|post|put|patch|delete)\b",
        r"/api/",
        r"https?://",
        r"\bendpoint\b",
    ]
    return any(re.search(pattern, text) for pattern in api_patterns)


def has_exact_class(task: str) -> bool:
    suffix_pattern = re.compile(
        r"\b[A-Z][A-Za-z0-9_]*(ViewController|VC|Manager|Service|Repository|UseCase|Interactor|ViewModel|Controller)\b"
    )
    if suffix_pattern.search(task):
        return True
    class_decl_pattern = re.compile(r"\b(class|struct|enum|protocol)\s+[A-Z][A-Za-z0-9_]+\b", re.IGNORECASE)
    return bool(class_decl_pattern.search(task))


def looks_like_mixed_context(task: str, text: str) -> bool:
    if contains_any(text, NORMALIZE_KEYWORDS):
        return True
    non_empty_lines = [line.strip() for line in task.splitlines() if line.strip()]
    if len(non_empty_lines) >= 4 and not has_target_file(text):
        return True
    speech_markers = ["그러니까", "뭔가", "아마", "같은데", "라고 함", "라고 하네요", "요청 왔"]
    return contains_any(text, speech_markers)


def choose_discover_template(text: str) -> str:
    if "symbol" in text or "심볼" in text or "lsp" in text or "call hierarchy" in text:
        return "discover.symbols"
    if contains_any(text, ["cache", "캐시", "urlcache", "네트워크", "offline", "오프라인", "stale"]):
        return "discover.ios-cache"
    return "discover.general"


def route(task: str) -> RoutingDecision:
    text = normalize(task)
    reasons: list[str] = []
    matched_rules: list[int] = []

    explicit_ticket_request = contains_any(text, TICKET_KEYWORDS) and contains_any(
        text, ["생성", "작성", "발행", "draft", "초안"]
    )
    if explicit_ticket_request:
        return RoutingDecision("TICKET", "ticket.from-plan", ["명시적 티켓 초안/생성 요청"], [])

    explicit_review_request = contains_any(text, REVIEW_KEYWORDS)
    if explicit_review_request and not looks_like_mixed_context(task, text):
        return RoutingDecision("REVIEW", "review.feature", ["명시적 리뷰/검토 요청"], [])

    if looks_like_mixed_context(task, text):
        return RoutingDecision(
            "NORMALIZE",
            "normalize.context",
            ["Slack/Jira/screenshot/voice-like 또는 mixed context 요청으로 판단되어 context normalize 선행"],
            [],
        )

    concrete_anchor = any(
        [
            has_target_file(text),
            has_target_screen(text),
            has_exact_api(text),
            has_exact_class(task),
        ]
    )

    # DISCOVER rule set (any-match)
    if contains_any(text, ["대형 프로젝트", "기존 프로젝트", "전체", "전역", "영향 범위"]):
        matched_rules.append(1)
        reasons.append("기존 프로젝트 영향 범위가 넓을 가능성")
    short_request = is_short_request(task)
    broad_concern = contains_any(text, BROAD_SYSTEM_CONCERNS)
    if short_request and (not concrete_anchor or broad_concern):
        matched_rules.append(2)
        reasons.append("요청이 짧고 context anchor가 부족하거나 broad concern이 포함됨")
    if not concrete_anchor:
        matched_rules.append(3)
        reasons.append("관련 파일/화면/API/class anchor가 부족함")
    if contains_any(text, BROAD_SYSTEM_CONCERNS):
        matched_rules.append(4)
        reasons.append("서버/API/캐시/인증/보안/오프라인/성능 관련 키워드 포함")
    if contains_any(text, ["아키텍처", "구조 파악", "기존 구조", "분석"]):
        matched_rules.append(5)
        reasons.append("기존 아키텍처 선파악 필요 신호")
    if contains_any(text, ABSTRACT_GOAL_KEYWORDS):
        matched_rules.append(6)
        reasons.append("요청 목표가 추상적 개선 표현 중심")
    if count_matches(text, MULTI_LAYER_KEYWORDS) >= 2:
        matched_rules.append(7)
        reasons.append("여러 레이어 동시 영향 가능성")
    if contains_any(text, EXTERNAL_CONTEXT_KEYWORDS):
        matched_rules.append(8)
        reasons.append("Slack/Jira/Figma/스크린샷 등 외부 맥락 필요 신호")
    if contains_any(text, ["변경 범위", "리스크", "안정성", "회귀", "영향 범위"]):
        matched_rules.append(9)
        reasons.append("잘못 설계 시 blast radius 확대 위험")
    if contains_any(text, ["개선", "향상"]) and not concrete_anchor:
        matched_rules.append(10)
        reasons.append("수정 지점 없이 개선 목표만 제시됨")

    # Extra disambiguation rules requested by team:
    broad_concern_short = short_request and broad_concern
    missing_anchors = not all([has_target_file(text), has_target_screen(text), has_exact_api(text), has_exact_class(task)])
    if broad_concern_short and 2 not in matched_rules:
        matched_rules.append(2)
        reasons.append("짧은 요청 + 광범위 시스템 concern 조합")
    if contains_any(text, BROAD_SYSTEM_CONCERNS) and missing_anchors and 3 not in matched_rules:
        matched_rules.append(3)
        reasons.append("핵심 concern 대비 대상 anchor 부족")

    if matched_rules:
        template = choose_discover_template(text)
        return RoutingDecision(
            intent="DISCOVER",
            template_id=template,
            reasons=reasons,
            matched_discover_rules=sorted(set(matched_rules)),
        )

    # Priority order when normalize/discover gates are not matched:
    # NORMALIZE > DISCOVER > REVIEW > TICKET > IMPLEMENT > SPEC > PLAN
    if contains_any(text, REVIEW_KEYWORDS):
        return RoutingDecision("REVIEW", "review.feature", ["리뷰/검토 의도 감지"], [])
    if contains_any(text, TICKET_KEYWORDS):
        return RoutingDecision("TICKET", "ticket.from-plan", ["티켓/협업 실행 artifact 의도 감지"], [])
    if contains_any(text, IMPLEMENT_KEYWORDS):
        return RoutingDecision("IMPLEMENT", "implement.feature", ["구현/수정 의도 감지"], [])
    if contains_any(text, SPEC_KEYWORDS):
        return RoutingDecision("SPEC", "spec.from-discovery", ["스펙/명세 의도 감지"], [])
    if contains_any(text, PLAN_KEYWORDS):
        return RoutingDecision("PLAN", "plan.feature", ["계획/설계 의도 감지 + context sufficient"], [])

    return RoutingDecision(
        intent="PLAN",
        template_id="plan.feature",
        reasons=["명시 intent 부족: 기본값 PLAN 적용"],
        matched_discover_rules=[],
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Route natural language to prompt-factory template.")
    parser.add_argument("task", help="Natural-language request")
    parser.add_argument("--dry-run", action="store_true", help="Only print routing decision")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    decision = route(args.task)

    print(f"intent: {decision.intent}", flush=True)
    print(f"template_id: {decision.template_id}", flush=True)
    if decision.matched_discover_rules:
        numbers = ", ".join(str(number) for number in decision.matched_discover_rules)
        print(f"discover_rules_matched: {numbers}", flush=True)
    print("reason:", flush=True)
    for reason in decision.reasons:
        print(f"- {reason}", flush=True)

    if args.dry_run:
        return 0

    script_dir = Path(__file__).resolve().parent
    command = [sys.executable, str(script_dir / "render_prompt.py"), "--template-id", decision.template_id]

    # Templates that require task var.
    if decision.template_id.startswith(("normalize.", "discover.", "plan.", "spec.", "ticket.", "implement.")):
        command.extend(["--var", f"task={args.task}"])

    completed = subprocess.run(command, text=True, check=False, cwd=script_dir.parent.parent.parent.parent)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
