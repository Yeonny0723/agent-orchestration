---
name: setup-orchestration
description: Codex와 Claude Code에서 agent-orchestration 플러그인을 처음 설치하거나 필수 외부 skill, 사용자 skill 링크, 개인 marketplace 등록 상태를 점검할 때 사용한다.
---

# 오케스트레이션 설정

## 원칙

설치는 사용자 범위에서 대화형으로 수행한다. 기존 파일이나 디렉터리를 덮어쓰지 않고, 변경 항목마다 경로와 명령을 보여준 뒤 항목별 승인을 받는다.

## 절차

1. 운영체제, 현재 호스트, 홈 디렉터리와 플러그인 원본 경로를 확인한다.
2. 사용자 범위에서 `superpowers`, `grill-with-docs`, `domain-modeling`을 각각 검사한다.
3. 누락 항목마다 설치 위치, 실행할 명령과 변경 범위를 제시하고 항목별 승인을 받는다.
4. 승인되지 않은 필수 항목은 건너뛰지 말고 설치 미완료로 보고한다.
5. 사용자 skill의 단일 원본은 `~/.agents/skills/<skill-name>`에 둔다.
6. Claude Code의 `~/.claude/skills/<skill-name>`에는 Windows에서 directory junction, Unix 계열에서 symbolic link를 만든다.
7. 대상 경로에 기대한 링크가 아닌 항목이 있으면 덮어쓰지 않고 충돌 경로와 유형을 보고한 뒤 중단한다.
8. 동일한 plugin source를 Codex와 Claude Code의 개인 marketplace에 각각 등록한다. 각 등록도 별도 승인을 받는다.
9. 이미 올바른 링크나 등록이면 성공으로 처리하고 재생성하지 않는다.
10. 성공, 실패, 충돌과 사용자가 거절한 항목을 구분해 최종 상태를 보고한다.

## 금지 사항

- 외부 skill을 축소 재구현하거나 fallback으로 대체하지 않는다.
- 기존 사용자 skill을 이동, 병합 또는 삭제하지 않는다.
- 설치 후 각 workflow 실행 때 의존성을 반복 검사하지 않는다.
- 한 호스트의 실패를 이유로 다른 호스트에서 성공한 설치를 되돌리지 않는다.
