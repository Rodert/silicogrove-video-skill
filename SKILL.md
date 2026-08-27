---
name: silicogrove-video
description: Generate text-to-video and reference-guided videos through the Silico Grove API. Use when a user asks to create, render, download, or check a Silico Grove video-generation job, including video prompts with local image, video, or audio references.
---

# Silico Grove Video

Run the bundled client from this Skill's directory. Resolve `SKILL_DIR` as the directory containing this `SKILL.md`; do not use an absolute path from another machine.

## Daily update check

Before the first request in a 24-hour period, run:

```bash
python3 "$SKILL_DIR/scripts/check_update.py" "$SKILL_DIR"
```

The script stores only a timestamp in the user's cache and returns `skipped`, `checked`, `updated`, `failed`, or `unavailable`. Keep `skipped` and `checked` silent. If it returns `updated`, re-read this `SKILL.md` before continuing. For `failed` or `unavailable`, continue with the installed version and mention the issue only if it affects the request. When an update is available, it fetches `origin/main` and force-resets tracked skill files to that revision; local tracked changes are intentionally discarded, while untracked files are kept. Install the skill by cloning its Git repository and preserve its `.git` directory.

The client sends requests to `https://ai.silicogrove.com` first. It automatically retries `https://api.silicogrove.com` only after a network error, timeout, or HTTP 404. `api` is the primary site; `ai` is its traffic-relief endpoint. Do not manually change this routing or retry another HTTP response, because a video submission may already have been accepted and billed.

## Credential workflow

1. Run the requested client command directly. If it reports that no key is saved, ask: `Please provide your Silico Grove API Key (sk-...). I will save it locally for future Silico Grove video requests. If you do not have one, sign in at https://api.silicogrove.com/keys and create a key with access to a video model.` When the user provides a new key, save it even if one is already configured; the new key replaces the old key, which may have expired.
2. Keep the key out of prompts, project files, output, and terminal arguments.
3. When the runtime supports interactive terminal input, run `config --set-key` and enter the key without echoing it.
4. When an Agent can securely send an already-provided key through process standard input, use `config --set-key-stdin`. Do not put it in a command-line argument or environment variable.

The client stores the key in the current user's configuration directory (`~/.config/silicogrove-video/config.json` on macOS/Linux, or `$XDG_CONFIG_HOME/silicogrove-video/config.json` when set; `%APPDATA%\\silicogrove-video\\config.json` on Windows) using owner-only permissions where supported.

## Generate

If the user specifies a model, use it without replacing it. If no model is specified, run the following exactly once before generating:

```bash
python3 "$SKILL_DIR/scripts/silicogrove_video.py" select-model
```

It queries `GET /v1/models` once and returns the first visible model in this order: `grok-imagine-video-1.5`, `grok-imagine-video`, `video-ds-2.0-fast`, `video-ds-2.0`, `as-sd2.0-fast`, `kling-video-v3`. Use the returned model directly. If the user asks to choose a model or asks which video models are available, run `python3 "$SKILL_DIR/scripts/silicogrove_video.py" video-models` once, show the returned video candidates, and wait for their selection. Do not show models during the automatic path. If no supported video model is visible, report that result rather than trying arbitrary models. Pass video length as a string, usually `"5"`, `"10"`, or `"15"`, and use `16:9`, `9:16`, or `1:1` for the aspect ratio.

## Grok video protocol

Use the exact schema for the selected Grok model; do not translate its image fields into the generic `images` array. The bundled client validates these rules before it uploads an asset or submits a task. For all details and future extensions, read `references/api.md`.

- `grok-imagine-video` is text-to-video only. Do not pass `--image`, `--reference-image`, `--video`, or `--audio`.
- `grok-imagine-video-1.5` supports text, one first-frame image, or one to seven reference images. Its `--seconds` must be `4`, `6`, `8`, `10`, `12`, or `15`; `--resolution` must be `480p`, `720p`, or `1080p`. When omitted, the client explicitly sends `720p`.
- First-frame mode uses exactly one `--image`; the client sends the singular API field `image`. It can use up to `1080p`.
- Reference-image mode uses one to seven `--reference-image` arguments; the client sends `reference_images`. It cannot be combined with `--image`, `--video`, or `--audio`, and it is limited to `480p` or `720p`. In the prompt, refer to these images as `<IMAGE_1>` through `<IMAGE_7>` when useful.

```bash
python3 "$SKILL_DIR/scripts/silicogrove_video.py" generate \
  --model grok-imagine-video-1.5 \
  --prompt 'A cinematic 9:16 product video of a silver espresso machine, slow orbiting camera, morning light, realistic, no watermark.' \
  --seconds 10 --aspect-ratio 9:16 --resolution 720p --output-dir ./outputs
```

```bash
python3 "$SKILL_DIR/scripts/silicogrove_video.py" generate \
  --model grok-imagine-video-1.5 \
  --prompt 'The provided image is the first frame. The man transforms into an armored warrior and flies into the sky.' \
  --image /absolute/path/to/first-frame.jpg \
  --seconds 8 --aspect-ratio 16:9 --resolution 1080p --output-dir ./outputs
```

```bash
python3 "$SKILL_DIR/scripts/silicogrove_video.py" generate \
  --model grok-imagine-video-1.5 \
  --prompt 'Keep <IMAGE_1> recognizable while creating a polished cinematic motion shot.' \
  --reference-image /absolute/path/to/person.jpg \
  --seconds 8 --aspect-ratio 16:9 --resolution 720p --output-dir ./outputs
```

For non-Grok-1.5 reference-capable models, pass a publicly accessible `http(s)` URL directly, or pass a local file with `--image`, `--video`, or `--audio`; local files are uploaded to Silico Grove's temporary asset service. Local uploads are limited to 10 MiB for images, 100 MiB for videos, and 20 MiB for audio; uploaded assets expire after 24 hours. The 4-image, 3-video, and 1-audio limits apply to `video-ds-2.0`, `video-ds-2.0-fast`, and `as-sd2.0-fast`; confirm limits for other models from their model documentation.

```bash
python3 "$SKILL_DIR/scripts/silicogrove_video.py" generate \
  --model video-ds-2.0 \
  --prompt 'Use the person in the image and the motion in the clip; create a natural vertical scene.' \
  --seconds 15 --aspect-ratio 9:16 \
  --image /absolute/path/to/reference.jpg \
  --video /absolute/path/to/motion.mp4 \
  --output-dir ./outputs
```

The client creates a private JSONL task log in the output directory before every `generate` or `status` request. It records the task ID, upload and polling state, result path, and summarized errors, but never the API key, prompt, reference URLs, or raw server responses. Return the log path with every request result. If terminal output is lost, inspect that log before retrying; use its task ID with `status TASK_ID --output-dir ./outputs` to resume an accepted task. The client waits for completion, then writes an MP4 path. Add `--no-wait` to return the task ID immediately.

## Error handling

Report only the bundled client's summarized error. Do not expose request URLs, upstream host names, HTTP response bodies, proxy or firewall details, or API keys. For authentication or authorization errors, ask the user to verify their saved key, model access, and balance. For rate limits or temporary service failures, ask them to retry later. See `references/api.md` before extending request fields or endpoint behavior.
