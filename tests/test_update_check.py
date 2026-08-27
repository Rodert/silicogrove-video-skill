import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import call, patch


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
        self.assertEqual(git.call_args_list, [
            call(Path("/skill"), "fetch", "--quiet", "origin", "main"),
            call(Path("/skill"), "reset", "--hard", "FETCH_HEAD"),
        ])
        self.assertTrue(CHECK_UPDATE.cache_path().is_file())

    def test_local_changes_are_overwritten_by_the_upstream_revision(self):
        with patch.object(CHECK_UPDATE, "head", side_effect=["local", "upstream"]), patch.object(
            CHECK_UPDATE, "git_output", return_value=SimpleNamespace(returncode=0, stdout="")
        ) as git:
            self.assertEqual(CHECK_UPDATE.check(Path("/skill")), "updated")
        self.assertEqual(git.call_count, 2)

    def test_failed_fetch_does_not_attempt_a_reset(self):
        with patch.object(CHECK_UPDATE, "head", return_value="local"), patch.object(
            CHECK_UPDATE, "git_output", return_value=SimpleNamespace(returncode=1, stdout="")
        ) as git:
            self.assertEqual(CHECK_UPDATE.check(Path("/skill")), "failed")
        git.assert_called_once_with(Path("/skill"), "fetch", "--quiet", "origin", "main")

    def test_unwritable_cache_does_not_raise(self):
        marker = CHECK_UPDATE.cache_path()
        with patch.object(Path, "mkdir", side_effect=PermissionError):
            self.assertFalse(CHECK_UPDATE.write_last_checked(marker, CHECK_UPDATE.time.time()))


if __name__ == "__main__":
    unittest.main()
