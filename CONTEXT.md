# Agent Orchestration

현재 구조를 근거로 발전하는 spec을 만들고, 리뷰 가능한 Task 단위로 구현과 커밋을 반복하는 개발 작업 도메인이다.

## Language

**Living Spec**:
현재 코드와 사용자 리뷰에서 발견한 사실, 결정과 미결정 사항을 같은 파일에 계속 반영하는 사양. 변경 이력은 Git으로 추적한다.
_Avoid_: 버전별 초안 파일, 모든 결정을 고정한 뒤에만 작성하는 문서

**초기 Spec 검토 (Initial Spec Review)**:
현재 구조, 기능 목표, 사용자 입력 Use Case, 예외 흐름과 운영 위험을 초안에서 반복 검토해 구현 전에 설계 빈칸을 찾는 과정.
_Avoid_: 고정 질문 목록, 질문 수 제한, 한 번의 일괄 승인

**결정 상태 (Decision Status)**:
결정의 현재 성숙도를 나타내는 `검토 중`, `잠정 결정`, `확정`, `후순위` 상태. MVP 제외 여부는 별도로 관리한다.
_Avoid_: 모든 미결정을 구현 차단 사유로 취급

**Task**:
사용자가 변경 전체를 파악하고 리뷰할 수 있는 구현·검증·문서 갱신과 로컬 커밋의 단위. 크기와 분할은 현재 코드와 리뷰 부담에 따라 조정한다.
_Avoid_: 파일 수 기반 등급, 구현 세부사항을 미리 고정한 plan

**Task 리뷰 경계 (Task Review Boundary)**:
Task의 최종 diff, 변경 이유, 계약 영향과 검증 결과를 사용자가 확인한 뒤 관련 파일을 같은 커밋으로 남기는 경계.
_Avoid_: 승인 전 커밋, 현재 Task 커밋 전 다음 Task 실행, 같은 범위의 중복 승인

**전문 도구 (Specialist Tool)**:
설계 비판, TDD, 테스트 민감도와 작업 이해처럼 에이전트가 위험과 작업 성격에 따라 선택하는 독립 skill.
_Avoid_: 모든 Task에서 실행하는 고정 게이트, 설치 부재로 기본 workflow 차단

**테스트 민감도 검증 (Test Sensitivity Check)**:
회귀 위험이 큰 핵심 행위에 작은 결함을 임시로 주입해 관련 테스트가 실패하는지 확인하는 선택형 검증.
_Avoid_: 모든 Task의 의무 단계, 저장소 전체 mutation 자동화

**명시적 실행 진입점 (Explicit Invocation Entry Point)**:
사용자 또는 다른 skill이 독립적으로 호출할 수 있는 안정된 이름과 단일 책임을 가진 skill.
_Avoid_: mode 인자를 받는 만능 command, command adapter 안의 workflow 로직

**PR 작성 컨텍스트 (PR Authoring Context)**:
PR 작성을 호출한 코딩 에이전트가 직접 읽는 living spec, 실제 diff와 현재 검증 근거의 논리적 묶음. 별도 문서가 아니다.
_Avoid_: 별도 PR 지식 문서, 작업 일지, 원시 로그

**컨벤션 팩 (Convention Pack)**:
특정 언어, 프레임워크 또는 공통 코드 품질 기준을 필요할 때 선택적으로 적용하는 규칙 묶음.
_Avoid_: 전역 프롬프트, 무조건 적용되는 스타일 규칙
