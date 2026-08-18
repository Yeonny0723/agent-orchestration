from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Snapshot:
    target_path: Path
    snapshot_path: Path
    sha256: str


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def snapshot(path: Path) -> Snapshot:
    target = path.resolve(strict=True)
    if not target.is_file():
        raise ValueError(f"mutation target is not a file: {target}")

    original = target.read_bytes()
    snapshot_dir = Path(tempfile.mkdtemp(prefix="agent-orchestration-mutation-"))
    snapshot_path = snapshot_dir / "original.bin"
    snapshot_path.write_bytes(original)
    return Snapshot(target, snapshot_path, _sha256(original))


def restore(saved: Snapshot) -> str:
    if not saved.snapshot_path.is_file():
        raise FileNotFoundError(f"snapshot does not exist: {saved.snapshot_path}")

    original = saved.snapshot_path.read_bytes()
    if _sha256(original) != saved.sha256:
        raise ValueError("snapshot hash mismatch")

    saved.target_path.write_bytes(original)
    restored_hash = _sha256(saved.target_path.read_bytes())
    if restored_hash != saved.sha256:
        raise ValueError("restored file hash mismatch")

    shutil.rmtree(saved.snapshot_path.parent)
    return restored_hash


def _write_state(saved: Snapshot, state_path: Path) -> None:
    state_path.write_text(
        json.dumps(
            {
                "target_path": str(saved.target_path),
                "snapshot_path": str(saved.snapshot_path),
                "sha256": saved.sha256,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def _read_state(state_path: Path) -> Snapshot:
    data = json.loads(state_path.read_text(encoding="utf-8"))
    return Snapshot(
        target_path=Path(data["target_path"]),
        snapshot_path=Path(data["snapshot_path"]),
        sha256=data["sha256"],
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Snapshot and restore one mutation target exactly.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    snapshot_parser = subparsers.add_parser("snapshot")
    snapshot_parser.add_argument("target", type=Path)
    snapshot_parser.add_argument("state", type=Path)
    restore_parser = subparsers.add_parser("restore")
    restore_parser.add_argument("state", type=Path)
    args = parser.parse_args()

    if args.command == "snapshot":
        saved = snapshot(args.target)
        _write_state(saved, args.state)
        print(saved.sha256)
        return 0

    saved = _read_state(args.state)
    print(restore(saved))
    args.state.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
