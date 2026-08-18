import tempfile
import unittest
from pathlib import Path

from scripts.install_codex_agents import install_agents


class InstallCodexAgentsTests(unittest.TestCase):
    def test_installs_new_agents_and_preserves_conflicts(self):
        with tempfile.TemporaryDirectory() as source_dir, tempfile.TemporaryDirectory() as target_dir:
            source = Path(source_dir)
            project = Path(target_dir)
            (source / "new-agent.toml").write_text('name = "new-agent"\n', encoding="utf-8")
            (source / "reviewer.toml").write_text('name = "reviewer"\n', encoding="utf-8")
            destination = project / ".codex/agents"
            destination.mkdir(parents=True)
            (destination / "reviewer.toml").write_text("user-owned", encoding="utf-8")

            result = install_agents(source, project)

            self.assertEqual(["new-agent.toml"], result.installed)
            self.assertEqual(["reviewer.toml"], result.conflicts)
            self.assertEqual("user-owned", (destination / "reviewer.toml").read_text(encoding="utf-8"))

    def test_rejects_non_directory_agent_target(self):
        with tempfile.TemporaryDirectory() as source_dir, tempfile.TemporaryDirectory() as target_dir:
            source = Path(source_dir)
            project = Path(target_dir)
            (source / "reviewer.toml").write_text('name = "reviewer"\n', encoding="utf-8")
            (project / ".codex").mkdir()
            (project / ".codex/agents").write_text("not-a-directory", encoding="utf-8")

            with self.assertRaisesRegex(NotADirectoryError, "agents"):
                install_agents(source, project)


if __name__ == "__main__":
    unittest.main()
