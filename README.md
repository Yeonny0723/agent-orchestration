# Agent Orchestration

Codex와 Claude Code에서 개발 작업을 일관된 방식으로 진행하기 위한 agent orchestration 플러그인입니다.
작업 규모에 따라 기획 깊이를 조절하고, 사용자와 기술적 의사결정을 확정한 뒤 구현·검증·PR 작성을 연결합니다.

## 해결하는 문제

AI가 생성한 코드의 품질만이 아니라 다음 내용을 작업 과정에서 명확하게 남기고 확인하는 것을 목표로 합니다.

- 작업의 규모와 필요한 워크플로우
- spec에 들어갈 의사결정과 선택 이유
- 구현 중 사용자와 합의해야 하는 기술적 선택
- TDD와 일반 검증 결과
- 테스트가 실제 변경 행위를 감지하는지에 대한 민감도 근거
- 사용자가 현재 변경을 설명하고 문제 발생 시 수정 위치를 판단할 수 있는지
- 실제 spec, diff와 검증 근거에 기반한 PR/MR 설명
- 사람의 문체와 사용자의 문체로 리뷰를 맡겨 검토 과정을 빠르게 진행하는 것

## 기본 워크플로우

```text
작업 규모 판정
  -> 문제·구조·제약 탐색
  -> spec 작성에 필요한 의사결정 확정
  -> spec 작성 및 사용자 승인
  -> plan 작성 중 기술적 합의
  -> TDD 기반 구현
  -> 테스트 민감도 검증
  -> 선택형 작업 이해 세션
  -> PR/MR 작성
```

## 주요 진입점

### 자동 오케스트레이션

`orchestrate-work` skill을 호출하면 작업 규모에 따라 필요한 단계를 선택합니다.

| 규모 | 판정 기준 | 기본 접근 |
| --- | --- | --- |
| 소형 | 명확한 버그 또는 한두 파일 변경 | 모호함이 없으면 짧게 진행 |
| 중형 | 여러 파일·모듈에 걸친 하나의 기능 | spec 결정을 모두 확정 |
| 대형 | 독립 배포 가능한 모듈 또는 둘 이상의 PR | 산출물별 plan과 PR로 분리 |

예상 시간이나 파일 수만으로 판정하지 않습니다. 공개 계약, 데이터 소유권, 운영 경계 또는 독립 검증 단위가 나뉘면 더 큰 규모로 올립니다.

### 문체 처리

사용자 검토 대상 글은 `author-reviewable-text`를 통해 작성하며, `capture-authoring-voice`의 사용자 문체와 설치된 선택형 `stop-slop`·`humanizer`를 반영합니다.

## 디렉터리 구조

```text
.
├── .claude-plugin/       # Claude Code plugin manifest
├── .codex-plugin/        # Codex plugin manifest
├── commands/             # Git 관련 얇은 command adapter
├── conventions/          # 공통·React·Python·TypeScript convention pack
├── docs/                 # 확정된 spec과 plan
├── scripts/              # 설치, mutation 복원, plugin 검증 도구
├── skills/               # Codex·Claude Code 공용 skill
│   ├── apply-conventions/       # 언어·프레임워크별 convention pack 선택 및 적용
│   ├── author-reviewable-text/  # 사용자 검토 대상 글의 최종 초안 작성
│   ├── capture-authoring-voice/ # 사용자 문체 프로파일 수집 및 저장
│   ├── commit-changes/          # 원자적 커밋 계획과 커밋 메시지 작성
│   ├── decision-first-grill/    # spec 작성에 필요한 의사결정 확정
│   ├── implement-with-tdd/      # 테스트 우선 구현과 검증
│   ├── orchestrate-work/        # 작업 규모에 따른 개발 워크플로우 조합
│   ├── post-git-comment/        # Git Issue·PR·MR 코멘트 작성 및 게시
│   ├── review-comment/          # 새 GitHub PR·GitLab MR 리뷰 코멘트 반영
│   ├── setup-orchestration/     # 플러그인과 외부 skill 의존성 설치
│   ├── understand-work/         # 현재 변경을 이해하기 위한 질문 진행
│   ├── verify-test-sensitivity/ # 테스트의 변경 감지 여부 검증
│   ├── write-issue/             # GitHub·GitLab Issue 작성 및 게시
│   └── write-pr/                # GitHub·GitLab PR·MR 작성 및 게시
├── templates/            # spec, plan, 검증 근거 등의 문서 템플릿
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

다른 브랜치를 설치하려면 Claude Code는 Git URL 뒤의 `#<branch>`를, Codex는 `--ref <branch>`를 같은 브랜치 이름으로 바꿉니다. 예를 들어 `feature/review-comment` 브랜치는 각각 `...git#feature/review-comment`, `--ref feature/review-comment`로 지정합니다.

업데이트:

```powershell
claude plugin marketplace update agent-orchestration-marketplace
claude plugin update agent-orchestration@agent-orchestration-marketplace --scope user

codex plugin marketplace upgrade agent-orchestration-marketplace
codex plugin add agent-orchestration@agent-orchestration-marketplace
```

Codex에서는 `codex plugin marketplace upgrade` 후 `codex plugin add`가 plugin을 다시 등록·설치합니다.

업데이트한 skill을 적용하려면 Codex 새 스레드 또는 Claude Code 재시작이 필요할 수 있습니다.

의존성:

- `superpowers`
- `grill-with-docs`
- `domain-modeling`
- 선택형 `stop-slop`
- 선택형 `humanizer`
