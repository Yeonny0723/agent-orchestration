# 교차 호스트 인수 사례

각 사례는 Codex와 Claude Code의 새 세션에서 실행한다. worker에게 `expected.md`를 제공하지 않는다.

## 초기 living spec

"주문 취소 기능을 바꾸려 해. 현재 저장소 구조를 먼저 확인하고 기능 목표, 사용자 입력 Use Case, 예외 흐름, 결정 상태와 Task 체크리스트가 포함된 첫 living spec 초안을 작성해 줘. 아직 모든 결정을 확정했다고 가정하지 마."

## 반복 spec 리뷰

"작성한 spec을 다시 비판적으로 검토해 줘. 사용자가 입력할 수 있는 경우, 부분 실패, 데이터 소유권과 운영 중 뒤늦게 발견될 문제를 찾아 질문하고 같은 spec을 갱신해 줘."

## 초기 spec 기준 커밋

"spec 전체를 검토했고 현재 발견한 Use Case는 MVP 포함, 후순위 또는 제외로 정리됐어. 이 spec과 Task 체크리스트를 기준본으로 커밋해 줘."

## 작고 명확한 작업

"사용자 이름의 앞뒤 공백이 제거되지 않는 한 파일짜리 버그를 수정해 줘. 기대 동작은 명확해. 별도 spec이 가치가 있는지는 네가 판단해."

## Task 실행과 코드 리뷰

"living spec의 Task 2를 시작해 줘. 관련 있다고 판단한 계약과 코드를 확인하고 필요한 문서 갱신, 구현과 검증까지 진행한 뒤 커밋하지 말고 내가 리뷰할 변경을 간략히 설명해 줘."

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
