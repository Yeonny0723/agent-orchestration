# Agent Orchestration

Codex와 Claude Code에서 living spec과 작은 Task 단위의 리뷰·커밋 루프로 개발 작업을 진행하는 플러그인입니다.

## 해결하는 문제

- 현재 구조와 사용자 입력 Use Case를 근거로 첫 spec 초안을 만든다.
- 사용자의 반복 리뷰로 설계 빈칸, 예외와 운영 위험을 앞당겨 찾는다.
- 결정 상태와 MVP 제외 범위를 하나의 living spec에서 관리한다.
- Task마다 필요한 문서 갱신, 구현과 검증을 묶어 리뷰 가능한 diff를 만든다.
- 승인된 Task만 관련 코드, 테스트와 문서를 같은 커밋에 포함한다.
- TDD, 테스트 민감도, 작업 이해와 Git 도구는 필요할 때 독립적으로 사용한다.

## 기본 워크플로우

```text
현재 구조 조사와 첫 living spec 초안
  -> 사용자와 반복 spec 리뷰
  -> 초기 spec과 Task 체크리스트 기준 커밋
  -> 지정한 Task 구현·검증
  -> 사용자 코드 리뷰
  -> 승인 범위 커밋
  -> 다음 Task
```

질문 수, Task 크기, 별도 plan, 구현 방식과 검증 깊이는 현재 작업에 맞춰 코딩 에이전트가 판단합니다. 작고 명확한 작업은 별도 spec이나 plan을 생략할 수 있으며 코드 리뷰와 커밋 경계는 유지합니다.

## 주요 진입점

### `orchestrate-work`

중요한 작업을 시작할 때 현재 코드와 문서를 조사하고 첫 living spec과 Task 체크리스트를 만듭니다. 사용자는 초안을 여러 번 리뷰할 수 있으며 에이전트는 같은 문서를 갱신합니다.

### `execute-task`

사용자가 지정한 Task의 관련 계약을 확인하고 필요한 spec·plan 갱신, 구현과 검증을 수행합니다. 최종 diff를 설명해 사용자 리뷰를 받고, 승인 범위가 분명하면 관련 파일만 같은 커밋에 포함합니다. 현재 Task가 커밋되기 전에는 다음 Task를 시작하지 않습니다.

### 선택형 전문 도구

- `decision-first-grill`: living spec의 빠진 Use Case, 예외와 운영 위험을 비판적으로 검토
- `implement-with-tdd`: 현재 Task를 테스트 우선으로 구현
- `verify-test-sensitivity`: 회귀 위험이 큰 행위에서 테스트의 결함 감지력을 확인
- `understand-work`: 사용자가 원할 때 현재 변경에 대한 이해를 확장
- `commit-changes`, `write-issue`, `post-git-comment`, `write-pr`: 필요한 Git 작업을 독립적으로 수행

사용자 검토 대상 글은 `author-reviewable-text`를 통해 작성하며, 사용자 문체와 설치된 `stop-slop`·`humanizer`를 선택적으로 반영합니다.

## 디렉터리 구조

```text
.
├── .claude-plugin/       # Claude Code plugin manifest
├── .codex-plugin/        # Codex plugin manifest
├── commands/             # Git 관련 얇은 command adapter
├── conventions/          # 공통·React·Python·TypeScript convention pack
├── docs/                 # living spec과 필요한 plan
├── scripts/              # 설치, mutation 복원, plugin 검증 도구
├── skills/               # Codex·Claude Code 공용 skill
│   ├── apply-conventions/       # 언어·프레임워크별 convention 적용
│   ├── author-reviewable-text/  # 사용자 검토 대상 글 작성
│   ├── commit-changes/          # 원자적 로컬 커밋
│   ├── decision-first-grill/    # living spec 비판적 검토
│   ├── execute-task/            # 지정 Task 구현, 리뷰와 커밋 연결
│   ├── implement-with-tdd/      # 선택형 테스트 우선 구현
│   ├── orchestrate-work/        # living spec과 Task 계획 작성
│   ├── setup-orchestration/     # 플러그인과 선택형 skill 설정
│   ├── verify-test-sensitivity/ # 선택형 테스트 민감도 검증
│   └── ...                      # 작업 이해와 Git 작성 도구
├── templates/            # spec과 검증 근거 템플릿
└── tests/                # 계약·인수·스크립트 테스트
```

## 설치와 선택형 의존성

저장소 경로를 각 호스트의 marketplace로 등록한 뒤 플러그인을 설치합니다.

Claude Code:

```powershell
claude plugin marketplace add "C:\Users\<사용자>\orca\projects\agent-orchestration" --scope user
claude plugin install agent-orchestration@agent-orchestration-marketplace --scope user
```

Codex:

```powershell
codex plugin marketplace add "C:\Users\<사용자>\orca\projects\agent-orchestration"
codex plugin add agent-orchestration@agent-orchestration-marketplace
```

원격 marketplace의 최신 변경사항을 반영하려면:

```powershell
codex plugin marketplace upgrade agent-orchestration-marketplace
```

다음 외부 skill은 설치돼 있으면 활용할 수 있으며 없어도 기본 workflow를 사용할 수 있습니다.

- `superpowers`
- `grill-with-docs`
- `domain-modeling`
- `stop-slop`
- `humanizer`
