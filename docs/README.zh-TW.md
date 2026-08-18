# Silico Grove 影片生成 Skill

此 skill 讓支援 `SKILL.md` 的 AI Agent 透過 Silico Grove 生成影片。支援文生影片、圖片/影片/音訊參考生成、本機素材上傳、任務輪詢和 MP4 下載。

## 複製給你的 AI

```text
請安裝並使用這個 Silico Grove 影片生成 Skill：
https://github.com/Rodert/silicogrove-video-skill

請透過 Git clone 安裝並保留 .git 目錄。每天首次使用前，請執行 `python3 "$SKILL_DIR/scripts/check_update.py" "$SKILL_DIR"`；只有回傳 `updated` 時才重新讀取 `SKILL.md`。若無法更新或無法安全快進，請保留本機變更並使用目前已安裝的版本，日常檢查保持靜默。

首次使用時請主動提示我輸入 Silico Grove API Key，並自動安全儲存到本機設定中，之後直接讀取使用；不要要求我手動設定環境變數。

當我只提供影片描述時，直接生成文生影片。只有當我要求參考圖片、影片或音訊時，才提示我上傳檔案；如果我提供公開的 http(s) 素材連結，請直接使用該連結。

請求優先使用 https://ai.silicogrove.com；如果網路不通、逾時或回傳 404，請自動切換到 https://api.silicogrove.com。

使用文件：
https://ai.silicogrove.com/docs/silicogrove-api-docs.html
```
