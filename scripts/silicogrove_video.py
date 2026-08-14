#!/usr/bin/env python3
"""Portable standard-library client for the Silico Grove Video API."""

import argparse
import getpass
import json
import mimetypes
import os
import secrets
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE_URLS = ("https://ai.silicogrove.com", "https://api.silicogrove.com")
POLL_INTERVAL_SECONDS = 10
DEFAULT_TIMEOUT_SECONDS = 300
MAX_REFERENCES = {"image": 4, "video": 3, "audio": 1}
REFERENCE_LIMITED_MODELS = {"video-ds-2.0", "video-ds-2.0-fast", "as-sd2.0-fast"}
EXTENSIONS = {
    "image": {".jpg", ".jpeg", ".png", ".webp"},
    "video": {".mp4", ".mov", ".webm"},
    "audio": {".mp3", ".m4a", ".wav", ".aac", ".ogg", ".webm"},
}
MAX_FILE_BYTES = {"image": 10 * 1024 * 1024, "video": 100 * 1024 * 1024, "audio": 20 * 1024 * 1024}
ACTIVE_TASK_LOG = None


def config_path():
    if os.name == "nt":
        root = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        root = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return root / "silicogrove-video" / "config.json"


def fail(message):
    if ACTIVE_TASK_LOG:
        ACTIVE_TASK_LOG.event("error", message=message)
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(1)


def private_mode(path, mode):
    if os.name != "nt":
        os.chmod(path, mode)


