---
name: post-git-comment
description: GitHub나 GitLab의 이슈 또는 PR/MR에 현재 대화 맥락을 한국어 코멘트로 작성하고 사용자 승인 후 게시할 때 사용한다.
---

# Git 코멘트 게시

이 skill은 직접 호출과 `git:comment` command 위임에 같은 절차를 사용한다.

## Provider와 대상 확인

1. `git remote get-url origin`으로 remote host와 저장소 경로를 확인한다.
2. `github.com`이거나 현재 저장소에서 `gh repo view`만 성공하면 GitHub로 판정한다.
3. host가 GitLab이거나 현재 저장소에서 `glab repo view`만 성공하면 GitLab으로 판정한다.
4. 필요한 `gh` 또는 `glab` CLI와 인증 상태를 확인하되 token 값을 읽거나 출력하지 않는다.
5. provider를 감지할 수 없거나 대상 번호와 이슈/PR·MR 구분이 없으면 사용자에게 확인하고 외부 쓰기를 중단한다.

## 초안과 승인

1. 사용자가 본문을 제공하면 원문을 유지한다. 그렇지 않으면 직전 대화의 확정 결정, 분석 또는 상태만 한국어 Markdown으로 정리한다.
2. 조사 중간 가설과 진행 경과는 이슈 코멘트에 남길 수 있지만, PR·MR 본문에는 최종 상태와 결정만 남긴다.
3. 대상 provider, 이슈 또는 PR·MR 번호, 게시 본문 전문을 보여주고 사용자 승인을 받는다.
4. 승인 전에는 코멘트를 게시하거나 기존 코멘트를 수정하지 않는다.

## 게시

1. 승인 후 GitHub 이슈에는 `gh issue comment`, GitHub PR에는 `gh pr comment`를 사용한다.
2. GitLab 이슈에는 `glab issue note`, GitLab MR에는 `glab mr note create`를 사용한다. 자동 상태 코멘트는 merge를 막지 않도록 non-resolvable note로 게시한다.
3. CLI가 없거나 인증·권한 오류가 나면 다른 provider나 token 방식으로 우회하지 않고 실패 원인과 보존된 본문을 보고한다.
4. 게시 결과 URL 또는 provider가 반환한 식별자를 보고한다.
