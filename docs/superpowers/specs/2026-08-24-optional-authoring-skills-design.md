# 선택형 작성 보조 스킬 통합 설계

## 문제

현재 여러 workflow skill이 `voice-profile.md`를 직접 읽어 사용자 대면 질문과 산출물의 문체를 결정한다. 이 구조에는 세 가지 문제가 있다.

- 문체 처리 책임이 `orchestrate-work`, `decision-first-grill`, `implement-with-tdd`, `understand-work`, `write-pr`에 흩어져 있다.
- `capture-authoring-voice`가 만든 사용자 문체만 반영하며, AI 특유의 과장, 반복 구조와 상투 표현을 줄이는 공통 작성 규칙이 없다.
- `implement-with-tdd`는 적용할 convention pack을 확인한다고만 적혀 있고 `apply-conventions`를 호출하지 않아 실제 적용을 보장하지 않는다.

## 목적

- 사용자 검토 또는 승인을 거치는 글을 한 공통 작성 계약으로 생성한다.
- `capture-authoring-voice`의 사용자 문체와 외부 `stop-slop`, `humanizer` 규칙을 함께 사용할 수 있게 한다.
- 외부 작성 보조 스킬을 선택 사항으로 두고, 설치 조합과 관계없이 workflow를 계속 실행한다.
- `implement-with-tdd`가 구현 전에 `apply-conventions`를 명시적으로 호출하게 한다.

## 비목표

- 외부 작성 보조 스킬의 내용을 플러그인 안에 복사하거나 축소 재구현하지 않는다.
- 커밋 메시지, 코드, 테스트, 로그와 명령어에는 작성 보조 스킬을 적용하지 않는다.
- 외부 스킬 버전을 고정하거나 자동으로 업데이트하지 않는다.
- `capture-authoring-voice`를 필수 설정 단계로 만들지 않는다.
- 작성 보조 스킬을 적용하기 위해 완성된 초안을 반복해서 전면 재작성하지 않는다.

## 적용 범위

공통 작성 계약은 다음 글에 적용한다.

- spec
- plan
- Issue 제목과 본문
- Issue, PR, MR 코멘트
- PR, MR 제목과 본문
- `understand-work`가 사용자에게 제시하는 질문

다음 내용에는 적용하지 않는다.

- `commit-changes`가 만드는 커밋 메시지
- 일반적인 진행 질문과 선택지
- 구현과 검증 결과 보고
- `understand-work`가 답변 뒤에 제공하는 기술적 피드백과 근거 설명
- 코드, 테스트, 로그, 명령어와 사용자가 제공한 인용문

## 결정

### 공통 작성 skill

플러그인에 `author-reviewable-text` skill을 추가한다. 이 skill은 독립적인 문서 종류나 Git 작업을 소유하지 않는다. 호출한 skill이 제공한 산출물 종류, 필수 형식과 사실 근거를 바탕으로 사용자에게 제시할 최종 초안을 작성한다.

처리 순서는 다음과 같다.

1. 호출한 skill이 요구하는 템플릿, 길이 제한, 필수 항목과 사실 근거를 확인한다.
2. `$AGENT_ORCHESTRATION_HOME/voice-profile.md`를 확인하고 환경 변수가 없으면 `~/.agent-orchestration/voice-profile.md`를 확인한다.
3. 설치된 선택형 작성 보조 스킬을 확인하고 해당 스킬을 호출한다.
4. 문체 프로파일과 호출한 외부 스킬의 규칙을 참고해 최종 초안을 한 번 작성한다.
5. 필수 절, 사실, 수치, 파일명, 명령어와 산출물 형식이 유지됐는지 확인한다.
6. 문제가 발견된 부분만 수정하고 호출한 skill에 최종 초안을 반환한다.

5단계는 두 번째 전면 재작성 단계가 아니다. 공통 skill은 사실과 형식을 검사하며, 문제가 있는 부분만 고친다.

### 규칙 우선순위

규칙이 충돌하면 다음 순서를 적용한다.

1. 사용자의 명시적 지시
2. 산출물 템플릿, 필수 내용과 길이 제한
3. 실제 코드, diff, 검증 결과와 확인된 사실
4. `voice-profile.md`의 사용자 문체
5. `humanizer`
6. `stop-slop`
7. 기본 한국어 문체

낮은 순위의 규칙이 높은 순위의 의미나 형식을 바꾸면 해당 규칙을 적용하지 않는다. 예를 들어 `stop-slop`의 엄격한 문장 규칙이 기술적 의미를 흐리거나 필수 내용을 제거하면 원래 내용을 유지한다.

### 선택형 외부 스킬

선택할 수 있는 외부 스킬은 두 개다.

- `stop-slop`: `https://github.com/hardikpandya/stop-slop`
- `humanizer`: `https://github.com/blader/humanizer`

허용하는 설치 상태는 다음 네 가지다.

- 둘 다 설치
- `stop-slop`만 설치
- `humanizer`만 설치
- 둘 다 설치하지 않음

`author-reviewable-text`는 설치된 스킬만 호출한다. 아무것도 설치되지 않았으면 문체 프로파일 또는 기본 한국어 문체로 작성한다. 설치된 스킬을 호출할 수 없으면 해당 이름과 원인을 보고하고 나머지 규칙으로 계속한다. 선택형 의존성 오류는 산출물 작성을 차단하지 않는다.

`unslop`은 의존성, 설치 선택지와 작성 계약에 포함하지 않는다.

### 설치와 업데이트

`setup-orchestration`은 기존 필수 의존성과 별도로 `stop-slop`, `humanizer`를 선택 가능한 작성 보조 스킬로 제시한다. 사용자가 선택한 항목만 사용자 범위에 설치한다.

설치에는 Skills CLI를 사용한다.

