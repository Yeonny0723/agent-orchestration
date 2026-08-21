---
name: write-issue
description: 현재 작업 맥락에서 버그 또는 기능 이슈 초안을 작성하고 GitHub나 GitLab에 사용자 승인 후 생성할 때 사용한다.
---

# 이슈 작성

이 skill은 직접 호출과 `git:issue` command 위임에 같은 절차를 사용한다.

## Provider 감지

1. `git remote get-url origin`으로 remote host와 저장소 경로를 확인한다.
2. `github.com`이거나 현재 저장소에서 `gh repo view`만 성공하면 GitHub로 판정한다.
3. host가 GitLab이거나 현재 저장소에서 `glab repo view`만 성공하면 GitLab으로 판정한다.
4. 필요한 `gh` 또는 `glab` CLI와 인증 상태를 확인하되 token 값을 읽거나 출력하지 않는다.
5. 두 CLI가 모두 성공하거나 어느 쪽도 확인되지 않아 provider를 감지할 수 없으면 사용자에게 provider를 확인하고 외부 쓰기를 중단한다.

## 초안 작성

1. 사용자 인자에서 제목, 유형, labels와 관련 이슈를 확인한다.
2. 버그는 `assets/bug-issue-template.md`, 기능·개선·chore는 `assets/feature-issue-template.md`를 읽어 사용한다.
3. 버그 제목과 Background는 추정 원인이 아니라 관찰된 증상과 재현 조건으로 작성한다. 원인 미확정 상태에서는 Root Cause를 `가설`로 표시한다.
4. 기능 이슈는 목적, 범위와 비범위, 지켜야 할 계약, 완료 기준이 되는 Tasks를 포함한다.
5. 이슈만 읽어도 무엇을 왜 어디까지 해야 하는지 이해되게 작성한다. spec과 plan 경로는 보충 자료로만 제공하고 본문 내용을 링크로 대체하지 않는다.
6. 사용자나 저장소가 지정하지 않은 label을 임의로 만들지 않는다. 요청 label이 실제 provider 저장소에 없으면 생성을 중단하지 말고 label 제외 여부를 사용자에게 확인한다.

## 승인과 생성

1. provider, 이슈 유형, 제목, labels와 본문 전문을 보여주고 사용자 승인을 받는다.
2. 승인 전에는 issue를 생성하거나 기존 issue를 수정하지 않는다.
3. 승인 후 GitHub는 `gh issue create`, GitLab은 `glab issue create`로 초안과 동일한 제목과 본문을 생성한다.
4. provider CLI가 자체 확인 prompt를 표시하지 않도록 비대화형 옵션을 사용하되 이 skill의 사용자 승인 절차를 생략하지 않는다.
5. 생성 결과의 URL과 번호를 보고한다. 실패하면 오류, provider, 제목과 보존된 본문을 보고하고 다른 provider로 우회하지 않는다.
