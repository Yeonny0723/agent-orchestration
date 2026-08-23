---
name: capture-authoring-voice
description: spec, plan, PR과 사용자 대면 질문에 적용할 개인 문체가 아직 없거나 기존 전역 voice profile의 일부 축을 갱신할 때 사용한다.
---

# 문체 페르소나 수집

## 저장 위치

`$AGENT_ORCHESTRATION_HOME/voice-profile.md`를 사용하고 환경 변수가 없으면 `~/.agent-orchestration/voice-profile.md`를 사용한다. 문체는 저장소가 아니라 사용자에게 귀속되므로 호스트별 skill 디렉터리에 저장하지 않는다.

## 인터뷰

1. 기존 profile이 있으면 갱신할 축을 확인하고 선택하지 않은 값은 보존한다.
2. `references/voice-axes.md`의 10개 축 전체를 먼저 보여준다.
3. 한 번에 한 질문씩 묻는다. 사용자는 선택지 대신 자유 응답할 수 있다.
4. 답하지 않은 축은 `미정`으로 두며 추정으로 채우지 않는다.
5. 초안 profile을 적용한 짧은 PR 본문 예시를 만든다.
6. 사용자에게 문체가 맞는지 확인하고 어긋난 축만 다시 질문한다.
7. 사용자 승인 후에만 `templates/voice-profile.md` 구조로 저장한다.
8. 기존 파일을 덮어쓰기 전에도 변경 내용을 보여주고 승인을 받는다.

profile은 문체만 제어한다. 사실성, 검증 근거, 질문당 판단 하나와 템플릿 고정 절 같은 내용 계약은 바꾸지 않는다.
