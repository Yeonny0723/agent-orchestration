---
name: setup-orchestration
description: Codex와 Claude Code에서 agent-orchestration 플러그인, 사용자 skill 링크와 개인 marketplace 등록 상태를 점검할 때 사용한다.
---

# 오케스트레이션 설정

## 원칙

설치는 사용자 범위에서 대화형으로 수행한다. 기존 파일이나 디렉터리를 덮어쓰지 않고, 변경 항목마다 경로와 명령을 보여준 뒤 항목별 승인을 받는다.

## 선택형 외부 skill

`superpowers`, `grill-with-docs`, `domain-modeling`, `stop-slop`, `humanizer`는 설치돼 있으면 관련 skill이 활용할 수 있다. 누락돼도 플러그인 설치 완료나 기본 workflow를 차단하지 않는다. 선택하지 않은 항목은 작업을 차단하지 않는다. 사용자가 설치를 원할 때만 원본, 설치 위치, 명령과 변경 범위를 보여주고 항목별 승인을 받는다.

작성 보조 skill 설치 명령은 다음과 같다.

```powershell
npx skills add hardikpandya/stop-slop --global --skill stop-slop
npx skills add blader/humanizer --global --skill humanizer
```

둘 다, 하나만 또는 둘 다 선택하지 않는 결정을 허용한다. 설치할 때 최신 `main`을 사용하며 기존 설치를 자동 업데이트하지 않는다. 사용자가 명시적으로 업데이트를 요청했을 때만 별도 승인 후 갱신한다.

같은 이름과 같은 원본이면 설치 완료로 판단한다. 같은 이름이 다른 원본을 가리키거나 대상 경로가 기대한 skill 링크가 아니면 덮어쓰지 않고 충돌을 보고한다.

## 사용자 skill과 marketplace

1. 사용자 skill의 단일 원본은 `~/.agents/skills/<skill-name>`에 둔다.
2. Claude Code의 `~/.claude/skills/<skill-name>`에는 Windows에서 directory junction, Unix 계열에서 symbolic link를 만든다.
3. 대상 경로에 기대한 링크가 아닌 항목이 있으면 덮어쓰지 않고 충돌 경로와 유형을 보고한 뒤 중단한다.
4. 동일한 plugin source를 Codex와 Claude Code의 개인 marketplace에 각각 등록한다. 각 등록도 별도 승인을 받는다.
5. 이미 올바른 링크나 등록이면 성공으로 처리하고 재생성하지 않는다.
6. 성공, 실패, 충돌과 사용자가 거절한 항목을 구분해 최종 상태를 보고한다.

## 금지 사항

- 외부 skill을 필수 의존성으로 만들거나 누락을 이유로 작업을 중단하지 않는다.
- 기존 사용자 skill을 이동, 병합 또는 삭제하지 않는다.
- 설치되지 않은 외부 skill을 자동으로 설치하거나 업데이트하지 않는다.
- 한 호스트의 실패를 이유로 다른 호스트에서 성공한 설치를 되돌리지 않는다.
