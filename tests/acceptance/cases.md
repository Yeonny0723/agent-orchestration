# 교차 호스트 인수 사례

각 사례는 Codex와 Claude Code의 새 세션에서 실행한다. worker에게 `expected.md`를 제공하지 않는다.

## 초기 living spec

"주문 취소 기능을 바꾸려 해. 현재 구조와 제약을 확인하고 기능 목표와 사용자 인터페이스에서 가능한 Use Case를 먼저 정리해 living spec 초안을 작성해 줘. 각 Use Case의 MVP 범위를 좁히고 예외·운영 위험·결정 상태를 검토하되 Task 계획은 아직 쓰지 마. 모든 결정을 확정했다고 가정하지 마."

## 반복 spec 리뷰

"작성한 spec을 다시 비판적으로 검토해 줘. 사용자 인터페이스에서 빠진 Use Case, 불필요한 범위, 부분 실패, 데이터와 비용 소유권, 현재 구조의 제약, 운영에서 뒤늦게 발견될 문제를 찾아 설명하고 같은 spec을 갱신해 줘. 중요한 비판이 더 남지 않을 때까지 반복하자."

## 큰 변경의 시각 설계와 계약

"기존 서비스에 문서 생성 기능을 추가하려 해. 먼저 기능 목표와 화면 Use Case를 정리하고, 현재 코드를 확인한 다음 Draw.io MCP로 Use Case diagram과 시스템 간 flow chart를 만들고 Spec에 PNG를 넣어 줘. 새 Browser→API→worker API schema와 DB schema/ERD를 제안하고, 핵심 도메인 객체의 관계를 class diagram으로 정리해 줘. 화면에서 확인 가능한 최소 PoC를 P0로 두고 선행 담당 팀, P1/P2 후속 작업, 완료 기준을 제안해 줘. 확정하지 못한 항목은 상태로 표시하고, 중요한 비판이 남아 있으면 Task 계획 전에 설계를 계속 다듬자."

## 작고 명확한 변경

"기존 설정의 오타 한 곳을 수정하려 해. 새 API·데이터·시스템 경계는 없어. 필요한 내용만 담은 짧은 spec을 작성하고 상세 Draw.io 그림, schema와 PoC 계획은 생략해 줘."

## 초기 spec 최종 리뷰 및 완료

"목표, Use Case, 예외와 운영 위험을 비판적으로 검토했고 범위도 좁혔어. 이제 Task 계획을 작성한 뒤 spec 전체를 최종 리뷰할 수 있게 보여줘."

## 작고 명확한 작업

"사용자 이름의 앞뒤 공백이 제거되지 않는 한 파일짜리 버그를 수정해 줘. 기대 동작은 명확해. 별도 spec이 가치가 있는지는 네가 판단해."

## Task 실행과 코드 리뷰

"living spec의 Task 2를 시작해 줘. 관련 있다고 판단한 계약과 코드를 확인하고 필요한 문서 갱신, 구현과 검증까지 진행한 뒤 커밋하지 말고 내가 리뷰할 변경을 간략히 설명해 줘."

"Task 작업이 끝나면 내가 diff를 수동 리뷰할게. 변경 요약, 테스트가 검증하는 내용, 권장 파일 리뷰 순서로 설명해 줘."

## 리뷰 수정

"Task diff를 리뷰해 보니 오류 응답 계약이 spec과 맞지 않아. 같은 Task에서 코드와 문서를 고치고 다시 검증해 줘. 아직 커밋하지 마."

## 커밋 승인

"방금 설명한 Task diff를 리뷰했고 승인해. 관련 코드, 테스트, spec과 Task 체크리스트를 같은 커밋으로 만들어 줘."

## 다음 Task 차단

"현재 Task는 아직 리뷰 중이고 커밋하지 않았지만 다음 Task도 바로 구현해 줘."

## 전문 도구 선택

### `decision-first-grill`

"첫 spec 초안에서 빠진 Use Case와 예외 흐름을 더 강하게 검토해 줘."

### `implement-with-tdd`

"현재 Task의 목표와 완료 조건은 분명해. 회귀 위험이 크니 테스트 우선으로 구현해 줘."

### `verify-test-sensitivity`

"새 테스트가 핵심 분기 결함을 실제로 잡는지 불확실해. 테스트 민감도를 확인해 줘."

## 외부 skill 부재

"superpowers, grill-with-docs와 domain-modeling이 설치되지 않은 환경에서 중요한 기능의 living spec 작성을 시작해 줘."

## 관련 없는 변경 보존

"작업 트리에 내가 수정한 다른 파일이 있어. 현재 Task만 구현하고 리뷰와 커밋 범위에서 내 변경을 제외해 줘."

## 독립 진입점

아래 사례는 전체 workflow를 다시 시작하지 않고 해당 skill만 실행한다.

### `execute-task`

"현재 living spec의 Task 3만 `execute-task`로 진행해 줘."

### `implement-with-tdd`

"현재 Task 계약을 기준으로 `implement-with-tdd`만 실행해 줘."

### `verify-test-sensitivity`

"구현과 일반 검증은 끝났어. `verify-test-sensitivity`만 실행해 줘."

### `understand-work`

"현재 living spec과 실제 diff를 바탕으로 `understand-work`를 진행해 줘."

### `write-pr`

"현재 구현에 대해 `write-pr`만 실행해 한국어 PR 초안을 작성해 줘."

## Git command

### `git:commit`

"현재 staged 변경을 논리적인 커밋으로 만들고 싶어. `git:commit`으로 계획부터 보여 줘."

### `git:issue`

"로그인 실패가 반복되는 버그 이슈를 `git:issue`로 작성해 줘."

### `git:comment`

"이슈 42에 조사 결과를 `git:comment`로 남겨 줘."

### `git:pr`

"현재 변경으로 `git:pr`를 실행해 PR 초안을 작성해 줘."

## 선택형 이해 세션

"구현과 검증을 마쳤다. 이해 세션은 호출하지 않고 PR 작성 단계로 진행해 줘."

## 문체 프로파일

### 프로파일 있음

"전역 voice profile이 있는 상태에서 spec 질문과 PR 초안을 작성해 줘."

### 프로파일 없음

"voice profile이 없는 환경에서 living spec 작성을 시작해 줘."
