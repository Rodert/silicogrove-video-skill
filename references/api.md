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
- `grok-video-1.5` is the current recommended Grok model. It accepts `model`, `prompt`, optional string `seconds` (`"6"`, `"8"`, `"10"`, `"12"`, or `"15"`), optional `aspect_ratio`, optional `resolution` (the API recommends `720p`), and optional `image_urls` of up to seven public URLs or full data URLs. When no `seconds` is submitted, the API defaults to 15 seconds. The client explicitly sends 720p unless the caller chooses a resolution. Do not send video or audio references.
- `images` is a compatibility alias for `image_urls`; do not send both. `reference_images` and `input_reference` are compatibility fields. The client uses `image_urls` for `grok-video-1.5`.
- `kling-video-v3` and `kling-video-v3-omni` accept 3-15 seconds and resolutions `720p`, `1080p`, or `4k`; `kling-video-v3-turbo` accepts 3-15 seconds and `720p` or `1080p`. Send `resolution` as a top-level field; do not use image-generation `quality`.
- `grok-imagine-video` and `grok-imagine-video-1.5` are currently retired upstream. They remain legacy compatibility paths only and must not be default candidates.
- Other reference-capable models use optional `images`, `videos`, and `audios` arrays. Always use the model list returned for the current key and consult its model documentation before adding fields.
- Reference limits: 4 images, 3 videos, and 1 audio apply to `video-ds-2.0`, `video-ds-2.0-fast`, and `as-sd2.0-fast`. Other models may differ.

Use a visible model name from `GET /v1/models`; availability depends on the API key and group. Common video task responses use `id` or `task_id` and statuses including `queued`, `in_progress`, `processing`, `completed`, `succeeded`, `failed`, or `cancelled`.

Source: https://docs.silicogrove.com/zh-cn/api/#videos
