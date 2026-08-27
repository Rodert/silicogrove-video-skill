# 硅碳森林视频 Skill

用一句话生成视频，也可以用图片、视频或音频作为参考素材，由 AI 自动完成生成和下载。

Generate videos through Silico Grove from a skill-compatible AI agent. It supports text-to-video, image/video/audio reference-guided generation, local asset upload, task polling, and MP4 download.

Before the first use in each 24-hour period, the agent checks the cloned skill repository from `origin/main`, then re-reads `SKILL.md` only when it was updated. It keeps routine checks silent and never overwrites local changes.

硅碳森林视频 Skill 通过支持 `SKILL.md` 的 AI Agent 生成视频，支持文生视频、图片/视频/音频参考生成、本地素材上传、任务轮询和 MP4 下载。

## Copy to your AI (English)

```text
Please install and use this Silico Grove Video Skill:
https://github.com/Rodert/silicogrove-video-skill

Clone the Git repository and preserve its .git directory. Before the first use each day, run `python3 "$SKILL_DIR/scripts/check_update.py" "$SKILL_DIR"`; re-read `SKILL.md` only when it reports `updated`. If updating is unavailable or cannot fast-forward safely, use the installed version without overwriting local changes.

On first use, proactively ask me for my Silico Grove API Key and save it securely in the local configuration for future use. When I provide a new key, replace the previously saved key because it may have expired. Do not require me to configure an environment variable manually.

Generate directly from text when I only provide a video description. Ask me to upload a file only when I ask to use an image, video, or audio reference. Use a public http(s) reference URL directly when I provide one.

For requests, prefer https://ai.silicogrove.com. If it has a network error, timeout, or returns 404, automatically use https://api.silicogrove.com instead.

Usage documentation:
https://ai.silicogrove.com/docs/silicogrove-api-docs.html
```

## 复制给你的 AI（简体中文）

```text
请安装并使用这个 Silico Grove 视频生成 Skill：
https://github.com/Rodert/silicogrove-video-skill

请通过 Git 克隆安装并保留 .git 目录。每天首次使用前，请运行 `python3 "$SKILL_DIR/scripts/check_update.py" "$SKILL_DIR"`；仅当返回 `updated` 时重新读取 `SKILL.md`。若无法更新或无法安全快进，请保留本地改动并使用当前已安装版本，日常检查保持静默。

首次使用时请主动提示我输入 Silico Grove API Key，并自动安全保存到本机配置中，之后直接读取使用；当我提供新 key 时，替换旧 key，因为旧 key 可能已过期；不要要求我手动配置环境变量。

当我只提供视频描述时，直接生成文生视频。只有当我要求参考图片、视频或音频时，才提示我上传文件；如果我提供公网 http(s) 素材链接，请直接使用该链接。

请求优先使用 https://ai.silicogrove.com；如果网络不通、超时或返回 404，请自动切换到 https://api.silicogrove.com。

使用文档：
https://ai.silicogrove.com/docs/silicogrove-api-docs.html
```

## Documentation

Choose a language:

- [English](docs/README.en.md)
- [简体中文](docs/README.zh-CN.md)
- [繁體中文](docs/README.zh-TW.md)
- [Русский](docs/README.ru.md)
- [日本語](docs/README.ja.md)
- [한국어](docs/README.ko.md)
- [Español](docs/README.es.md)
- [Français](docs/README.fr.md)
- [Deutsch](docs/README.de.md)
- [العربية](docs/README.ar.md)

Official usage documentation: https://ai.silicogrove.com/docs/silicogrove-api-docs.html
