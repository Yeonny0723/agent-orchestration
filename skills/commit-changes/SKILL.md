---
name: commit-changes
description: 현재 Git 변경을 원자적 커밋으로 나누어 계획하거나, 사용자가 승인한 Conventional Commit을 실제로 생성할 때 사용한다.
---

# 커밋 생성

이 skill은 직접 호출과 `git:commit` command 위임에 같은 절차를 사용한다. push는 책임 범위가 아니다.

## 변경 확인

1. `git status --short`, staged diff, unstaged diff와 최근 커밋 제목을 확인한다.
2. 스테이지된 파일이 있으면 해당 파일만 커밋 대상으로 삼고 unstaged 변경은 제외한다고 명시한다.
3. 스테이지된 파일이 없으면 변경을 목적별로 묶고 각 커밋에서 스테이징할 정확한 파일을 제안한다. `git add .`로 범위를 넓히지 않는다.
4. 사용자 변경을 되돌리거나 관련 없는 파일을 포함하지 않는다.

## 의존성 공급망 확인

- `package.json`이 대상이면 dependencies 계열의 `^`, `~`, `*`, `.x` 범위를 찾아 정확한 버전 고정을 권장한다. `file:`, `github:`, `git+`, `workspace:`는 제외한다.
- `package.json`과 대응 lockfile이 함께 바뀌었는지 확인하고 누락을 알린다.
- `package.json` 또는 lockfile 변경은 기능 코드와 별도 커밋으로 분리할지 우선 검토한다.
- lockfile만 바뀌었거나 manifest만 바뀐 경우 의도인지 확인한다.

## 계획과 승인

커밋 실행 전에 다음 커밋 계획 전체를 보여주고 사용자 승인을 받는다.

- 커밋 순서와 분할 이유
- 각 커밋의 정확한 파일 목록
- 최종 커밋 메시지
- 의존성 및 lockfile 경고

메시지는 `type(scope): 명령형 한글 요약`을 기본으로 하며 scope는 선택 사항이다. 모든 커밋에서 변경의 배경·목적·현상을 먼저 검토하고, 가능하면 맥락과 변경 결과가 함께 드러나는 제목을 권장한다. 예를 들어 `~로 인해 ~ 변경`, `~ 현상으로 ~ 보강`, `~을 위해 ~ 추가`처럼 작성한다. 다만 맥락을 넣으면 부자연스럽거나 제목이 지나치게 길어지는 경우에는 기존 요약형을 사용해도 된다. 제목은 72자 미만으로 유지하고 변경 목적 하나만 설명한다. 본문(description)은 기본적으로 만들지 않으며 사용자가 명시적으로 요청한 경우에만 추가한다. 허용 type은 `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`다.

승인 전에는 staging이나 commit을 변경하지 않는다. 수정 요청이 있으면 계획을 갱신하고 다시 승인받는다.

## 실행

1. 승인된 파일만 명시적으로 stage한다.
2. 각 staged diff가 승인된 범위와 같은지 다시 확인한다.
3. 승인된 메시지로 commit하고 결과 hash와 제목을 보고한다.
4. AI 서명, `Co-Authored-By` 또는 생성 도구 표식을 추가하지 않는다.
5. `--signoff`, `--author`, `--trailer`와 자동 생성 attribution을 사용하지 않는다.
6. commit 실패 시 우회하거나 amend하지 말고 원인과 현재 staged 상태를 보고한다.
