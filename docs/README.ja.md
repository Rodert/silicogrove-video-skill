# Silico Grove 動画生成 Skill

この skill は、対応する AI Agent から Silico Grove を通じて動画を生成します。テキストからの動画生成、画像/動画/音声の参照生成、ローカル素材のアップロード、タスク確認、MP4 ダウンロードに対応しています。

## AI にコピー

```text
次の Silico Grove 動画生成 Skill をインストールして使用してください。
https://github.com/Rodert/silicogrove-video-skill

Git clone でインストールし、.git ディレクトリを保持してください。毎日の最初の使用前に `python3 "$SKILL_DIR/scripts/check_update.py" "$SKILL_DIR"` を実行し、`updated` の場合だけ `SKILL.md` を再読してください。更新できない場合や安全に fast-forward できない場合は、ローカルの変更を保持してインストール済みのバージョンを使用してください。

初回使用時には Silico Grove API Key の入力を私に求め、今後使えるようローカル設定に安全に保存してください。環境変数を手動で設定するよう私に求めないでください。

私が動画の説明だけを渡した場合は、すぐにテキストから動画を生成してください。画像、動画、または音声の参照を使いたいと私が指定した場合のみ、ファイルのアップロードを求めてください。公開 http(s) URL を渡した場合は直接使用してください。

リクエストにはまず https://ai.silicogrove.com を使用してください。ネットワークエラー、タイムアウト、または 404 が発生した場合は、https://api.silicogrove.com に自動で切り替えてください。

使用ドキュメント：
https://ai.silicogrove.com/docs/silicogrove-api-docs.html
```
