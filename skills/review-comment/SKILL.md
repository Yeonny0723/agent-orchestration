---
name: review-comment
description: 사용자가 명시적으로 호출한 GitHub PR 또는 GitLab MR의 새 리뷰 코멘트를 읽고 필요한 수정, 검증, 커밋과 push까지 수행할 때 사용한다.
---

# 리뷰 코멘트 반영

이 skill은 사용자가 skill을 호출할 때만 실행한다. 사용자가 `review-comment`를 명시적으로 호출할 때만 실행하며, 백그라운드 polling으로 실행하지 않는다. 호출마다 대상의 새 리뷰 코멘트를 확인하고, 실행 가능한 요청만 코드에 반영한 뒤 검증하고 커밋한다.

## 대상과 세션

1. 현재 대화 세션에 저장된 대상이 없으면 사용자에게 PR/MR 링크를 먼저 요청한다. 링크를 받기 전에는 provider 조회나 코드 수정을 시작하지 않는다.
2. 링크에서 GitHub PR 또는 GitLab MR의 provider, 저장소 또는 프로젝트, 번호를 파싱하고 현재 대화 세션의 대상 기록으로 저장한다.
3. 같은 세션에서 다시 호출되면 저장된 PR/MR 링크를 다시 요구하지 않는다. 사용자가 새 링크를 주면 새 대상이 이전 대상보다 우선한다.
4. 대상이 현재 checkout과 맞는지 remote와 source branch를 확인한다. 대상이 모호하거나 checkout과 일치하지 않으면 외부 쓰기와 코드 수정을 멈추고 사용자에게 확인한다.

## provider 접근

1. 사용 가능한 connector를 먼저 확인한다. connector가 제공하는 리뷰 조회, 답글, thread/discussion resolve 기능을 우선 사용한다.
2. connector가 없거나 필요한 기능을 제공하지 않을 때만 provider CLI를 재사용한다. GitHub에는 `gh`, GitLab에는 `glab`을 사용한다.
3. 필요한 CLI가 설치되지 않았거나 인증·권한 확인에 실패하면 CLI를 설치하지 않으며 인증을 자동으로 변경하지 않는다. token을 읽거나 출력하지 않고, 변경을 수행하지 않고 실패 원인만 보고한다.
4. 이 skill의 provider 접근 규칙은 기존 `git:commit`, 기존 `git:pr`, 기존 `git:comment`, 기존 `git:issue` command의 동작을 변경하지 않는다. 기존 명령은 기존처럼 필요한 CLI와 인증을 전제로 하며, 자동 설치를 추가하지 않는다.

## 새 코멘트 선별

1. 대상 PR/MR에서 이전 실행 이후의 새 unresolved 리뷰 코멘트 또는 discussion을 조회한다. provider가 제공하는 생성 시각, ID, thread 상태와 현재 세션에서 처리한 ID를 함께 사용해 중복 처리를 피한다.
2. 사람이 작성한 코멘트 중 실행 가능한 변경 요청만 남긴다. 봇 메시지, 이미 resolved된 항목, `✅ 반영 완료` 답글, 중복 요청, 단순 질의나 감사 인사는 수정 대상으로 삼지 않는다.
3. 각 항목에서 파일·라인·본문과 주변 diff를 확인한다. 코멘트의 요구가 불명확하거나 현재 코드와 충돌하면 임의로 해석하지 말고 해당 항목을 보류한 이유를 보고한다.
4. 코멘트별로 필요한 최소 변경을 수행하고, 관련 테스트 또는 프로젝트의 일반 검증을 실행한다. 하나의 코멘트 실패가 다른 코멘트의 성공을 숨기지 않도록 항목별 결과를 기록한다.

## 커밋과 push

사용자가 승인한 이 workflow는 수정이 끝나면 자동 commit과 push를 수행한다.

1. 실행 시작 전에 `git status --short`와 대상 branch를 기록한다. 실행 중 agent가 실제로 수정한 파일 목록을 별도로 추적한다.
2. 검증이 통과한 경우에만 이번 실행에서 변경된 파일만 명시적으로 stage한다. `git add -A`나 전체 파일 staging을 사용하지 않는다.
3. 기존 사용자 변경은 보존한다. stash, reset, checkout으로 덮어쓰거나 삭제하지 않으며, 이번 실행에서 수정하지 않은 변경 파일을 커밋하지 않는다.
4. 관련 변경을 하나의 간결한 커밋으로 만들고 source branch에 push한다. 커밋 또는 push가 실패하면 원격 리뷰 상태를 성공으로 표시하지 않는다.
5. 자동 merge, 승인, branch protection 우회는 수행하지 않는다.

## 성공 처리와 보고

각 코멘트의 변경과 검증, 커밋 및 push가 모두 성공했을 때만 해당 리뷰 항목에 다음 형식으로 답한다.

`✅ 반영 완료 — commit SHA: <sha>`

답글을 게시한 뒤 provider 기능이 지원하면 해당 GitHub review thread 또는 GitLab discussion을 resolve한다. GitHub review thread와 GitLab discussion을 resolve할 수 없거나 답글 게시가 실패하면 코멘트는 resolve하지 않고 실패 원인과 commit SHA를 보고한다. 실패하면 코멘트를 resolve하지 않는다.

새 실행 가능한 코멘트가 없으면 코드와 원격 상태를 변경하지 않고 없다는 사실만 보고한다. 보고에는 대상, 처리한 코멘트 ID 또는 위치, 변경 파일, 검증 명령과 결과, commit SHA, push 결과, 보류 또는 실패 항목을 포함한다.
