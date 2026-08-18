from __future__ import annotations

import argparse
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class InstallResult:
    installed: list[str]
    conflicts: list[str]


def install_agents(source: Path, project: Path) -> InstallResult:
    source = source.resolve(strict=True)
    project = project.resolve(strict=True)
    if not source.is_dir():
        raise NotADirectoryError(source)

    destination = project / ".codex" / "agents"
    if destination.exists() and not destination.is_dir():
        raise NotADirectoryError(destination)
    destination.mkdir(parents=True, exist_ok=True)

    installed: list[str] = []
    conflicts: list[str] = []
    for agent in sorted(source.glob("*.toml")):
        target = destination / agent.name
        if target.exists():
            conflicts.append(agent.name)
            continue
        shutil.copy2(agent, target)
        installed.append(agent.name)
    return InstallResult(installed, conflicts)


def main() -> int:
    parser = argparse.ArgumentParser(description="Install Codex agent adapters without overwriting files.")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument(
        "--source",
        type=Path,
        default=Path(__file__).parents[1] / "adapters" / "codex" / "agents",
    )
    args = parser.parse_args()
    result = install_agents(args.source, args.project)
    for name in result.installed:
        print(f"installed: {name}")
    for name in result.conflicts:
        print(f"conflict: {name}")
    return 2 if result.conflicts else 0


if __name__ == "__main__":
    raise SystemExit(main())
