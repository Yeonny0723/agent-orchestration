---
name: implement-with-tdd
description: 승인된 spec과 해당 plan이 준비된 기능 개발, 버그 수정 또는 리팩터링을 테스트 우선으로 구현하고 일반 검증까지 수행할 때 사용한다.
---

# TDD 기반 구현

이 skill은 사용자 직접 호출과 `orchestrate-work`의 위임을 모두 허용한다. 두 호출 경로는 같은 절차를 사용한다.

## 진입 조건

1. 승인된 spec과 저장소 지침을 확인한다.
2. plan이 필요한 규모라면 계획 기술 합의가 모두 끝났는지 확인한다.
3. 적용할 convention pack을 확인한다.
4. spec 수준 결정이 없거나 미확정이면 구현하지 않고 `orchestrate-work` 또는 spec 수정 단계로 돌려보낸다.

## 실행

1. 외부 `superpowers:test-driven-development`를 호출한다.
2. 한 행위를 설명하는 실패 테스트를 먼저 작성한다.
3. 테스트를 실행해 구현 부재 또는 결함 때문에 실패하는지 확인한다.
4. 통과에 필요한 최소 구현을 작성한다.
5. 관련 테스트를 통과시킨 뒤 중복과 이름을 정리한다.
6. 변경 영향 범위의 일반 검증을 실행한다.
7. 실제 변경 범위, 검증 명령과 결과를 현재 세션에 보고한다.
8. 다음 독립 단계로 `verify-test-sensitivity`를 안내한다.

## 책임 경계

규모 판정, spec 의사결정, 테스트 mutation, 작업 이해 질문, PR 작성 또는 PR 생성 절차를 이 skill에 복제하지 않는다.

## 문체

사용자 대면 질문과 결과는 `$AGENT_ORCHESTRATION_HOME/voice-profile.md` 또는 `~/.agent-orchestration/voice-profile.md`를 문체에만 적용한다. 프로파일이 없어도 차단하지 않는다.
