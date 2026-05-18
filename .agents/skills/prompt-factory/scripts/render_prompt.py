#!/usr/bin/env python3
"""Render a workflow prompt from template ID and variables."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from template_store import COMMON_BLOCKS, TEMPLATES

PLACEHOLDER_PATTERN = re.compile(r"\{\{([A-Za-z0-9_.-]+)\}\}")
DEFAULT_MODEL = "gpt-5.4"
FIXED_OUTPUT_FILE = "compiled-prompt.txt"


def parse_vars(raw_items: list[str]) -> dict[str, str]:
    values: dict[str, str] = {}
    for item in raw_items:
        if "=" not in item:
            raise ValueError(f"Invalid --var format: {item}. Use key=value.")
        key, value = item.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"Invalid --var key in: {item}")
        values[key] = value
    return values


def collect_missing_placeholders(rendered: str) -> list[str]:
    return sorted({match.group(1) for match in PLACEHOLDER_PATTERN.finditer(rendered)})


def collect_section_headers(text: str) -> list[str]:
    headers: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.endswith(":") and not stripped.startswith("- "):
            headers.append(stripped)
    return headers


def collect_guard_lines(text: str) -> list[str]:
    guards: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        lowered = stripped.lower()
        if lowered.startswith("- do not ") or lowered.startswith("do not "):
            guards.append(stripped)
    return guards


def collect_run_block_lines(text: str) -> list[str]:
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.strip() == "Do not run:":
            start = index + 1
            break
    if start is None:
        return []

    block: list[str] = []
    for line in lines[start:]:
        stripped = line.strip()
        if not stripped:
            break
        if not stripped.startswith("- "):
            break
        block.append(stripped)
    return block


def collect_ai_artifact_paths(text: str) -> list[str]:
    found = re.findall(r"ai/[A-Za-z0-9._/-]+", text)
    return sorted(set(found))


def validate_candidate(base: str, candidate: str) -> list[str]:
    issues: list[str] = []

    if not candidate.strip():
        issues.append("candidate is empty")
        return issues

    min_len = int(len(base) * 0.6)
    max_len = int(len(base) * 1.8)
    candidate_len = len(candidate)
    if candidate_len < min_len or candidate_len > max_len:
        issues.append(f"candidate length out of range ({candidate_len} not in {min_len}..{max_len})")

    unresolved = collect_missing_placeholders(candidate)
    if unresolved:
        issues.append(f"candidate has unresolved placeholders: {', '.join(unresolved)}")

    for header in collect_section_headers(base):
        if header not in candidate:
            issues.append(f"missing required section header: {header}")

    candidate_lower = candidate.lower()
    for guard in collect_guard_lines(base):
        if guard.lower() not in candidate_lower:
            issues.append(f"missing safety guard line: {guard}")

    for run_line in collect_run_block_lines(base):
        if run_line.lower() not in candidate_lower:
            issues.append(f"missing do-not-run entry: {run_line}")

    for path in collect_ai_artifact_paths(base):
        if path not in candidate:
            issues.append(f"missing artifact path mention: {path}")

    return issues


def improve_with_codex(base_prompt: str, model: str) -> str:
    if not shutil_which("codex"):
        raise RuntimeError("codex CLI not found")

    instruction = """You are improving a workflow prompt for execution quality.

Rules:
1. Preserve scope boundaries and authority boundaries exactly.
2. Do not add runtime/build execution instructions.
3. Keep Korean prose for explanations.
4. Keep technical identifiers and file paths in English.
5. Keep all required safety constraints and do-not-run restrictions.
6. Output prompt text only. No markdown fences. No explanations.

