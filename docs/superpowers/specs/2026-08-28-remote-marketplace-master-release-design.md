# 원격 marketplace master 전용 릴리즈 설계

## 목적

플러그인 사용자가 저장소를 clone하거나 pull하지 않아도 공개 원격 marketplace를 통해 Codex와 Claude Code에서 `agent-orchestration`을 설치하고 업데이트할 수 있게 한다. 공식 marketplace 릴리즈는 항상 `master` 브랜치의 내용만 대상으로 하며, 릴리즈 작업은 로컬에 보관한 배포 스크립트 하나로 수행한다.

## 확정 요구사항

- 공개 Git 저장소를 Codex·Claude Code 공용 원격 marketplace source로 사용한다.
- `master`에 머지된 변경만 공식 marketplace 릴리즈 대상으로 인정한다.
- 배포 스크립트는 관리자의 로컬 환경에만 두며 저장소에는 배포하지 않는다.
- 배포 스크립트는 현재 브랜치가 `master`가 아니면 실행을 중단한다.
- 사용자는 저장소를 직접 clone/pull하지 않고 marketplace의 설치·업데이트 명령만 사용한다.
- Codex와 Claude Code의 marketplace manifest는 저장소 root를 plugin source로 가리킨다.
- 배포 방법과 배포 대상 변경 방법은 추적되는 `scripts/README.md`에 기록한다.

## 범위 밖

- feature 브랜치를 공식 marketplace source로 직접 제공하지 않는다.
- 배포 스크립트를 public 저장소에서 내려받아 실행하는 사용자용 설치 스크립트로 만들지 않는다.
- marketplace 서비스나 별도 패키지 저장소를 새로 운영하지 않는다.
- 스크립트 자체만으로 다른 사용자의 marketplace 명령 실행을 기술적으로 차단하지 않는다. public 저장소의 접근 제어는 Git 호스팅 서비스의 권한과 `master` 보호 규칙으로 관리한다.

## 설계

### 배포 기준

`master`를 유일한 공식 릴리즈 브랜치로 사용한다. 배포 스크립트는 다음 조건을 모두 확인한 뒤에만 marketplace 갱신을 시작한다.

1. 현재 checkout 브랜치가 정확히 `master`다.
2. 작업 트리가 깨끗하다.
3. 원격 `master`를 fetch한 뒤 local `master`와 원격 `master`가 같은 commit이다.
4. Codex·Claude Code manifest와 marketplace 구조 검증이 통과한다.
5. Codex와 Claude Code manifest의 plugin 이름·버전이 일치한다.

스크립트는 안전을 위해 자동 commit, merge, pull, push를 수행하지 않는다. 릴리즈할 변경을 `master`에 먼저 머지하고 원격에 push하는 책임은 관리자에게 있다.

### 배포 스크립트

배포 스크립트는 `scripts/redeploy-plugin.ps1`로 유지하되, 로컬 전용 파일로 `.gitignore`에 둔다. 스크립트는 저장소 root를 기준으로 동작하고, public Git 원격 주소와 marketplace 이름을 상수 또는 명시적인 설정값으로 관리한다.

실행 순서는 다음과 같다.

```text
master 및 원격 동기화 확인
  -> plugin/marketplace 검증
  -> Codex marketplace를 public 저장소의 master ref로 갱신
  -> Codex plugin 재설치 또는 업데이트
  -> Claude Code marketplace를 public 저장소의 master source로 갱신
  -> Claude Code plugin 업데이트
  -> 호스트 재시작 또는 새 스레드 필요 여부 출력
```

Codex와 Claude Code 명령은 host별 adapter 함수로 분리한다. 한 host의 갱신이 실패하면 오류를 표시하고 전체를 성공으로 보고하지 않는다. 기존 marketplace 등록을 제거해야 하는 경우에는 새 원격 source가 유효한지 확인한 뒤 수행하며, 실패 시 기존 등록을 불필요하게 삭제하지 않도록 한다.

### 원격 marketplace 사용

