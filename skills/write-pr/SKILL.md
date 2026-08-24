---
name: write-pr
description: 구현이 끝난 현재 저장소에서 승인된 spec과 실제 diff를 근거로 검증을 다시 수행하고 한국어 PR 초안을 작성하거나 승인 후 PR을 생성할 때 사용한다.
---

# PR 작성

## 진입

사용자가 직접 호출할 때만 시작한다. `orchestrate-work`가 자동 실행하거나 다른 세션을 열지 않는다. 사용자가 선택한 Codex, Claude Code 또는 Agent Skills 호환 agent에서 같은 계약을 사용하며 특정 호스트나 PR writer agent를 고정하지 않는다. `git:pr` command와 모든 호스트별 PR 진입점은 이 skill에만 1:1로 위임한다.

## 근거와 검증

1. 승인된 spec에서 문제 배경, 목적, 비목표, 현재 구조와 제약, 결정과 이유를 추출한다.
2. 현재 저장소의 실제 diff를 직접 읽고 최종 변경 범위와 리뷰 포인트를 추출한다.
3. plugin root의 `conventions/general.md`와 이 skill의 `assets/pr-template.md`, `references/writing-pr-rules.md`를 읽는다.
4. 저장소 지침과 plan에서 일반 검증 명령을 식별해 현재 diff에 다시 실행한다.
5. `verify-test-sensitivity`를 현재 diff에 다시 실행하고 mutation이 정확히 복원됐는지 확인한다.
6. 검증이 실패하거나 실행할 수 없으면 PR 작성을 중단하고 부족한 근거를 보고한다.

`understand-work 실행 여부와 무관`하게 진행하며 이해 세션 결과를 요구하지 않는다. 별도 PR 지식 패킷이나 중간 문서를 만들지 않는다.

## 작성과 provider 감지

1. `author-reviewable-text`에 산출물 종류가 PR·MR 제목과 본문임을 밝히고 PR 템플릿과 필수 형식, 승인된 spec·실제 diff·검증 결과인 확인된 사실, provider의 길이 제한과 target branch 등 사용자 옵션을 전달한다. 반환된 한국어 제목과 본문 최종 초안을 사용한다.
2. 시간순 작업 로그나 폐기한 시행착오 대신 최종 상태를 설명한다.
3. 한국어 제목과 본문에 문제 배경, 목적, 주요 결정과 이유, 실제 변경, 검증 명령과 결과, 남은 위험을 포함한다.
4. 실행 근거 없이 테스트 성공을 주장하지 않는다.
5. `git remote get-url origin`으로 remote host와 저장소 경로를 확인한다. `github.com`이거나 `gh repo view`만 성공하면 GitHub, host가 GitLab이거나 `glab repo view`만 성공하면 GitLab으로 판정한다.
6. 필요한 `gh` 또는 `glab` CLI와 인증 상태를 확인하되 token 값을 읽거나 출력하지 않는다. provider를 감지할 수 없거나 둘 다 성공하면 외부 생성은 중단하고 사용자에게 확인한다.

## 승인과 생성

1. 제목과 본문 초안, target branch, provider, push 여부와 실행할 외부 명령을 사용자에게 보여주고 사용자 승인을 받는다.
2. 승인 전에는 push나 PR·MR 생성을 하지 않는다.
3. 승인 후 현재 branch가 target branch가 아닌지 확인하고 `git push -u origin HEAD`로 source branch를 push한다.
4. GitHub에서는 `gh pr create`, GitLab에서는 `glab mr create`로 승인된 제목과 본문을 생성한다.
5. provider CLI가 없거나 push·생성에 실패하면 다른 provider나 token 방식으로 우회하지 않고 현재 branch, 실패 원인과 보존된 초안을 보고한다.
6. 생성된 PR·MR URL을 보고한다.
