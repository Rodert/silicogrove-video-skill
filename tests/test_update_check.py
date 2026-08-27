import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


SCRIPT = Path(__file__).parents[1] / "scripts" / "check_update.py"
SPEC = importlib.util.spec_from_file_location("check_update", SCRIPT)
CHECK_UPDATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK_UPDATE)


class UpdateCheckTests(unittest.TestCase):
    def setUp(self):
        self.cache = tempfile.TemporaryDirectory()
        self.original_cache = os.environ.get("XDG_CACHE_HOME")
        os.environ["XDG_CACHE_HOME"] = self.cache.name

    def tearDown(self):
        if self.original_cache is None:
            os.environ.pop("XDG_CACHE_HOME", None)
        else:
            os.environ["XDG_CACHE_HOME"] = self.original_cache
        self.cache.cleanup()

    def test_fresh_marker_skips_git(self):
        marker = CHECK_UPDATE.cache_path()
        CHECK_UPDATE.write_last_checked(marker, CHECK_UPDATE.time.time())
        with patch.object(CHECK_UPDATE, "git_output") as git:
            self.assertEqual(CHECK_UPDATE.check(Path("/skill")), "skipped")
        git.assert_not_called()

    def test_updated_result_records_daily_marker(self):
        with patch.object(CHECK_UPDATE, "head", side_effect=["old", "new"]), patch.object(
            CHECK_UPDATE, "git_output", return_value=SimpleNamespace(returncode=0, stdout="")
        ) as git:
            self.assertEqual(CHECK_UPDATE.check(Path("/skill")), "updated")
        git.assert_called_once_with(Path("/skill"), "pull", "--ff-only", "origin", "main")
        self.assertTrue(CHECK_UPDATE.cache_path().is_file())

    def test_local_changes_report_blocked(self):
        pull_failed = SimpleNamespace(returncode=1, stdout="")
        local_changes = SimpleNamespace(returncode=0, stdout=" M SKILL.md\n")
        with patch.object(CHECK_UPDATE, "head", return_value="same"), patch.object(
            CHECK_UPDATE, "git_output", side_effect=[pull_failed, local_changes]
        ):
            self.assertEqual(CHECK_UPDATE.check(Path("/skill")), "blocked")

    def test_unwritable_cache_does_not_raise(self):
        marker = CHECK_UPDATE.cache_path()
        with patch.object(Path, "mkdir", side_effect=PermissionError):
            self.assertFalse(CHECK_UPDATE.write_last_checked(marker, CHECK_UPDATE.time.time()))


if __name__ == "__main__":
    unittest.main()
