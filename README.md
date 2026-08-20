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

### 사용자 승인 경계

- spec은 필요한 의사결정을 모두 확정한 뒤 작성하며, 작성 후 사용자가 승인해야 plan으로 진행합니다.
- plan 자체는 사용자가 리뷰하지 않습니다. plan을 작성하면서 구현 수준의 합의가 필요한 내용만 질문합니다.
- TDD 구현과 테스트 민감도 검증은 독립적으로 직접 호출할 수 있습니다.
- 작업 이해 세션은 사용자가 명시적으로 호출할 때만 실행하며, 최대 5개의 질문으로 현재 변경에 대한 이해를 확인합니다. PR을 차단하는 게이트는 아닙니다.
- PR/MR 작성도 사용자가 원하는 Codex, Claude Code 또는 호환 agent 세션에서 명시적으로 호출합니다.

## 주요 진입점

### 자동 오케스트레이션

`orchestrate-work` skill을 호출하면 작업 규모에 따라 필요한 단계를 선택합니다.

| 규모 | 판정 기준 | 기본 접근 |
| --- | --- | --- |
| 소형 | 명확한 버그 또는 한두 파일 변경 | 모호함이 없으면 짧게 진행 |
| 중형 | 여러 파일·모듈에 걸친 하나의 기능 | spec 결정을 모두 확정 |
| 대형 | 독립 배포 가능한 모듈 또는 둘 이상의 PR | 산출물별 plan과 PR로 분리 |

예상 시간이나 파일 수만으로 판정하지 않습니다. 공개 계약, 데이터 소유권, 운영 경계 또는 독립 검증 단위가 나뉘면 더 큰 규모로 올립니다.

### 독립 호출 skill

- `decision-first-grill`: spec 작성에 필요한 결정을 하나씩 확정
- `implement-with-tdd`: 승인된 spec과 plan을 기준으로 테스트 우선 구현
- `verify-test-sensitivity`: 작은 행위 결함을 주입해 관련 테스트의 감지 여부 확인
- `understand-work`: 실제 spec과 diff를 바탕으로 최대 5개의 이해 질문 진행
- `write-pr`: 실제 diff와 최종 검증 근거를 재확인해 한국어 PR/MR 초안 작성
- `apply-conventions`: 언어·프레임워크별 convention pack 선택 및 적용
- `setup-orchestration`: Codex·Claude Code와 외부 skill 의존성 설치 상태 점검

## Git 커맨드

Git 관련 기능은 얇은 command가 대응 skill에 1:1로 위임합니다.

| 커맨드 | 위임 skill | 동작 |
| --- | --- | --- |
| `/git-commit` | `commit-changes` | 원자적 커밋 계획을 제시하고 승인 후 로컬 커밋 |
| `/git-issue` | `write-issue` | GitHub Issue 또는 GitLab Issue 초안 작성 및 승인 후 생성 |
| `/git-comment` | `post-git-comment` | Issue·PR·MR 코멘트 초안 작성 및 승인 후 게시 |
| `/git-pr` | `write-pr` | spec·diff·검증 근거 기반 PR/MR 작성 및 승인 후 생성 |

provider는 `origin` remote와 CLI 상태를 기준으로 GitHub 또는 GitLab을 자동 감지합니다. 감지할 수 없거나 모호하면 외부 쓰기를 실행하지 않습니다. push, commit, issue/comment/PR 생성은 초안과 실행 명령을 보여준 뒤 승인받아 수행합니다.

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
├── templates/            # spec, plan, 검증 근거 등의 문서 템플릿
└── tests/                # 계약·인수·스크립트 테스트
```

## 설치와 의존성

플러그인 원본을 Codex와 Claude Code에서 사용자 전역 plugin으로 설치하려면 저장소 경로를 각 호스트의 marketplace로 등록한 뒤 plugin을 설치합니다. 이 저장소는 현재 root 자체를 plugin source로 가리키는 marketplace manifest를 제공합니다.

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

설치 후 새 Claude Code 또는 Codex thread를 시작합니다. 업데이트할 때는 marketplace source의 변경사항을 갱신한 뒤 각 호스트의 plugin update/install 명령을 사용합니다. 외부 skill 의존성까지 점검하려면 `setup-orchestration` skill을 별도로 호출합니다.

설치 과정은 다음 외부 skill을 확인하고, 사용자 범위의 충돌을 덮어쓰지 않습니다.

- `superpowers`
- `grill-with-docs`
- `domain-modeling`

사용자 convention은 필요할 때만 선택해 적용합니다. Python과 TypeScript 규칙은 각각 `conventions/python/`, `conventions/typescript/`에 있으며 React 규칙은 `conventions/react.md`에 있습니다.

## 검증

저장소 루트에서 실행합니다.

```powershell
python -m unittest discover -s tests -v
python scripts/validate_plugin.py .
```

첫 번째 명령은 계약·인수·스크립트 테스트를 실행하고, 두 번째 명령은 양쪽 manifest, skill metadata, command 위임과 참조 파일의 구조를 검사합니다.

## 범위 원칙

- PR 지식 패킷이나 별도 작업 로그를 만들지 않습니다. PR 작성 agent가 승인된 spec, 실제 diff와 최종 검증 근거를 직접 읽습니다.
- 작업 이해 세션의 답변은 조직용 산출물이나 영구 학습 기록으로 저장하지 않습니다.
- command에 워크플로우 로직을 넣지 않습니다. provider 감지와 상태 전이는 대응 skill이 담당합니다.
- TDD 구현, 테스트 민감도 검증, 작업 이해 세션과 PR 작성은 필요할 때 사용자가 독립적으로 호출할 수 있습니다.
