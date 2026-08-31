# Maintainer release

`redeploy-plugin.ps1`는 저장소에 포함된 관리자용 배포 스크립트입니다. 지정한 원격 브랜치에 push된 내용을 Codex·Claude Code marketplace에서 다시 읽도록 갱신합니다.

## 릴리즈 절차

1. 배포할 브랜치를 원격에 push합니다.
2. 해당 브랜치의 깨끗한 worktree에서 실행합니다.

```powershell
.\scripts\redeploy-plugin.ps1 -Branch feature/review-comment
```

`-Branch`를 생략하면 `master`를 사용합니다. 스크립트는 현재 branch가 요청한 branch인지, 작업 트리가 깨끗한지, local branch가 `origin/<branch>`와 같은 commit인지, plugin validator가 통과하는지 확인합니다. 조건을 만족하지 않으면 Codex·Claude Code marketplace를 변경하지 않고 중단합니다.

## 배포 대상 변경

공식 기본 배포 대상은 `master`입니다. 다른 branch를 배포하려면 `-Branch`와 사용자의 marketplace 설치 ref를 같은 값으로 맞춥니다. Codex는 `--ref <branch>`, Claude Code는 Git URL 뒤에 `#<branch>`를 사용합니다.

## 운영 권한

실제 merge·push 권한은 Git hosting의 branch protection과 관리자 credential로 제한합니다. 스크립트는 요청한 branch, 원격 동기화 상태와 plugin 유효성을 확인한 뒤에만 marketplace를 갱신합니다.
