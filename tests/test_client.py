import contextlib
import importlib.util
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import urllib.error


CLIENT = Path(__file__).parents[1] / "scripts" / "silicogrove_video.py"
SPEC = importlib.util.spec_from_file_location("silicogrove_video", CLIENT)
CLIENT_MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CLIENT_MODULE)


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.config = tempfile.TemporaryDirectory()
        self.original_config = os.environ.get("XDG_CONFIG_HOME")
        os.environ["XDG_CONFIG_HOME"] = self.config.name
        CLIENT_MODULE.save_key("sk-test-value")
        CLIENT_MODULE.ACTIVE_TASK_LOG = None

    def tearDown(self):
        if self.original_config is None:
            os.environ.pop("XDG_CONFIG_HOME", None)
        else:
            os.environ["XDG_CONFIG_HOME"] = self.original_config
        CLIENT_MODULE.ACTIVE_TASK_LOG = None
        self.config.cleanup()

    def response(self, payload):
        response = MagicMock()
        response.read.return_value = json.dumps(payload).encode()
        response.headers.get_content_type.return_value = "application/json"
        response.__enter__.return_value = response
        return response

    def test_save_key_is_private_on_unix(self):
        path = CLIENT_MODULE.config_path()
        self.assertEqual(json.loads(path.read_text())["api_key"], "sk-test-value")
        if os.name != "nt":
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(path.parent.stat().st_mode & 0o777, 0o700)

    def test_save_key_replaces_the_existing_key(self):
        CLIENT_MODULE.save_key("sk-replacement-value")
        self.assertEqual(CLIENT_MODULE.load_key(), "sk-replacement-value")
        self.assertEqual(json.loads(CLIENT_MODULE.config_path().read_text()), {"api_key": "sk-replacement-value"})

    def test_prefers_ai_endpoint(self):
        with patch.object(CLIENT_MODULE.urllib.request, "urlopen", return_value=self.response({"id": "task_1"})) as urlopen:
            response, base = CLIENT_MODULE.json_request("POST", "/v1/videos", {"model": "m"})
        self.assertEqual(response["id"], "task_1")
        self.assertEqual(base, "https://ai.silicogrove.com")
        self.assertEqual(urlopen.call_count, 1)

    def test_falls_back_after_404(self):
        error = urllib.error.HTTPError("https://ai.silicogrove.com/v1/videos", 404, "missing", {}, None)
        with patch.object(CLIENT_MODULE.urllib.request, "urlopen", side_effect=[error, self.response({"id": "task_1"})]) as urlopen:
            _, base = CLIENT_MODULE.json_request("POST", "/v1/videos", {"model": "m"})
        self.assertEqual(base, "https://api.silicogrove.com")
        self.assertEqual(urlopen.call_count, 2)

    def test_falls_back_after_network_error(self):
        with patch.object(CLIENT_MODULE.urllib.request, "urlopen", side_effect=[urllib.error.URLError("unavailable"), self.response({"id": "task_1"})]) as urlopen:
            _, base = CLIENT_MODULE.json_request("POST", "/v1/videos", {"model": "m"})
        self.assertEqual(base, "https://api.silicogrove.com")
        self.assertEqual(urlopen.call_count, 2)

    def test_does_not_fallback_after_server_error(self):
        error = urllib.error.HTTPError("https://ai.silicogrove.com/v1/videos", 503, "unavailable", {}, None)
        with patch.object(CLIENT_MODULE.urllib.request, "urlopen", side_effect=error) as urlopen:
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                CLIENT_MODULE.json_request("POST", "/v1/videos", {"model": "m"})
        self.assertEqual(urlopen.call_count, 1)

    def test_task_id_accepts_openai_response(self):
        self.assertEqual(CLIENT_MODULE.task_id_from({"id": "video_1"}), "video_1")
        self.assertEqual(CLIENT_MODULE.task_id_from({"data": {"task_id": "task_1"}}), "task_1")

    def test_select_default_video_model_prefers_grok_1_5(self):
        response = {"data": [{"id": "video-ds-2.0-fast"}, {"id": "grok-imagine-video"}, {"id": "grok-imagine-video-1.5"}]}
        with patch.object(CLIENT_MODULE, "json_request", return_value=(response, "https://api.example")), contextlib.redirect_stdout(io.StringIO()) as output:
            CLIENT_MODULE.select_default_video_model()
        self.assertEqual(output.getvalue().strip(), "grok-imagine-video-1.5")

    def test_select_default_video_model_uses_grok_fallback(self):
        response = {"data": [{"id": "grok-imagine-video"}, {"id": "video-ds-2.0-fast"}]}
        with patch.object(CLIENT_MODULE, "json_request", return_value=(response, "https://api.example")), contextlib.redirect_stdout(io.StringIO()) as output:
            CLIENT_MODULE.select_default_video_model()
        self.assertEqual(output.getvalue().strip(), "grok-imagine-video")

    def test_generate_persists_a_redacted_task_log(self):
        with tempfile.TemporaryDirectory() as directory:
            prompt = "A private prompt that must not be logged"
            args = SimpleNamespace(
                model="video-ds-2.0-fast", prompt=prompt, seconds="5", aspect_ratio="16:9",
                image=[], video=[], audio=[], output_dir=directory, no_wait=True,
            )
            with patch.object(CLIENT_MODULE, "json_request", return_value=({"id": "task_1"}, "https://api.example")):
                with contextlib.redirect_stdout(io.StringIO()):
                    CLIENT_MODULE.generate(args)
            logs = list(Path(directory).glob("silicogrove-task-*.jsonl"))
            self.assertEqual(len(logs), 1)
            contents = logs[0].read_text()
            self.assertIn('"task_id": "task_1"', contents)
            self.assertIn('"event": "task_submitted"', contents)
            self.assertNotIn(prompt, contents)
            if os.name != "nt":
                self.assertEqual(logs[0].stat().st_mode & 0o777, 0o600)

    def test_fail_persists_the_summarized_error(self):
        with tempfile.TemporaryDirectory() as directory:
            task_log = CLIENT_MODULE.TaskLog(directory, "generate")
            CLIENT_MODULE.ACTIVE_TASK_LOG = task_log
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                CLIENT_MODULE.fail("Silico Grove could not complete the video request. Please retry later.")
            self.assertIn('"event": "error"', task_log.path.read_text())

    def test_audio_webm_is_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sound.webm"
            path.write_bytes(b"audio")
            self.assertEqual(CLIENT_MODULE.validate_reference("audio", path), path.resolve())

    def test_oversized_reference_is_rejected_before_upload(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "image.png"
            path.write_bytes(b"x" * (CLIENT_MODULE.MAX_FILE_BYTES["image"] + 1))
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                CLIENT_MODULE.validate_reference("image", path)

    def test_public_reference_url_is_not_uploaded(self):
        with patch.object(CLIENT_MODULE, "upload_reference") as upload:
            url, base = CLIENT_MODULE.reference_url("image", "https://cdn.example.com/reference.png")
        self.assertEqual(url, "https://cdn.example.com/reference.png")
        self.assertIsNone(base)
        upload.assert_not_called()

    def test_reference_count_limit_only_applies_to_documented_models(self):
        references = [f"https://cdn.example.com/reference-{index}.png" for index in range(5)]
        other_model = SimpleNamespace(model="another-video-model", image=references, video=[], audio=[])
        documented_model = SimpleNamespace(model="video-ds-2.0", image=references, video=[], audio=[])
        self.assertEqual(CLIENT_MODULE.collect_references(other_model)[0]["images"], references)
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            CLIENT_MODULE.collect_references(documented_model)

if __name__ == "__main__":
    unittest.main()
