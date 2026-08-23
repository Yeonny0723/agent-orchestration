import tempfile
import unittest
from pathlib import Path

from scripts.mutation_guard import restore, snapshot


class MutationGuardTests(unittest.TestCase):
    def test_restores_exact_dirty_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "module.py"
            original = b"dirty = True\r\nvalue = 7\r\n"
            path.write_bytes(original)

            saved = snapshot(path)
            path.write_bytes(b"dirty = False\n")
            restored_hash = restore(saved)

            self.assertEqual(original, path.read_bytes())
            self.assertEqual(saved.sha256, restored_hash)

    def test_restore_rejects_a_tampered_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "module.py"
            path.write_bytes(b"original")
            saved = snapshot(path)
            saved.snapshot_path.write_bytes(b"tampered")

            with self.assertRaisesRegex(ValueError, "snapshot hash mismatch"):
                restore(saved)


if __name__ == "__main__":
    unittest.main()
