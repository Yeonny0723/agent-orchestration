import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_plugin import validate_plugin


class ValidatePluginTests(unittest.TestCase):
    def test_requires_matching_dual_manifests(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".codex-plugin").mkdir()
            (root / ".claude-plugin").mkdir()
            (root / ".codex-plugin/plugin.json").write_text(
                json.dumps({"name": "agent-orchestration", "version": "0.1.0"}),
                encoding="utf-8",
            )
            (root / ".claude-plugin/plugin.json").write_text(
                json.dumps({"name": "different-name", "version": "0.1.0"}),
                encoding="utf-8",
            )

            errors = validate_plugin(root)

            self.assertIn("manifest names must match", errors)

    def test_rejects_unmatched_cross_host_agent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_matching_manifests(root)
            (root / "agents").mkdir()
            (root / "agents/reviewer.md").write_text("---\nname: reviewer\n---\n", encoding="utf-8")

            errors = validate_plugin(root)

            self.assertIn("missing Codex agent adapter: reviewer.toml", errors)

    def test_reports_missing_manifest_fields_without_crashing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for manifest_dir in (".codex-plugin", ".claude-plugin"):
                (root / manifest_dir).mkdir()
                (root / manifest_dir / "plugin.json").write_text("{}", encoding="utf-8")

            errors = validate_plugin(root)

            self.assertIn("missing manifest field name: .codex-plugin/plugin.json", errors)
            self.assertIn("missing manifest field version: .claude-plugin/plugin.json", errors)

    def test_rejects_command_with_unknown_delegate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_matching_manifests(root)
            (root / "commands").mkdir()
            (root / "commands/git/pr.md").parent.mkdir(parents=True)
            (root / "commands/git/pr.md").write_text(
                "# Git PR\n\nDelegate-To: `missing-skill`\n",
                encoding="utf-8",
            )

            errors = validate_plugin(root)

            self.assertIn("unknown command delegate in commands/git/pr.md: missing-skill", errors)

    def test_repository_is_valid(self):
        root = Path(__file__).parents[1]
        self.assertEqual([], validate_plugin(root))

    def test_requires_codex_repo_marketplace_at_standard_path(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_matching_manifests(root)
            (root / "marketplace.json").write_text(
                json.dumps({"name": "local", "plugins": [{"name": "agent-orchestration", "source": {"path": "."}}]}),
                encoding="utf-8",
            )
            (root / ".claude-plugin/marketplace.json").write_text(
                json.dumps({"name": "local", "plugins": [{"name": "agent-orchestration", "source": "."}]}),
                encoding="utf-8",
            )

            errors = validate_plugin(root)

            self.assertIn("missing marketplace manifest: .agents/plugins/marketplace.json", errors)

    def test_rejects_marketplace_that_does_not_point_to_plugin_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_matching_manifests(root)
            (root / "marketplace.json").write_text(
                json.dumps({
                    "name": "local",
                    "plugins": [{"name": "agent-orchestration", "source": {"path": "./plugins/agent-orchestration"}}],
                }),
                encoding="utf-8",
            )
            (root / ".claude-plugin/marketplace.json").write_text(
                json.dumps({"name": "local", "plugins": [{"name": "agent-orchestration", "source": "."}]}),
                encoding="utf-8",
            )

            errors = validate_plugin(root)

            self.assertIn("Codex marketplace source must point to plugin root: marketplace.json", errors)

    @staticmethod
    def _write_matching_manifests(root: Path) -> None:
        for directory in (".codex-plugin", ".claude-plugin"):
            (root / directory).mkdir()
            (root / directory / "plugin.json").write_text(
                json.dumps({"name": "agent-orchestration", "version": "0.1.0"}),
                encoding="utf-8",
            )


if __name__ == "__main__":
    unittest.main()
