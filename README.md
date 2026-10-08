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
현재 구조와 제약 조사
  -> 기능 목표와 사용자 Use Case 초안
  -> 예외·운영 위험 검토 및 불필요한 범위 축소
  -> 사용자 비판을 반영해 반복 갱신
  -> Task 계획 작성
  -> spec 전체 최종 리뷰와 완료 승인
  -> 승인된 spec 기준 커밋
  -> 지정한 Task 구현·검증
  -> 사용자 코드 리뷰
  -> 승인 범위 커밋
  -> 다음 Task
```

기능 목표와 사용자 Use Case를 먼저 다루고 설계 검토와 범위 축소가 끝난 다음 Task 계획을 작성합니다. 큰 변경은 Draw.io 다이어그램, API·DB schema, 필요 시 class diagram과 PoC 중심 우선순위를 Spec에 포함합니다. 중요한 비판이나 설계 빈칸이 남으면 사용자와 같은 spec 및 그림을 계속 갱신합니다. 결정 상태는 `검토 중`, `잠정 결정`, `확정`, `후순위`로 표시할 수 있으며 모든 미결정을 억지로 확정하지 않습니다. 작고 명확한 변경에는 상세 그림과 schema를 요구하지 않습니다.

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
│   ├── capture-authoring-voice/ # 사용자 문체 프로파일 수집
│   ├── commit-changes/          # 원자적 로컬 커밋
│   ├── decision-first-grill/    # living spec 비판적 검토
│   ├── execute-task/            # 지정 Task 구현, 리뷰와 커밋 연결
│   ├── implement-with-tdd/      # 선택형 테스트 우선 구현
│   ├── orchestrate-work/        # living spec과 Task 계획 작성
│   ├── post-git-comment/        # Git Issue·PR·MR 코멘트 작성
│   ├── review-comment/          # 새 PR·MR 리뷰 코멘트 반영
│   ├── setup-orchestration/     # 플러그인과 선택형 skill 설정
│   ├── understand-work/         # 현재 변경 이해 확장
│   ├── verify-test-sensitivity/ # 선택형 테스트 민감도 검증
│   ├── write-issue/             # GitHub·GitLab Issue 작성
│   └── write-pr/                # GitHub·GitLab PR·MR 작성
├── templates/            # spec과 검증 근거 템플릿
└── tests/                # 계약·인수·스크립트 테스트
```

## 설치와 업데이트

공개 GitHub marketplace에서 설치하므로 사용자는 이 저장소를 clone하거나 pull할 필요가 없습니다. 기본 배포 브랜치는 `master`이며, 다른 브랜치를 시험할 때는 설치 명령의 branch 값을 바꿉니다.

Claude Code:

```powershell
claude plugin marketplace add "https://github.com/Yeonny0723/agent-orchestration.git#master" --scope user
claude plugin install agent-orchestration@agent-orchestration-marketplace --scope user
```

Codex:

```powershell
codex plugin marketplace add Yeonny0723/agent-orchestration --ref master
codex plugin add agent-orchestration@agent-orchestration-marketplace
```

다른 브랜치를 설치하려면 Claude Code는 Git URL 뒤의 `#<branch>`를, Codex는 `--ref <branch>`를 같은 브랜치 이름으로 바꿉니다.

업데이트:

```powershell
claude plugin marketplace update agent-orchestration-marketplace
claude plugin update agent-orchestration@agent-orchestration-marketplace --scope user

codex plugin marketplace upgrade agent-orchestration-marketplace
codex plugin add agent-orchestration@agent-orchestration-marketplace
```

Codex에서는 `codex plugin marketplace upgrade` 후 `codex plugin add`가 plugin을 다시 등록·설치합니다. 업데이트한 skill을 적용하려면 Codex 새 스레드 또는 Claude Code 재시작이 필요할 수 있습니다.

다음 외부 skill은 설치돼 있으면 활용할 수 있으며 없어도 기본 workflow를 사용할 수 있습니다.

- `superpowers`
- `grill-with-docs`
- `domain-modeling`
- `stop-slop`
- `humanizer`
