# 교차 호스트 예상 관찰 결과

## 규모 라우팅

- 소형 명확 작업은 불필요한 그릴을 생략한다.
- 소형 모호 작업은 최대 두 질문으로 결과를 바꾸는 모호함만 확정한다.
- 중형과 대형은 실질적 spec 결정을 전수 목록화하고 한 번에 하나씩 확정한다.
- 대형은 독립 산출물 경계로 plan과 PR을 분리한다.

## 독립 진입점

- Codex와 Claude Code에서 같은 skill 계약을 사용한다.
- `implement-with-tdd`는 규모 판정이나 spec 결정을 반복하지 않고 테스트 우선 구현과 일반 검증만 수행한 뒤 `verify-test-sensitivity`를 안내한다.
- `verify-test-sensitivity`는 전체 orchestrator를 시작하지 않고 mutation 하나, killed/survived 판정, 정확한 복원과 원본 검증만 수행한다.
- `understand-work`는 최대 5문항을 한 번에 하나씩 모두 묻고 결과를 현재 대화에만 남긴다.
- `write-pr`은 현재 spec, 실제 diff와 재실행한 검증 근거로 한국어 초안을 만들고 사용자 승인 전에는 외부 PR을 생성하지 않는다.
- `git-commit`, `git-issue`, `git-comment`, `git-pr`은 대응 skill 하나에만 위임한다.
- 이슈, 코멘트와 PR/MR command는 GitHub 또는 GitLab을 감지하지 못하면 외부 쓰기 없이 초안과 중단 사유를 보고한다.
- 외부 이슈, 코멘트, PR/MR 생성과 push는 사용자 승인 전에는 수행하지 않는다.

## 테스트 민감도 실패

- `survived`를 성공으로 처리하지 않는다.
- mutation을 정확히 복원하고 테스트를 보강한 뒤 같은 행위를 다시 검증한다.

## 선택형 이해 세션

- `understand-work`를 자동 실행하지 않는다.
- 이해 세션 부재가 `write-pr`을 차단하지 않는다.

## 문체 프로파일

- profile이 있으면 문체에 적용하지만 내용 계약과 질문 구조는 유지한다.
- profile이 없으면 설정 가능성을 한 번 안내하고 기본 한국어 문체로 계속한다.
