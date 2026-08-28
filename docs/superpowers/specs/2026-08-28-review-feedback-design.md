# 리뷰 코멘트 반영 skill

## 문제

PR/MR 리뷰어가 남긴 새 코멘트를 현재 Codex 또는 Claude 세션에서 직접 확인하고 코드에 반영하려면, 매번 링크와 코멘트를 수동으로 복사하거나 별도 자동화 서비스를 사용해야 한다. 기존 Git command는 provider CLI 의존성을 유지하면서, 사용자가 명시적으로 호출할 때만 리뷰 피드백을 처리하는 공용 진입점이 필요하다.

## 목적

Codex와 Claude Code에서 공통으로 호출할 수 있는 `review-comment` skill을 제공한다. 첫 호출에서 PR/MR 링크를 받아 세션의 대상 컨텍스트로 유지하고, 이후 호출마다 해당 대상의 새 리뷰 코멘트를 읽어 수정·검증·commit·push까지 수행한다.

처리된 코멘트에는 완료 응답과 commit SHA를 남기고, provider가 지원하면 review thread 또는 discussion을 resolve한다.

## 현재 구조와 제약

- 공용 skill은 `skills/<name>/SKILL.md`와 Codex UI metadata인 `agents/openai.yaml`로 구성된다.
- Codex와 Claude Code가 같은 `skills/` 진입점을 사용한다.
- 기존 `git:commit`, `git:pr`, `git:comment`, `git:issue` command와 skill은 변경하지 않는다.
- 기존 Git command의 `gh`/`glab` 설치·인증 요구사항을 완화하지 않는다. CLI 자동 설치나 임의의 token/API fallback은 추가하지 않는다.
- 현재 환경에는 `glab`이 설치되어 있고 사내 GitLab host 인증이 설정되어 있다. `gitlab.com` API 인증은 실패한다. `gh`는 설치되어 있지 않다.
- 현재 Codex 세션에는 GitHub connector 도구가 노출되어 있으므로 GitHub 작업은 connector를 우선 사용할 수 있다. GitLab connector는 현재 노출되어 있지 않으므로 `glab`을 사용한다.

## 결정

### 공용 명시적 진입점

새 skill 이름은 `review-comment`로 정한다. 사용자가 skill을 호출할 때만 실행하며, 임의의 일반 메시지나 백그라운드 polling으로 실행하지 않는다.

### 세션 대상

첫 호출에 대상 PR/MR 링크가 없으면 링크만 요청한다. 링크를 받으면 provider, repository/project, PR/MR 번호를 현재 대화 세션의 대상 컨텍스트로 유지한다. 이후 호출에는 링크를 다시 요구하지 않는다. 다른 링크가 명시되면 대상 컨텍스트를 교체한다.

### provider 접근 순서

현재 호스트에서 사용할 수 있는 provider connector/API 도구를 우선 사용한다. 해당 도구가 없으면 provider CLI를 사용한다.

- GitHub: Codex connector 우선, 그 외 `gh`
- GitLab: connector 우선, 그 외 `glab`

필요한 도구가 없거나 인증·권한 검사가 실패하면 수정·commit·push를 수행하지 않고 원인과 필요한 조치만 보고한다. 도구를 설치하거나 인증을 자동으로 변경하지 않는다.

### 코멘트 처리

각 호출에서 대상 PR/MR의 새 unresolved 리뷰 코멘트와 discussion을 조회한다. 사람이 작성한 실행 가능한 코드 변경 요청만 처리하고, 봇의 완료 응답·중복 코멘트·단순 질의는 다시 수정 대상으로 삼지 않는다.

코멘트의 파일·라인·본문과 PR/MR diff 및 repository guidance를 함께 사용해 수정한다. 수정 후 관련 테스트 또는 프로젝트 검증 명령을 실행한다.

### commit/push와 완료 표시

검증을 통과하면 이번 실행에서 변경된 파일만 stage하여 자동 commit하고 대상 PR/MR source branch에 push한다. `git add -A`나 사용자의 기존 변경을 포함하는 broad staging은 사용하지 않는다.

성공한 코멘트에는 `✅ 반영 완료`와 commit SHA를 포함한 답글을 남기고, provider가 지원하면 해당 review thread/discussion을 resolve한다. 수정·검증·push 중 하나라도 실패하면 코멘트를 resolve하지 않고 실패 원인을 답글 또는 세션 보고로 남긴다.

## 비목표

- PR/MR webhook 기반의 백그라운드 자동 실행
- 기존 Git command의 provider CLI 설치·인증 방식 변경
- `gh` 또는 `glab` 자동 설치 및 token 발급·갱신
- 자동 merge, 승인, branch protection 우회
- 별도의 장기 저장소에 세션 대상 링크나 리뷰 처리 이력 저장
- 사용자의 기존 변경사항을 stash, reset, 삭제 또는 자동 commit

## 완료 기준

- `skills/review-comment/SKILL.md`가 Codex와 Claude Code에서 사용할 수 있는 명시적 skill 진입점으로 존재한다.
- Codex UI metadata가 기존 skill 형식과 일치하고 plugin validator를 통과한다.
- 첫 호출에서 PR/MR 링크를 요청하고, 링크 수신 후 같은 세션에서 대상을 재사용하도록 지침이 명확하다.
- GitHub/GitLab 모두 connector 우선 및 provider CLI fallback 규칙이 명확하다.
- 도구 미설치·미인증 시 자동 설치나 외부 변경 없이 중단한다.
- 새 리뷰 코멘트를 읽어 코드 수정, 검증, 변경 파일만 commit/push하고 완료 응답 및 가능한 thread resolve를 수행하도록 지침이 명확하다.
- 기존 Git command 파일과 기존 skill의 동작 계약이 변경되지 않는다.
- 전체 테스트와 plugin validation이 통과한다.
