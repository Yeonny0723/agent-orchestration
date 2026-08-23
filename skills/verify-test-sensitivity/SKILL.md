---
name: verify-test-sensitivity
description: TDD와 일반 검증이 끝난 뒤 새 테스트와 변경 영향 범위의 기존 테스트가 실제 행위 결함을 감지하는지 확인할 때 사용한다.
---

# 테스트 민감도 검증

이 skill은 사용자 직접 호출과 `orchestrate-work` 위임을 모두 허용한다. 자동 mutation runner가 아니라 agent가 한 mutation을 선택하고 안전 helper로 복원하는 절차다.

## 진입 조건

`implement-with-tdd` 또는 동등한 TDD 절차와 일반 검증이 완료됐는지 확인한다. 검증할 핵심 행위, 운영 코드 위치, 해당 결함을 잡아야 하는 테스트와 기준 명령을 연결한다.

## 상태 머신

1. 원본 상태에서 관련 테스트 명령을 실행해 통과를 확인한다.
2. `scripts/mutation_guard.py`로 대상 파일의 byte snapshot과 SHA-256을 기록한다.
3. `references/common.md`와 해당 언어 recipe를 읽고 컴파일 가능한 작은 mutation 하나만 운영 코드에 적용한다.
4. 연결한 테스트만 먼저 실행한다.
5. 실패하면 `killed`로 판정한다. 테스트가 결함에 민감하다는 좋은 신호다.
6. 통과하면 `survived`로 판정하고 게이트를 실패시킨다. 테스트를 보강한 뒤 같은 행위를 다시 검증한다.
7. 성공, 실패 또는 중단 여부와 무관하게 snapshot 바이트를 복원한다.
8. 복원 파일의 hash가 snapshot SHA-256과 같은지 확인한다.
9. 원본 상태의 관련 테스트와 일반 검증을 다시 실행한다.

## 범위와 안전

- 새 테스트와 변경 행위를 다루는 기존 테스트만 대상으로 한다.
- 저장소 전체 mutation, 여러 mutation 동시 적용과 테스트 코드 mutation을 주 검증으로 사용하지 않는다.
- `git checkout`, `git restore`, reset으로 복원하지 않는다. 미커밋 사용자 변경이 손실될 수 있다.
- 복원 hash가 다르거나 원본 상태 재검증이 없으면 완료로 보고하지 않는다.

결과는 `templates/test-sensitivity-evidence.md` 형식으로 현재 작업 근거에 남긴다.
