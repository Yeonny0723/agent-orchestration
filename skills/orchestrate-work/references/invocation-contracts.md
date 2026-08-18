# 독립 실행 진입점 계약

`git-commit`, `git-issue`, `git-comment`, `git-pr` command는 아래 대응 skill 하나에만 1:1로 위임하며 인자 전달 외의 업무 로직을 포함하지 않는다. provider 감지, Git 실행, 상태 전이, 검증과 문서 작성은 skill이 담당한다. mode 인자로 여러 기능을 분기하는 단일 command를 만들지 않는다.

## `implement-with-tdd`

- 책임: 승인된 작업 기준에 따라 테스트 우선 구현과 일반 검증을 수행한다.
- 입력: 승인된 spec, 해당되는 plan과 계획 기술 합의, 저장소 지침.
- 종료: 실제 diff, 일반 검증 명령과 결과, `verify-test-sensitivity` 안내.
- 호출: 사용자 직접 호출 또는 `orchestrate-work` 위임.

## `verify-test-sensitivity`

- 책임: 작은 행위 결함을 관련 테스트가 감지하는지 확인하고 정확히 복원한다.
- 입력: TDD 완료 근거, 현재 diff, 관련 테스트 명령.
- 종료: killed/survived 판정, 복원 hash, 원본 상태 검증 결과.
- 호출: 사용자 직접 호출 또는 `orchestrate-work` 위임.

## `understand-work`

- 책임: 실제 변경에 대한 사용자 이해를 최대 5문항으로 확인하고 넓힌다.
- 입력: 승인된 spec, 실제 diff, 연결된 이슈, ADR과 관련 문서.
- 종료: 현재 대화의 문항별 피드백과 이해 영역 요약.
- 호출: 사용자 명시적 직접 호출만 허용하며 다른 절차를 차단하지 않는다.

## `commit-changes`

- 책임: 현재 변경을 원자적 Conventional Commit 계획으로 제시하고 승인 후 로컬 commit을 생성한다.
- 입력: 현재 Git 상태, staged·unstaged diff, 사용자 메시지 또는 커밋 분할 요청.
- 종료: 승인된 commit hash와 제목 또는 승인 전 계획·중단 사유.
- 호출: 사용자 직접 호출 또는 `git-commit` command 위임.

## `write-issue`

- 책임: provider를 감지해 자체 완결적인 이슈 초안을 작성하고 승인 후 생성한다.
- 입력: 제목, 유형, labels, 현재 대화와 승인된 작업 문서.
- 종료: 이슈 URL·번호 또는 보존된 초안과 중단 사유.
- 호출: 사용자 직접 호출 또는 `git-issue` command 위임.

## `post-git-comment`

- 책임: 이슈 또는 PR·MR 코멘트 초안을 작성하고 승인 후 게시한다.
- 입력: 대상 번호, 대상 유형, 사용자 제공 본문 또는 현재 대화 맥락.
- 종료: 게시 URL·식별자 또는 보존된 초안과 중단 사유.
- 호출: 사용자 직접 호출 또는 `git-comment` command 위임.

## `write-pr`

- 책임: 현재 근거를 재검증하고 한국어 PR 초안을 작성하며 승인 후 PR을 생성한다.
- 입력: 승인된 spec, 실제 diff, 현재 실행 가능한 검증 명령.
- 종료: 사용자 승인된 PR 또는 부족한 근거 보고.
- 호출: 사용자가 선택한 코딩 에이전트 세션의 직접 호출만 허용한다.
