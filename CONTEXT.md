# Agent Orchestration

개발 작업의 규모, 의사결정, 검증, 작업 이해, PR 작성을 여러 코딩 에이전트에서 일관되게 운영하기 위한 도메인이다.

## Language

**작업 규모 (Work Scale)**:
작업에 필요한 독립 산출물과 변경 범위를 기준으로 분류한 소형, 중형, 대형 등급.
_Avoid_: 난이도, 작업 시간

**의사결정 우선 그릴 (Decision-First Grill)**:
spec 작성에 필요한 실질적 의사결정을 전수 식별하고, 선택지와 트레이드오프를 드러내어 사용자의 결정을 하나씩 확정하는 대화형 게이트.
_Avoid_: spec 리뷰, 계획 리뷰, 일반 질의응답

**구현 기준 문서 (Implementation Baseline)**:
사용자가 승인하여 이후 계획과 구현이 따라야 하는 확정된 spec.
_Avoid_: 작업 로그, 초안, 메모

**계획 기술 합의 (Planning Technical Alignment)**:
plan을 작성하면서 공동 합의가 필요한 구현 수준의 기술 선택을 식별하고, 선택지와 트레이드오프를 제시해 사용자의 결정을 하나씩 확정하는 대화형 절차. 완성된 plan 자체는 사용자 리뷰 대상이 아니다.
_Avoid_: spec 결정 재논의, plan 전체 리뷰, 사소한 구현 세부사항 질문

**테스트 민감도 검증 (Test Sensitivity Check)**:
의도한 동작에 작은 결함을 임시로 주입했을 때 관련 테스트가 실패하는지 확인하는 검증.
_Avoid_: mutation testing 전체 자동화, 테스트 실행

**작업 이해 세션 (Work Understanding Session)**:
사용자가 명시적으로 호출하면 spec, 실제 diff, 이슈, ADR과 관련 문서에서 최대 5개의 상황형 질문을 만들어 사용자의 변경 이해를 확인하고 넓히는 대화형 세션.
_Avoid_: 조직용 산출물 등록, blocking gate, 점수형 시험, 영구 학습 기록

**명시적 실행 진입점 (Explicit Invocation Entry Point)**:
사용자 또는 전체 워크플로우가 독립적으로 호출할 수 있는 안정된 이름과 단일 책임을 가진 skill. 향후 호스트별 command는 이 진입점에 1:1로 위임한다.
_Avoid_: mode 인자를 받는 단일 만능 command, command adapter 안의 워크플로우 로직

**PR 작성 컨텍스트 (PR Authoring Context)**:
사용자가 PR 작성을 호출한 세션의 코딩 에이전트가 직접 읽는 승인된 spec, 실제 diff, 최종 검증 근거의 논리적 묶음. 별도 문서가 아니다.
_Avoid_: 별도 PR 작성 문서, 작업 일지, 원시 로그

**컨벤션 팩 (Convention Pack)**:
특정 언어, 프레임워크 또는 공통 코드 품질 기준을 필요할 때 선택적으로 적용하는 규칙 묶음.
_Avoid_: 전역 프롬프트, 무조건 적용되는 스타일 규칙
