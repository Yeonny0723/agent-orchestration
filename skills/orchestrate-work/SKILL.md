---
name: orchestrate-work
description: 기능 개발, 버그 수정, 리팩터링을 시작할 때 작업 규모를 판정하고 spec, TDD 구현, 검증, 선택형 작업 이해와 PR 작성의 올바른 순서를 선택하는 데 사용한다.
---

# 작업 오케스트레이션

## 시작

1. `references/work-scale.md`로 규모를 판정한다.
2. `references/workflow.md`를 읽고 현재 단계를 정확히 하나만 유지한다.
3. 독립 실행 skill의 책임과 입력은 `references/invocation-contracts.md`를 따른다.

## 통제 정책

1. 예상 시간이 아니라 독립적으로 병합하고 검증할 수 있는 산출물 경계로 규모를 판정한다.
2. 소형 작업은 spec 결과에 영향을 주는 모호함이 있을 때만 `decision-first-grill`을 사용하고 질문은 최대 두 개로 제한한다.
3. 중형과 대형 작업은 brainstorming에서 모든 실질적 spec 결정을 전수 목록화하고, `decision-first-grill`로 사용자에게 하나씩 확정받은 뒤 spec 승인을 요구한다.
4. plan 작성 중 공동 합의가 필요한 구현 수준의 기술 선택만 선택지, 트레이드오프와 추천안과 함께 하나씩 묻는다. 완성된 plan 전체의 사용자 리뷰는 요구하지 않는다.
5. 구현은 `implement-with-tdd`에 위임한다. 이 skill에서 TDD 세부 절차를 복제하지 않는다.
6. 일반 검증 뒤 `verify-test-sensitivity`에 위임한다.
7. `understand-work`는 사용자 명시적 호출이 있을 때만 실행하며 다른 단계를 차단하지 않는다.
8. `write-pr`도 사용자가 선택한 세션에서 명시적으로 호출할 때만 실행한다.
9. 승인 또는 필수 근거가 없는 단계에서는 멈추고 부족한 내용을 보고한다.

## plan 작성

계획 기술 합의가 끝나면 `author-reviewable-text`에 산출물 종류가 plan임을 밝히고 plan 형식과 필수 형식, 승인된 spec과 확정된 기술 결정인 확인된 사실, 해당되는 길이 제한을 전달한다. 확정된 기술 결정만 전달하며 일반적인 기술 선택을 추가하거나 대안이나 새로운 선택지를 다시 열지 않는다. 반환된 최종 plan을 저장하되 plan 전체를 사용자 승인 게이트로 만들지는 않는다.