class TaskLog:
    """Persist non-sensitive request state so a task can be recovered after a lost terminal."""

    def __init__(self, output_dir, action, task_id=None):
        directory = Path(output_dir).expanduser().resolve()
        directory.mkdir(parents=True, exist_ok=True)
        name = f"silicogrove-task-{time.strftime('%Y%m%d-%H%M%S')}-{secrets.token_hex(4)}.jsonl"
        self.path = directory / name
        self.event("started", action=action, task_id=task_id)

    def event(self, event, **details):
        payload = {"time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "event": event, **details}
        try:
            with open(self.path, "a", encoding="utf-8") as handle:
                private_mode(self.path, 0o600)
                json.dump(payload, handle, sort_keys=True)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
        except OSError:
            pass


def save_key(key):
    key = key.strip()
    if not key:
        fail("API key cannot be empty.")
    path = config_path()
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    private_mode(path.parent, 0o700)
    temporary = path.parent / f".{path.name}.{secrets.token_hex(8)}.tmp"
    try:
        with open(temporary, "w", encoding="utf-8") as handle:
            private_mode(temporary, 0o600)
            json.dump({"api_key": key}, handle)
            handle.write("\n")
        os.replace(temporary, path)
        private_mode(path, 0o600)
    finally:
        if temporary.exists():
            temporary.unlink()


def load_key():
    try:
        with open(config_path(), encoding="utf-8") as handle:
            key = json.load(handle).get("api_key", "").strip()
    except (OSError, json.JSONDecodeError):
        key = ""
    if not key:
        fail("No Silico Grove API key is saved. Ask the user for their key, then run config --set-key or config --set-key-stdin.")
    return key


def request_failure_summary(failures):
    statuses = {status for kind, status in failures if kind == "http"}
    if 401 in statuses:
        return "Silico Grove could not authenticate the request. Check the saved API key and its access."
    if 403 in statuses:
        return "Silico Grove did not authorize this video request. Check API key access, model availability, and balance."
    if 429 in statuses:
        return "Silico Grove is rate-limiting video requests. Retry after a short delay."
    if any(status >= 500 for status in statuses) or any(kind == "network" for kind, _ in failures):
        return "Silico Grove video service is temporarily unavailable. Please retry later."
    return "Silico Grove could not complete the video request. Please retry later."


def api_request(method, endpoint, body=None, content_type=None, base_url=None):
    headers = {"Authorization": f"Bearer {load_key()}", "User-Agent": "SilicoGroveVideoSkill/1.0 (portable local client)"}
    if content_type:
        headers["Content-Type"] = content_type
    bases = BASE_URLS if base_url is None else (base_url,) + tuple(base for base in BASE_URLS if base != base_url)
    failures = []
    for index, base in enumerate(bases):
        request = urllib.request.Request(base + endpoint, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=DEFAULT_TIMEOUT_SECONDS) as response:
                return response.read(), response.headers.get_content_type(), base
        except urllib.error.HTTPError as error:
            failures.append(("http", error.code))
            if index == 0 and error.code == 404:
                continue
            fail(request_failure_summary(failures))
        except (urllib.error.URLError, TimeoutError):
            failures.append(("network", None))
            if index == 0:
                continue
            fail(request_failure_summary(failures))
    fail(request_failure_summary(failures))


def json_request(method, endpoint, payload=None, base_url=None):
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    raw, _, used_base = api_request(method, endpoint, body, "application/json" if body else None, base_url)
    try:
        result = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        fail("Silico Grove returned an invalid video response. Please retry later.")
    if not isinstance(result, dict):
        fail("Silico Grove returned an invalid video response. Please retry later.")
    return result, used_base


def multipart(fields, file_path):
    boundary = "----SilicoGrove" + secrets.token_hex(16)
    path = Path(file_path)
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    parts = []
    for name, value in fields.items():
        parts.extend([f"--{boundary}\r\n".encode(), f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode(), str(value).encode(), b"\r\n"])
    parts.extend([f"--{boundary}\r\n".encode(), f'Content-Disposition: form-data; name="file"; filename="{path.name}"\r\n'.encode(), f"Content-Type: {mime}\r\n\r\n".encode(), path.read_bytes(), b"\r\n", f"--{boundary}--\r\n".encode()])
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def validate_reference(kind, raw_path):
    path = Path(raw_path).expanduser().resolve()
    if not path.is_file():
        fail(f"Reference file does not exist: {path}")
    if path.suffix.lower() not in EXTENSIONS[kind]:
        allowed = ", ".join(sorted(EXTENSIONS[kind]))
        fail(f"Unsupported {kind} reference format. Choose one of: {allowed}")
    if path.stat().st_size > MAX_FILE_BYTES[kind]:
        fail(f"{kind.capitalize()} reference exceeds the {MAX_FILE_BYTES[kind] // (1024 * 1024)} MiB upload limit.")
    return path


def upload_reference(kind, raw_path, task_log=None):
    path = validate_reference(kind, raw_path)
    if task_log:
        task_log.event("reference_upload_started", kind=kind)
    body, content_type = multipart({"kind": kind}, path)
    raw, _, used_base = api_request("POST", "/pg/assets", body, content_type)
    try:
        result = json.loads(raw.decode("utf-8"))
        url = result["data"]["url"]
    except (KeyError, TypeError, UnicodeDecodeError, json.JSONDecodeError):
        fail("Silico Grove did not return a usable reference asset URL.")
    if not isinstance(url, str) or not url.startswith(("https://", "http://")):
        fail("Silico Grove did not return a usable reference asset URL.")
    if task_log:
        task_log.event("reference_upload_completed", kind=kind)
    return url, used_base


def is_public_url(value):
    parsed = urllib.parse.urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def reference_url(kind, value, task_log=None):
    if is_public_url(value):
        return value, None
    return upload_reference(kind, value, task_log)


def collect_references(args, task_log=None):
    supplied = {"image": args.image, "video": args.video, "audio": args.audio}
    result = {}
    used_base = None
    for kind, paths in supplied.items():
        if args.model in REFERENCE_LIMITED_MODELS and len(paths) > MAX_REFERENCES[kind]:
            fail(f"At most {MAX_REFERENCES[kind]} {kind} reference file(s) are allowed.")
        urls = []
        for value in paths:
            url, reference_base = reference_url(kind, value, task_log)
            if reference_base:
                used_base = reference_base
            urls.append(url)
        if urls:
            result[kind + "s"] = urls
    return result, used_base


def task_id_from(response):
    nested = response.get("data") if isinstance(response.get("data"), dict) else response
    task_id = nested.get("id") or nested.get("task_id")
    if not isinstance(task_id, str) or not task_id:
        fail("Silico Grove did not return a video task ID.")
    return task_id


def task_status(response):
    nested = response.get("data") if isinstance(response.get("data"), dict) else response
    value = nested.get("status", "")
    return value.lower() if isinstance(value, str) else ""


def download_task(task_id, output_dir, base_url, task_log=None):
    raw, content_type, _ = api_request("GET", f"/v1/videos/{urllib.parse.quote(task_id, safe='')}/content", base_url=base_url)
    if not raw:
        fail("Silico Grove returned an empty video file.")
    suffix = ".mp4" if "mp4" in content_type else ".webm" if "webm" in content_type else ".mp4"
    directory = Path(output_dir).expanduser().resolve()
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"silicogrove-{time.strftime('%Y%m%d-%H%M%S')}-{task_id}{suffix}"
    path.write_bytes(raw)
    if task_log:
        task_log.event("result_downloaded", task_id=task_id, result_path=str(path))
    print(str(path))


def wait_for_task(task_id, output_dir, base_url, task_log=None):
    while True:
        response, used_base = json_request("GET", f"/v1/videos/{urllib.parse.quote(task_id, safe='')}", base_url=base_url)
        status = task_status(response)
        if task_log:
            task_log.event("task_status", task_id=task_id, status=status or "unknown")
        if status in {"completed", "succeeded", "success"}:
            download_task(task_id, output_dir, used_base, task_log)
            return
        if status in {"failed", "cancelled", "canceled", "error"}:
            fail("Silico Grove video generation did not complete. Check the prompt and model access, then retry.")
        time.sleep(POLL_INTERVAL_SECONDS)


def list_models():
    response, _ = json_request("GET", "/v1/models")
    models = response.get("data")
    if not isinstance(models, list):
        fail("Silico Grove returned an invalid model list.")
    for model in models:
        if isinstance(model, dict) and isinstance(model.get("id"), str):
            print(model["id"])


def generate(args):
    global ACTIVE_TASK_LOG
    task_log = TaskLog(args.output_dir, "generate")
    ACTIVE_TASK_LOG = task_log
    print(f"Task log: {task_log.path}")
    if not args.model.strip() or not args.prompt.strip():
        fail("model and prompt cannot be empty.")
    if not args.seconds.isdigit() or int(args.seconds) <= 0:
        fail("seconds must be a positive whole-number string.")
    if args.aspect_ratio not in {"16:9", "9:16", "1:1"}:
        fail("aspect-ratio must be 16:9, 9:16, or 1:1.")
    reference_counts = {"images": len(args.image), "videos": len(args.video), "audios": len(args.audio)}
    task_log.event("request_validated", model=args.model, seconds=args.seconds, aspect_ratio=args.aspect_ratio, **reference_counts)
    references, upload_base = collect_references(args, task_log)
    payload = {"model": args.model, "prompt": args.prompt, "seconds": args.seconds, "aspect_ratio": args.aspect_ratio, **references}
    response, used_base = json_request("POST", "/v1/videos", payload, base_url=upload_base)
    task_id = task_id_from(response)
    task_log.event("task_submitted", task_id=task_id)
    if args.no_wait:
        print(task_id)
        return
    wait_for_task(task_id, args.output_dir, used_base, task_log)


def main():
    parser = argparse.ArgumentParser(description="Silico Grove Video API client")
    commands = parser.add_subparsers(dest="action", required=True)
    config = commands.add_parser("config")
    config.add_argument("--show-status", action="store_true")
    config.add_argument("--set-key", action="store_true")
    config.add_argument("--set-key-stdin", action="store_true")
    commands.add_parser("models")
    generate_parser = commands.add_parser("generate")
    generate_parser.add_argument("--model", required=True)
    generate_parser.add_argument("--prompt", required=True)
    generate_parser.add_argument("--seconds", default="10")
    generate_parser.add_argument("--aspect-ratio", default="16:9")
    generate_parser.add_argument("--image", action="append", default=[])
    generate_parser.add_argument("--video", action="append", default=[])
    generate_parser.add_argument("--audio", action="append", default=[])
    generate_parser.add_argument("--output-dir", default="outputs")
    generate_parser.add_argument("--no-wait", action="store_true")
    status = commands.add_parser("status")
    status.add_argument("task_id")
    status.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()
    if args.action == "generate":
        generate(args)
    elif args.action == "status":
        global ACTIVE_TASK_LOG
        ACTIVE_TASK_LOG = TaskLog(args.output_dir, "status", args.task_id)
        print(f"Task log: {ACTIVE_TASK_LOG.path}")
        wait_for_task(args.task_id, args.output_dir, None, ACTIVE_TASK_LOG)
    elif args.action == "models":
        list_models()
    elif args.set_key_stdin:
        save_key(sys.stdin.read())
        print("Silico Grove API key saved securely.")
    elif args.set_key:
        try:
            save_key(getpass.getpass("Silico Grove API Key: "))
        except (EOFError, KeyboardInterrupt):
            fail("API key entry was cancelled.")
        print("Silico Grove API key saved securely.")
    elif args.show_status:
        print("configured" if config_path().is_file() else "not configured")
    else:
        fail("Use --show-status, --set-key, or --set-key-stdin.")


if __name__ == "__main__":
    main()