저장소 root의 `marketplace.json`과 `.claude-plugin/marketplace.json`은 각각 현재 저장소 root를 plugin source로 가리킨다. 사용자는 공개 Git 저장소를 marketplace source로 한 번 등록한 뒤, Codex marketplace upgrade/plugin update와 Claude Code marketplace update/plugin update를 사용한다. 설치 안내는 root `README.md`에 두고, 관리자의 릴리즈 절차와 브랜치 정책은 `scripts/README.md`에 둔다.

공식 설치 안내에서는 `master`만 사용한다. feature 브랜치 ref를 직접 등록하는 방법은 공식 배포 경로로 문서화하지 않는다.

### 파일 추적 정책

배포 스크립트는 추적하지 않지만 배포 방법 문서는 추적해야 한다. 따라서 `.gitignore`가 `scripts` 전체를 무시하는 형태라면 다음과 같이 README만 예외로 둔다.

```gitignore
/scripts/*
!/scripts/README.md
```

이미 추적 중인 검증·설치 스크립트가 있다면 기존 파일의 추적 상태와 충돌하지 않도록 해당 정책을 별도로 정리한다. 이번 릴리즈 자동화에서는 배포 스크립트만 local-only로 관리하는 구성을 기본으로 한다.

### 권한과 운영 경계

로컬 `.gitignore`는 배포 스크립트를 일반 사용자에게 배포하지 않게 할 뿐, 실행 권한을 보안적으로 제한하지는 않는다. 실제 릴리즈 권한은 다음 운영 규칙으로 보완한다.

- Git hosting에서 `master` branch protection을 활성화한다.
- 관리자 계정만 `master`에 merge할 수 있게 한다.
- 관리자만 public repository에 push할 수 있는 credential을 사용한다.
- 배포 스크립트는 현재 branch와 원격 동기화를 확인해 잘못된 source 배포를 방지한다.

## 오류 처리

- `master`가 아니면 어떤 marketplace 명령도 실행하지 않고 중단한다.
- dirty worktree 또는 local/remote commit 불일치가 있으면 중단하고 필요한 정리 작업을 출력한다.
- validator 실패 시 marketplace 변경을 수행하지 않는다.
- Codex 또는 Claude Code CLI가 없으면 해당 host를 건너뛰지 않고 실패로 보고한다.
- marketplace 갱신 실패 시 실패한 host와 명령을 출력한다.
- plugin 재설치·업데이트 중 하나라도 실패하면 전체 릴리즈를 성공으로 보고하지 않는다.
- 스크립트가 임시로 manifest를 변경하는 경우 `try/finally`로 원본을 복구하고 복구 실패도 오류로 보고한다.

## 검증 계획

자동화 테스트는 외부 CLI를 실제로 변경하지 않도록 명령 실행 계층을 mock할 수 있어야 한다. 최소 검증 항목은 다음과 같다.

- `master`가 아닌 branch에서 실행하면 중단한다.
- dirty worktree에서 실행하면 중단한다.
- 원격 `master`와 commit이 다르면 중단한다.
- plugin validator 실패 시 marketplace 명령을 호출하지 않는다.
- Codex와 Claude Code 갱신 명령이 모두 성공하면 성공으로 종료한다.
- 한 host의 갱신 명령이 실패하면 실패 코드로 종료한다.
- manifest 임시 변경이 있어도 성공·실패 모두 원본으로 복구된다.
- 공개 marketplace 설치 안내가 clone/pull을 요구하지 않고 master source를 가리킨다.

## 완료 기준

- `master`에 머지된 최신 plugin을 관리자의 단일 로컬 스크립트 실행으로 Codex와 Claude Code marketplace에서 갱신할 수 있다.
- feature branch에서 같은 스크립트를 실행하면 변경 없이 명확한 오류로 종료한다.
- 일반 사용자는 저장소 clone/pull 없이 공개 marketplace 등록과 plugin update만으로 사용할 수 있다.
- 배포 스크립트는 저장소에 포함되지 않고, `scripts/README.md`에는 master 전용 정책과 실행 방법이 남아 있다.