```powershell
npx skills add hardikpandya/stop-slop --global --skill stop-slop
npx skills add blader/humanizer --global --skill humanizer
```

설치 시점의 최신 `main`을 사용한다. 이미 설치된 항목은 자동으로 업데이트하거나 덮어쓰지 않는다. 업데이트는 사용자가 명시적으로 요청할 때만 수행한다. 설치 전에 원본 URL, 대상 경로와 명령을 보여주고 승인을 받는다.

같은 이름과 같은 원본이면 설치 완료로 판단한다. 같은 이름이 다른 원본을 가리키거나 대상 경로에 기대한 링크가 아닌 항목이 있으면 덮어쓰지 않고 충돌을 보고한다.

### 문체 프로파일 통합

`capture-authoring-voice`는 선택형 사용자 문체 설정 skill로 유지한다. 프로파일이 없어도 설정을 반복해서 권유하거나 workflow를 막지 않는다.

기존 workflow skill이 `voice-profile.md`를 직접 읽는 계약은 제거한다. 적용 범위에 포함된 글을 만들 때만 `author-reviewable-text`가 프로파일을 읽는다. 이로써 일반 진행 질문, 구현 결과와 `understand-work`의 기술적 피드백에는 프로파일이나 외부 작성 규칙이 자동 적용되지 않는다.

### 호출 지점

- `decision-first-grill`: spec을 사용자에게 제시하기 전에 호출한다.
- `orchestrate-work`: plan 작성이 끝난 뒤 저장하기 전에 호출한다. plan이 사용자 리뷰 게이트가 아니라는 기존 계약은 유지한다.
- `write-issue`: Issue 제목과 본문을 승인받기 전에 호출한다.
- `post-git-comment`: 코멘트 초안을 승인받기 전에 호출한다.
- `write-pr`: PR 또는 MR 제목과 본문을 승인받기 전에 호출한다.
- `understand-work`: 선정한 각 질문을 사용자에게 보여주기 전에 호출한다. 답변 피드백에는 호출하지 않는다.

`commit-changes`에는 호출을 추가하지 않는다. 커밋 메시지는 기존 Conventional Commit 형식과 72자 제한만 적용한다.

### convention 적용 보강

`implement-with-tdd`는 구현 전에 `apply-conventions`를 명시적으로 호출한다.

1. 승인된 spec, 해당되는 plan과 저장소 지침을 확인한다.
2. `apply-conventions`를 호출해 프로젝트 규칙과 변경 대상의 언어, 프레임워크에 맞는 pack을 선택한다.
3. 선택한 pack과 충돌 시 우선한 프로젝트 규칙을 구현 입력으로 유지한다.
4. `superpowers:test-driven-development`를 호출한다.
5. 선택한 규칙에 따라 테스트와 구현을 작성하고 검증한다.
6. 구현 중 새로운 언어 또는 프레임워크 파일이 범위에 들어오면 적용 pack을 다시 확인한다.

이 호출은 `implement-with-tdd`가 직접 실행되거나 `orchestrate-work`에서 위임받는 두 경로에 동일하게 적용한다. `orchestrate-work`에는 convention 선택 로직을 복제하지 않는다.

## 오류 처리

- 선택형 외부 스킬이 없거나 읽기 실패해도 기본 작성 경로로 계속한다.
- 문체 프로파일이 없거나 읽기 실패하면 기본 한국어 문체로 계속한다.
- 외부 작성 규칙이 사실, 필수 형식 또는 사용자의 명시적 지시와 충돌하면 외부 규칙을 무시한다.
- `author-reviewable-text`가 필수 사실이나 형식을 확인할 근거를 받지 못하면 내용을 추정하지 않고 호출한 skill에 부족한 입력을 반환한다.
- `apply-conventions`가 프로젝트 규칙과 plugin pack의 충돌을 발견하면 프로젝트 규칙을 우선하고 선택 결과를 plan 또는 PR 검증 근거에 남긴다.

## 검증

계약 테스트는 다음 내용을 확인한다.

- `author-reviewable-text`와 `capture-authoring-voice`에 유효한 skill metadata가 있다.
- 적용 대상 skill은 `author-reviewable-text`를 정확히 한 번 참조한다.
- `commit-changes`와 구현 결과 작성 절차는 공통 작성 skill을 참조하지 않는다.
- `understand-work`는 질문에만 공통 작성 skill을 사용하고 답변 피드백에는 사용하지 않는다.
- `setup-orchestration`은 `stop-slop`, `humanizer`를 선택 사항으로 명시하고 0개, 1개, 2개 설치를 모두 허용한다.
- 선택하지 않은 외부 스킬을 설치하지 않으며 기존 경로 충돌을 덮어쓰지 않는다.
- spec, plan, Issue, 코멘트와 PR의 기존 필수 형식 및 승인 계약이 문체 규칙보다 우선한다.
- `implement-with-tdd`는 `apply-conventions`를 `superpowers:test-driven-development`보다 먼저 호출한다.
- 기존 plugin 구조 검증, Git 승인 경계와 provider 감지 계약이 유지된다.

## 완료 기준

- 적용 대상 글이 `author-reviewable-text`를 통해 작성된다.
- 산출물 작성 시 `voice-profile.md`를 적용하는 책임이 공통 작성 skill 한 곳으로 모인다.
- 사용자는 `stop-slop`, `humanizer`를 원하는 조합으로 설치하거나 둘 다 생략할 수 있다.
- 선택형 외부 스킬의 부재나 오류가 workflow를 차단하지 않는다.
- 커밋 메시지와 적용 제외 항목의 기존 동작이 유지된다.
- `implement-with-tdd`가 모든 호출 경로에서 `apply-conventions`를 먼저 실행한다.
- 전체 단위 테스트와 plugin 검증이 통과한다.
