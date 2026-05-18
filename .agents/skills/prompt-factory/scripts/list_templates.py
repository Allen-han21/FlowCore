#!/usr/bin/env python3
"""List available template IDs."""

from template_store import TEMPLATES


def main() -> int:
    print("Available template IDs:")
    for template_id in sorted(TEMPLATES.keys()):
        data = TEMPLATES[template_id]
        required = ", ".join(data["required_vars"]) if data["required_vars"] else "-"
        print(f"- {template_id}  [stage={data['stage']}]  required_vars={required}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

