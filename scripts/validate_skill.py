#!/usr/bin/env python3
"""Validate the repository structure and metadata for a Codex skill."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REQUIRED_INTERFACE_KEYS = {
    "display_name",
    "short_description",
    "default_prompt",
}


def load_frontmatter(path: Path) -> dict[str, str]:
    content = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---(?:\n|$)", content, re.DOTALL)
    if not match:
        raise ValueError(f"{path}: missing or malformed YAML frontmatter")

    frontmatter: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.startswith((" ", "\t")):
            continue
        key, separator, value = line.partition(":")
        if not separator:
            raise ValueError(f"{path}: invalid frontmatter line: {line}")
        frontmatter[key.strip()] = value.strip().strip("\"'")
    return frontmatter


def load_interface(path: Path) -> dict[str, str]:
    content = path.read_text(encoding="utf-8")
    if not re.search(r"(?m)^interface:\s*$", content):
        raise ValueError(f"{path}: missing interface mapping")

    interface: dict[str, str] = {}
    for line in content.splitlines():
        match = re.match(r"^\s{2}([a-z_]+):\s*(.*?)\s*$", line)
        if match:
            interface[match.group(1)] = match.group(2).strip("\"'")
    return interface


def validate_skill(root: Path) -> list[str]:
    errors: list[str] = []
    skill_md = root / "SKILL.md"
    agent_yaml = root / "agents" / "openai.yaml"

    for required_path in (skill_md, agent_yaml):
        if not required_path.is_file():
            errors.append(f"Missing required file: {required_path.relative_to(root)}")

    for required_dir in ("scripts", "references"):
        if not (root / required_dir).is_dir():
            errors.append(f"Missing required directory: {required_dir}/")

    if errors:
        return errors

    try:
        frontmatter = load_frontmatter(skill_md)
    except ValueError as exc:
        errors.append(str(exc))
        return errors

    name = frontmatter.get("name")
    description = frontmatter.get("description")

    if not isinstance(name, str) or not NAME_PATTERN.fullmatch(name):
        errors.append("SKILL.md: name must use lowercase hyphen-case")
    elif name != root.name:
        errors.append(f"SKILL.md: name '{name}' must match directory name '{root.name}'")

    if not isinstance(description, str) or not description.strip():
        errors.append("SKILL.md: description must be a non-empty string")
    elif len(description) > 1024:
        errors.append("SKILL.md: description must not exceed 1024 characters")

    try:
        interface = load_interface(agent_yaml)
    except ValueError as exc:
        errors.append(str(exc))
        return errors

    missing_keys = REQUIRED_INTERFACE_KEYS - set(interface)
    if missing_keys:
        errors.append(
            "agents/openai.yaml: missing interface keys: "
            + ", ".join(sorted(missing_keys))
        )

    default_prompt = interface.get("default_prompt")
    if isinstance(name, str) and isinstance(default_prompt, str):
        if f"${name}" not in default_prompt:
            errors.append(
                f"agents/openai.yaml: default_prompt must mention '${name}'"
            )

    python_scripts = sorted((root / "scripts").glob("*.py"))
    if not python_scripts:
        errors.append("scripts/: expected at least one Python script")

    reference_files = sorted((root / "references").glob("*.md"))
    if not reference_files:
        errors.append("references/: expected at least one Markdown reference")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_directory", type=Path)
    args = parser.parse_args()

    root = args.skill_directory.resolve()
    errors = validate_skill(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(f"Skill structure is valid: {root.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
