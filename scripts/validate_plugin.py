from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path


MANIFESTS = (Path(".codex-plugin/plugin.json"), Path(".claude-plugin/plugin.json"))
MARKETPLACES = (Path("marketplace.json"), Path(".claude-plugin/marketplace.json"))
SCAN_ROOTS = (".codex-plugin", ".claude-plugin", "commands", "skills", "agents", "adapters", "conventions", "templates")
PLACEHOLDER_PATTERNS = ("[TODO:", "[TODO]", "TODO: Complete", "TODO: Replace")


def _load_manifest(root: Path, relative: Path, errors: list[str]) -> dict | None:
    path = root / relative
    if not path.is_file():
        errors.append(f"missing manifest: {relative.as_posix()}")
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        errors.append(f"invalid JSON in {relative.as_posix()}: {error.msg}")
        return None
    for field in ("name", "version"):
        if not data.get(field):
            errors.append(f"missing manifest field {field}: {relative.as_posix()}")
    return data


def _validate_skills(root: Path, errors: list[str]) -> None:
    skills = root / "skills"
    if not skills.is_dir():
        return
    for directory in sorted(path for path in skills.iterdir() if path.is_dir()):
        skill_path = directory / "SKILL.md"
        if not skill_path.is_file():
            errors.append(f"missing SKILL.md: skills/{directory.name}")
            continue
        text = skill_path.read_text(encoding="utf-8")
        name = re.search(r"(?m)^name:\s*([^\s]+)\s*$", text)
        description = re.search(r"(?m)^description:\s*(.+?)\s*$", text)
        if not name or name.group(1) != directory.name:
            errors.append(f"skill name must match directory: {directory.name}")
        if not description:
            errors.append(f"missing skill description: {directory.name}")

        metadata_path = directory / "agents" / "openai.yaml"
        if not metadata_path.is_file():
            errors.append(f"missing skill UI metadata: {directory.name}")
            continue
        metadata = metadata_path.read_text(encoding="utf-8")
        for field in ("display_name", "short_description", "default_prompt"):
            if not re.search(rf"(?m)^\s*{field}:\s*.+$", metadata):
                errors.append(f"missing {field} in skill UI metadata: {directory.name}")


def _validate_agents(root: Path, errors: list[str]) -> None:
    claude_root = root / "agents"
    codex_root = root / "adapters" / "codex" / "agents"
    claude_names = {path.stem for path in claude_root.glob("*.md")} if claude_root.is_dir() else set()
    codex_names = {path.stem for path in codex_root.glob("*.toml")} if codex_root.is_dir() else set()
    for name in sorted(claude_names - codex_names):
        errors.append(f"missing Codex agent adapter: {name}.toml")
    for name in sorted(codex_names - claude_names):
        errors.append(f"missing Claude agent adapter: {name}.md")
    for path in codex_root.glob("*.toml") if codex_root.is_dir() else ():
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as error:
            errors.append(f"invalid TOML in {path.relative_to(root).as_posix()}: {error}")
            continue
        for field in ("name", "description", "developer_instructions"):
            if not data.get(field):
                errors.append(f"missing {field} in Codex agent: {path.name}")


def _validate_commands(root: Path, errors: list[str]) -> None:
    commands = root / "commands"
    if not commands.is_dir():
        return
    skills = {path.name for path in (root / "skills").iterdir() if path.is_dir()} if (root / "skills").is_dir() else set()
    for path in sorted(commands.glob("*.md")):
        matches = re.findall(r"(?m)^Delegate-To: `([^`]+)`$", path.read_text(encoding="utf-8"))
        relative = path.relative_to(root).as_posix()
        if len(matches) != 1:
            errors.append(f"command must delegate exactly once: {relative}")
        elif matches[0] not in skills:
            errors.append(f"unknown command delegate in {relative}: {matches[0]}")


def _validate_marketplaces(root: Path, errors: list[str]) -> None:
    for relative in MARKETPLACES:
        path = root / relative
        if not path.is_file():
            errors.append(f"missing marketplace manifest: {relative.as_posix()}")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            errors.append(f"invalid JSON in {relative.as_posix()}: {error.msg}")
            continue

        if not data.get("name"):
            errors.append(f"missing marketplace field name: {relative.as_posix()}")
        plugins = data.get("plugins")
        if not isinstance(plugins, list):
            errors.append(f"missing marketplace plugins: {relative.as_posix()}")
            continue

        plugin = next((item for item in plugins if isinstance(item, dict) and item.get("name") == "agent-orchestration"), None)
        if plugin is None:
            errors.append(f"missing agent-orchestration marketplace entry: {relative.as_posix()}")
            continue

        source = plugin.get("source")
        if relative == Path("marketplace.json"):
            if not isinstance(source, dict) or source.get("path") != ".":
                errors.append(f"Codex marketplace source must point to plugin root: {relative.as_posix()}")
        elif source != ".":
            errors.append(f"Claude marketplace source must point to plugin root: {relative.as_posix()}")


def _validate_placeholders(root: Path, errors: list[str]) -> None:
    for root_name in SCAN_ROOTS:
        scan_root = root / root_name
        if not scan_root.exists():
            continue
        paths = [scan_root] if scan_root.is_file() else scan_root.rglob("*")
        for path in paths:
            if not path.is_file() or path.suffix.lower() not in {".md", ".json", ".toml", ".yaml", ".yml"}:
                continue
            text = path.read_text(encoding="utf-8")
            if any(pattern in text for pattern in PLACEHOLDER_PATTERNS):
                errors.append(f"placeholder found: {path.relative_to(root).as_posix()}")


def validate_plugin(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    manifests = [_load_manifest(root, relative, errors) for relative in MANIFESTS]
    if all(manifest is not None for manifest in manifests):
        codex, claude = manifests
        if codex.get("name") != claude.get("name"):
            errors.append("manifest names must match")
        if codex.get("version") != claude.get("version"):
            errors.append("manifest versions must match")
    _validate_skills(root, errors)
    _validate_agents(root, errors)
    _validate_commands(root, errors)
    _validate_marketplaces(root, errors)
    _validate_placeholders(root, errors)
    return errors


if __name__ == "__main__":
    failures = validate_plugin(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
    for failure in failures:
        print(failure)
    raise SystemExit(1 if failures else 0)
