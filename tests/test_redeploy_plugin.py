import shutil
import subprocess
import unittest
from pathlib import Path


POWERSHELL = shutil.which("pwsh") or shutil.which("powershell.exe")
CASES = (
    "codex_wrapped_without_ref",
    "codex_wrapped_matching_ref",
    "codex_wrapped_stale_ref",
    "claude_single_entry_array",
    "codex_empty_wrapper",
    "claude_empty_array",
    "malformed_wrapper",
    "missing_source",
    "conflicting_sources",
    "malformed_nested_source",
    "legacy_missing_ref",
    "network_failure",
)


@unittest.skipUnless(POWERSHELL, "PowerShell is required for release script tests")
class RedeployPluginTests(unittest.TestCase):
    def test_marketplace_refresh(self):
        harness = Path(__file__).with_name("redeploy_plugin_cases.ps1")
        for case in CASES:
            with self.subTest(case=case):
                result = subprocess.run(
                    [POWERSHELL, "-NoProfile", "-File", str(harness), "-Case", case],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
