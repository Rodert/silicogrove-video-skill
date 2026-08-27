# Silico Grove Video API

- Preferred base URL: `https://ai.silicogrove.com`
- Primary fallback URL: `https://api.silicogrove.com`
- Auth: `Authorization: Bearer sk-...`
- Discover models: `GET /v1/models`; model visibility depends on the API key and user group.
- Submit: `POST /v1/videos` with a model-specific JSON schema. Do not assume generic reference fields apply to every model.
- Check task: `GET /v1/videos/{task_id}`.
- Download result: `GET /v1/videos/{task_id}/content`.
- References: send a public URL directly in `images`, `videos`, or `audios`, or upload a local file with `POST /pg/assets` multipart fields `kind` (`image`, `video`, or `audio`) and `file`; the response is `{ "data": { "url": "..." } }`.
- Local uploads: images are jpg/png/webp up to 10 MiB; videos are mp4/mov/webm up to 100 MiB; audio is mp3/m4a/wav/aac/ogg/webm up to 20 MiB. Assets expire after 24 hours.
- `grok-imagine-video`: text-to-video only. Do not send `image`, `images`, `reference_images`, `videos`, or `audios`.
- `grok-imagine-video-1.5`: accepts `model`, `prompt`, string `seconds` (`"4"`, `"6"`, `"8"`, `"10"`, `"12"`, or `"15"`), `aspect_ratio`, and `resolution` (`480p`, `720p`, or `1080p`). The client sends `720p` when the caller does not choose one. Its image modes are mutually exclusive:
  - First-frame mode: send one singular `image` URL or data URL. It fixes the opening frame and may use up to `1080p`.
  - Reference-image mode: send `reference_images` as an array of one to seven URLs. It guides identity/style without fixing the opening frame; prompts may address them as `<IMAGE_1>` through `<IMAGE_7>`. It may use only `480p` or `720p`.
  - Never mix `image`, `images`, `image_urls`, or `input_reference` with `reference_images`. Do not send video or audio references to this model.
- Other reference-capable models use optional `images`, `videos`, and `audios` arrays. Common models include `video-ds-2.0`, `as-sd2.0-fast`, and `kling-video-v3`; always use the model list returned for the current key and consult its model documentation before adding fields.
- Reference limits: 4 images, 3 videos, and 1 audio apply to `video-ds-2.0`, `video-ds-2.0-fast`, and `as-sd2.0-fast`. Other models may differ.

Use a visible model name from `GET /v1/models`; availability depends on the API key and group. Common video task responses use `id` or `task_id` and statuses including `queued`, `in_progress`, `processing`, `completed`, `succeeded`, `failed`, or `cancelled`.

Source: https://docs.silicogrove.com/zh-cn/api/#videos
