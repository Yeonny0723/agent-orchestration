---
name: author-reviewable-text
description: 사용자가 승인하거나 외부에 게시할 spec, plan, Issue, comment, PR, MR 또는 선택형 질문의 최종 초안을 작성할 때 사용한다.
---

# 검토 대상 글 작성

## 입력 계약

호출자는 다음 입력을 제공한다.

- 산출물 종류와 목적, 독자
- 확인된 사실과 아직 확인되지 않은 사항
- 반드시 지켜야 할 필수 형식
- 필요하면 선택형 질문의 선택지와 판단 기준
- 선택 사항인 `$AGENT_ORCHESTRATION_HOME/voice-profile.md` 또는 `~/.agent-orchestration/voice-profile.md`

확인되지 않은 내용을 추정해 사실로 만들지 않는다. 필수 입력이 모호하면 초안을 쓰기 전에 호출자에게 부족한 근거를 요청한다.

## 적용 범위

spec, plan, Issue, comment, PR, MR과 `understand-work` 질문처럼 사용자가 검토하거나 승인할 글에 적용한다. 선택형 질문은 선택지, 차이와 판단 기준을 보존한다.

commit message, 일반 진행 상황, code, tests, logs, commands, implementation report와 `understand-work` feedback에는 적용하지 않는다.

## 우선순위

충돌할 때는 다음 순서를 지킨다.

1. 사용자의 명시적 지시
2. 산출물의 필수 형식
3. 확인된 사실
4. 선택 사항인 voice profile
5. `humanizer`
6. `stop-slop`
7. 기본 한국어 문체

voice profile은 문체만 바꾸며 앞선 세 항목을 바꾸지 않는다. profile이 없거나 읽기 오류가 나도 작성을 차단하지 않는다.

## 작성 절차

1. 입력에서 사실, 미확인 사항, 형식과 문체 제약을 분리한다.
2. 설치된 skill 목록을 확인하고 `humanizer`가 설치된 경우에만 작업 중인 문안을 다듬는다.
3. `stop-slop`이 설치된 경우에만 그 결과의 군더더기를 줄인다.
4. 두 선택형 skill이 없거나 호출 중 오류가 나면 해당 단계를 건너뛰며 전체 작성을 차단하지 않는다. 대체 skill을 찾거나 설치하지 않는다.
5. 우선순위에 다시 대조한 뒤 사용자에게 최종 초안을 한 번만 제시한다.

`humanizer`와 `stop-slop`에는 앞선 우선순위를 위반하거나 사실과 필수 형식을 바꿀 권한이 없다. 최종 검토에서 사실이나 형식의 오류가 발견되면 전체 초안을 다시 생성하지 않고 영향받은 사실 또는 형식만 수리한다.

## 결과

기본값은 간결하고 자연스러운 한국어다. 초안과 함께 여러 대안이나 작성 과정을 덧붙이지 않는다. 미확인 사항은 산출물 형식이 허용하는 방식으로 명시하며, 확인된 사실처럼 단정하지 않는다.