Rewrite this prompt for higher clarity and lower ambiguity while preserving meaning:
"""

    with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False) as input_file:
        input_file.write(instruction)
        input_file.write("\n")
        input_file.write(base_prompt)
        input_file_path = input_file.name

    with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False) as output_file:
        output_file_path = output_file.name

    try:
        with open(input_file_path, "r", encoding="utf-8") as source:
            completed = subprocess.run(
                [
                    "codex",
                    "exec",
                    "-m",
                    model,
                    "--sandbox",
                    "read-only",
                    "--ignore-rules",
                    "--color",
                    "never",
                    "-o",
                    output_file_path,
                    "-",
                ],
                stdin=source,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip() or "codex exec failed")
        return Path(output_file_path).read_text(encoding="utf-8").strip() + "\n"
    finally:
        try:
            os.remove(input_file_path)
        except OSError:
            pass
        try:
            os.remove(output_file_path)
        except OSError:
            pass


def shutil_which(binary: str) -> bool:
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        candidate = Path(directory) / binary
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return True
    return False


def render(template_id: str, variables: dict[str, str]) -> str:
    if template_id not in TEMPLATES:
        raise KeyError(f"Unknown template_id: {template_id}")

    template = TEMPLATES[template_id]
    missing_required = [name for name in template["required_vars"] if name not in variables]
    if missing_required:
        missing = ", ".join(missing_required)
        raise ValueError(f"Missing required vars for {template_id}: {missing}")

    materialized = template["body"]
    merged = dict(COMMON_BLOCKS)
    merged.update(variables)
    merged.setdefault("crash_context", "[가능하면 crash log / stack trace / 재현 경로 붙여넣기]")
    merged.setdefault("commit_subject", "메시지를 작성하세요")

    for key, value in merged.items():
        materialized = materialized.replace(f"{{{{{key}}}}}", value)

    unresolved = collect_missing_placeholders(materialized)
    if unresolved:
        unresolved_names = ", ".join(unresolved)
        raise ValueError(f"Unresolved placeholders: {unresolved_names}")

    return materialized.strip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render workflow prompt templates.")
    parser.add_argument("--template-id", required=True, help="Template ID to render")
    parser.add_argument("--var", action="append", default=[], help="Template variable (key=value)")
    parser.add_argument("--show-required", action="store_true", help="Show required vars and exit")
    parser.add_argument(
        "--improve",
        action="store_true",
        help="Run validated auto-improvement. Fallback to base prompt if validation fails.",
    )
    parser.add_argument(
        "--improve-model",
        default=DEFAULT_MODEL,
        help=f"Model for auto-improvement (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--strict-improve",
        action="store_true",
        help="Fail instead of fallback when improvement is invalid.",
    )
    parser.add_argument(
        "--print-improve-report",
        action="store_true",
        help="Print improve/fallback decision and validation details to stderr.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.template_id not in TEMPLATES:
        print(f"Error: unknown template_id: {args.template_id}", file=sys.stderr)
        print("Run scripts/list_templates.py to see available IDs.", file=sys.stderr)
        return 1

    required_vars = TEMPLATES[args.template_id]["required_vars"]
    if args.show_required:
        req = ", ".join(required_vars) if required_vars else "-"
        print(req)
        return 0

    try:
        variables = parse_vars(args.var)
        compiled = render(args.template_id, variables)
    except (ValueError, KeyError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    if args.improve:
        improve_issues: list[str] = []
        improved_prompt = compiled
        improved_accepted = False
        try:
            candidate = improve_with_codex(compiled, args.improve_model)
            improve_issues = validate_candidate(compiled, candidate)
            if not improve_issues:
                improved_prompt = candidate
                improved_accepted = True
        except RuntimeError as error:
            improve_issues = [str(error)]

        if args.print_improve_report:
            if improved_accepted:
                print("improve: accepted", file=sys.stderr)
            else:
                print("improve: rejected -> fallback to base", file=sys.stderr)
                for issue in improve_issues:
                    print(f"- {issue}", file=sys.stderr)

        if not improved_accepted and args.strict_improve:
            print("Error: auto-improvement failed validation in strict mode.", file=sys.stderr)
            for issue in improve_issues:
                print(f"- {issue}", file=sys.stderr)
            return 1

        compiled = improved_prompt

    output_path = Path(FIXED_OUTPUT_FILE)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(compiled, encoding="utf-8")
    print(f"saved: {output_path}")
    print(compiled, end="")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
