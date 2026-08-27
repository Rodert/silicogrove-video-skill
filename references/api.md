# Silico Grove Video API

- Preferred base URL: `https://ai.silicogrove.com`
- Primary fallback URL: `https://api.silicogrove.com`
- Auth: `Authorization: Bearer sk-...`
- Discover models: `GET /v1/models`; model visibility depends on the API key and user group.
- Submit: `POST /v1/videos` with JSON fields `model`, `prompt`, optional string `seconds`, `aspect_ratio`, `images`, `videos`, and `audios`.
- Check task: `GET /v1/videos/{task_id}`.
- Download result: `GET /v1/videos/{task_id}/content`.
- References: send a public URL directly in `images`, `videos`, or `audios`, or upload a local file with `POST /pg/assets` multipart fields `kind` (`image`, `video`, or `audio`) and `file`; the response is `{ "data": { "url": "..." } }`.
- Local uploads: images are jpg/png/webp up to 10 MiB; videos are mp4/mov/webm up to 100 MiB; audio is mp3/m4a/wav/aac/ogg/webm up to 20 MiB. Assets expire after 24 hours.
- Common video models include `video-ds-2.0`, `as-sd2.0-fast`, `kling-video-v3`, `grok-imagine-video`, and `grok-imagine-video-1.5`. Always use the model list returned for the current key.
- Reference limits: 4 images, 3 videos, and 1 audio apply to `video-ds-2.0`, `video-ds-2.0-fast`, and `as-sd2.0-fast`. Other models may differ.

Use a visible model name from `GET /v1/models`; availability depends on the API key and group. Common video task responses use `id` or `task_id` and statuses including `queued`, `in_progress`, `processing`, `completed`, `succeeded`, `failed`, or `cancelled`.

Source: https://ai.silicogrove.com/docs/silicogrove-api-docs.html
