# Silico Grove 영상 생성 Skill

이 skill은 호환되는 AI Agent가 Silico Grove를 통해 영상을 생성하도록 합니다. 텍스트 기반 영상 생성, 이미지/영상/오디오 참조 생성, 로컬 파일 업로드, 작업 조회 및 MP4 다운로드를 지원합니다.

## AI에 복사

```text
다음 Silico Grove 영상 생성 Skill을 설치하고 사용해 주세요.
https://github.com/Rodert/silicogrove-video-skill

Git clone으로 설치하고 .git 디렉터리를 유지해 주세요. 매일 처음 사용하기 전에 `python3 "$SKILL_DIR/scripts/check_update.py" "$SKILL_DIR"`를 실행하고, 결과가 `updated`일 때만 `SKILL.md`를 다시 읽어 주세요. 업데이트가 있으면 추적되는 Skill 파일을 `origin/main`으로 강제 재설정하여 로컬 추적 변경을 버립니다. 업데이트할 수 없으면 현재 버전을 사용해 주세요.

처음 사용할 때 Silico Grove API Key를 입력하라고 먼저 안내하고, 이후 사용할 수 있도록 로컬 설정에 안전하게 저장해 주세요. 환경 변수를 직접 설정하라고 요구하지 마세요.

제가 영상 설명만 제공하면 즉시 텍스트 기반 영상을 생성해 주세요. 이미지, 영상 또는 오디오 참조를 사용해 달라고 요청할 때만 파일 업로드를 안내해 주세요. 공개 http(s) URL을 제공하면 직접 사용해 주세요.

요청에는 먼저 https://ai.silicogrove.com을 사용해 주세요. 네트워크 오류, 시간 초과 또는 404가 발생하면 https://api.silicogrove.com으로 자동 전환해 주세요.

사용 문서:
https://ai.silicogrove.com/docs/silicogrove-api-docs.html
```
