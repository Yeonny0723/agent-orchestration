# 에이전트 오케스트레이션 플러그인 구현 계획

> **에이전트 작업자용:** 필수 하위 스킬로 `superpowers:subagent-driven-development`(권장) 또는 `superpowers:executing-plans`를 사용해 이 계획을 태스크별로 실행한다. 진행 상태는 체크박스(`- [ ]`)로 추적한다.

**목표:** Codex와 Claude Code에서 공통으로 사용하는 규모별 개발 워크플로우와 TDD 구현, 테스트 민감도 검증, 작업 이해, PR 작성을 독립 호출할 수 있는 플러그인을 제공한다.

**아키텍처:** Agent Skills 표준의 `skills/`를 공통 코어로 사용하고, manifest와 custom agent는 플랫폼별 어댑터로 분리한다. `implement-with-tdd`, `verify-test-sensitivity`, `understand-work`, `commit-changes`, `write-issue`, `post-git-comment`, `write-pr`는 안정된 이름과 단일 책임을 가진 독립 진입점이며 `orchestrate-work`는 개발 흐름에 필요한 기능만 조합한다. Git command 네 개는 대응 skill 하나에 1:1로 위임하는 얇은 adapter이며 provider 감지와 업무 로직을 포함하지 않는다. 워크플로우와 호출 경계는 Markdown과 JSON 계약으로 표현하며, Python 표준 라이브러리 기반 검증기가 구조와 교차 플랫폼 대응 관계를 검사한다. 대화형 `setup-orchestration` skill이 설치 진입점이 되어 `superpowers`, `grill-with-docs`, `domain-modeling` 외부 의존성을 한 번 검사하고 누락 항목의 설치를 안내하거나 실행한다. 사용자 skill 원본은 `~/.agents/skills`에 두고 Claude Code의 `~/.claude/skills`에는 운영체제에 맞는 디렉터리 링크를 만든다. 규모 판정 기준과 Adept 질문 설계 규칙은 출처를 표시한 plugin reference로 포함한다. 정상 설치 후에는 워크플로우마다 재검사하지 않는다. 실제 mutation은 agent가 recipe에 따라 수행하고 자동 mutation 엔진은 만들지 않는다.

**기술 스택:** Agent Skills (`SKILL.md`), JSON, TOML, Markdown, Python 3.11+ 표준 라이브러리, `unittest`

---

## 계획 기술 합의

### TA-01: 외부 skill 의존성 정책

- **질문:** superpowers, grill-with-docs, Adept 질문 설계 규칙 같은 외부 기능이 없는 환경을 어떻게 처리할 것인가?
- **선택:** 필수 의존성으로 선언한다.
- **이유:** 기존 도구를 포크하거나 축소 재구현하지 않으면서 양쪽 호스트에서 동일한 워크플로우 계약을 유지한다.
- **구현상 결과:** 누락된 의존성과 설치 방법을 구체적으로 보고하고, 필요한 의존성이 준비되기 전에는 플러그인 설치를 완료하지 않는다.
- **spec 영향:** 없음.

### TA-02: 외부 의존성 검사 시점

- **질문:** 필수 의존성을 설치 시, 실행 시 또는 둘 다 검사할 것인가?
- **선택:** 설치 시에만 한 번 검사한다.
- **이유:** 정상 설치 후 반복되는 워크플로우 진입 비용과 호스트별 런타임 판정 차이를 없앤다.
- **구현상 결과:** 설치가 성공하면 각 skill은 의존성이 준비됐다고 간주한다. 설치 이후 사용자가 의존성을 삭제하거나 이동한 상황은 자동 감지 범위에서 제외한다.
- **spec 영향:** 없음.

### TA-03: 설치 흐름

- **질문:** 설치 시 의존성 검사를 호스트 기본 설치, 통합 스크립트 또는 대화형 setup skill 중 어디에 연결할 것인가?
- **선택:** 대화형 `setup-orchestration` skill을 설치 진입점으로 사용한다.
- **이유:** Codex와 Claude Code의 설치 방식 차이를 agent가 흡수하고, 사용자가 누락 의존성과 설치 조치를 대화형으로 확인할 수 있다.
- **구현상 결과:** setup skill이 현재 호스트와 설치 상태를 식별하고, 필수 의존성을 검사하며, 누락 항목별 설치 안내 또는 실행 승인을 제공한다. 설치 검사는 결정론적 자동화보다 대화형 관찰 가능성을 우선한다.
- **spec 영향:** 없음.

### TA-04: 외부 의존성과 내장 reference 경계

- **질문:** 원본 도구 중 무엇을 실행 시 외부 의존성으로 유지하고 무엇을 plugin reference로 포함할 것인가?
- **선택:** `superpowers`, `grill-with-docs`, `domain-modeling`은 외부 skill로 사용한다. `work-scale-workflow`의 규모 판정 기준과 Adept의 질문 설계 규칙은 출처를 표시한 plugin reference로 포함한다.
- **이유:** 실제 대화형 workflow를 중복 구현하지 않으면서 개인 로컬 파일 경로에 대한 배포 의존성을 제거한다.
- **구현상 결과:** setup skill은 외부 실행 skill만 검사한다. 구조 검증기는 두 내장 reference의 존재와 출처 표기를 검사한다.
- **spec 영향:** 없음.

### TA-05: PR 작성 세션의 최종 검증 근거 확보

- **질문:** 구현 세션과 다른 PR 작성 세션에서 최종 검증 근거를 임시 파일, 재실행 또는 사용자 입력 중 어떤 방식으로 확보할 것인가?
- **선택:** PR 작성 세션이 현재 diff를 기준으로 최종 검증을 다시 실행한다.
- **이유:** 세션 간 임시 산출물을 추가하지 않고 PR에 기록되는 검증 결과가 현재 변경과 정확히 대응하도록 한다.
- **구현상 결과:** `write-pr`은 일반 검증과 테스트 민감도 검증을 직접 다시 실행한다. 하나라도 실패하거나 실행할 수 없으면 PR 초안 작성을 중단한다. 이전 구현 세션의 검증 로그는 PR 근거로 신뢰하지 않는다.
- **spec 영향:** 없음. 승인된 spec의 `최종 검증 근거 확인`을 현재 세션의 재실행으로 충족한다.

### TA-06: setup skill의 설치 실행 권한

- **질문:** setup skill이 누락 의존성을 직접 설치할 때 어떤 승인 단위를 사용할 것인가?
- **선택:** 의존성마다 설치 위치, 명령, 변경 범위를 보여주고 개별 승인을 받은 뒤 설치한다.
- **이유:** 대화형 설치의 편의성을 유지하면서 전역 파일 변경과 외부 다운로드를 항목별로 통제한다.
- **구현상 결과:** 승인하지 않은 항목은 건너뛰지 않고 설치 미완료로 보고한다. 설치 실패 시 다음 항목으로 진행하지 않으며, 이미 성공한 설치는 되돌리지 않고 결과 목록에 남긴다.
- **spec 영향:** 없음.

### TA-07: 외부 skill 설치 범위

- **질문:** 필수 외부 skill을 사용자 범위, 프로젝트 범위 또는 항목별 선택 범위 중 어디에 설치할 것인가?
- **선택:** 사용자 범위에 설치한다.
- **이유:** 여러 프로젝트와 두 코딩 에이전트에서 같은 외부 workflow를 재사용하고 프로젝트별 중복과 버전 편차를 줄인다.
- **구현상 결과:** 프로젝트에는 이 plugin과 프로젝트별 설정만 둔다. setup skill은 Codex의 `~/.agents/skills`와 Claude Code의 `~/.claude/skills` 사용자 탐색 위치를 대상으로 설치 상태를 확인한다.
- **spec 영향:** 없음.

### TA-08: 사용자 skill의 두 호스트 공유 방식

- **질문:** 사용자 범위 skill을 두 호스트 경로에 복사할지, 중립 원본을 둘지, Codex 사용자 경로를 원본으로 공유할지 결정한다.
- **선택:** `~/.agents/skills`를 원본으로 사용하고 `~/.claude/skills/<skill-name>`에서 원본으로 연결한다.
- **이유:** Codex의 공식 사용자 skill 위치를 단일 원본으로 유지하면서 Claude Code가 지원하는 symlink 탐색을 활용해 복사본의 버전 편차를 없앤다.
- **구현상 결과:** Windows에서는 directory junction을 우선하고, Unix 계열에서는 symbolic link를 사용한다. setup skill은 링크 생성 전 대상과 원본 경로를 사용자에게 보여주고 승인을 받는다.
- **spec 영향:** 없음.

### TA-09: 기존 사용자 skill 경로 충돌 처리

- **질문:** Claude Code 사용자 skill 경로에 기대한 원본 링크가 아닌 파일이나 디렉터리가 이미 있을 때 어떻게 처리할 것인가?
- **선택:** 기존 항목을 덮어쓰거나 이동하지 않고 충돌을 보고한 뒤 중단한다.
- **이유:** setup skill이 사용자의 기존 skill을 손상하거나 서로 다른 버전의 내용을 자동 병합하는 위험을 제거한다.
- **구현상 결과:** 충돌 보고에는 기존 경로, 기대 원본, 감지한 항목 유형과 사용자가 직접 해결한 뒤 재실행해야 한다는 안내를 포함한다. 이미 올바른 링크이면 idempotent 성공으로 처리한다.
- **spec 영향:** 없음.

### TA-10: 두 호스트의 plugin 배포 방식

- **질문:** plugin을 개인 marketplace, 개발 경로 또는 사용자 skill 링크 중 어떤 방식으로 두 호스트에 배포할 것인가?
- **선택:** 동일한 plugin source를 Codex와 Claude Code의 개인 marketplace에 각각 등록한다.
- **이유:** plugin manifest, namespace, custom agent와 버전 관리 기능을 유지하면서 두 호스트가 같은 원본을 사용하게 한다.
- **구현상 결과:** setup skill은 호스트별 marketplace 등록 상태를 보여주고 각각 사용자 승인을 받아 등록한다. 한 호스트 등록이 실패하면 다른 호스트의 성공 상태는 유지하되 설치 전체를 미완료로 보고한다.
- **spec 영향:** 없음.

### TA-11: 테스트 민감도 mutation 복원 방식

- **질문:** 테스트가 결함을 잡는지 확인하려고 운영 코드에 잠시 넣은 mutation을 어떻게 안전하게 제거할 것인가?
- **선택:** mutation 전에 대상 파일의 현재 바이트와 SHA-256을 임시 snapshot으로 저장하고, 테스트 후 바이트를 복원한 뒤 hash 일치를 확인한다.
- **이유:** 기존 미커밋 변경을 포함한 현재 파일 상태를 그대로 보존하고, 역방향 patch의 모호함이나 `git checkout`에 의한 사용자 변경 손실을 방지한다.
- **구현상 결과:** snapshot과 복원만 담당하는 Python 표준 라이브러리 helper를 제공한다. mutation 생성 자체는 recipe를 따르는 agent가 수행하며 자동 mutation runner는 만들지 않는다. 복원 hash가 다르면 전체 검증을 실패로 처리한다.
- **spec 영향:** 없음.

### TA-12: 작업 이해 기능의 목적과 책임

- **질문:** 작업 이해 기능을 조직이 반드시 보관해야 하는 산출물과 blocking gate로 둘 것인가, 사용자의 개인적인 변경 이해를 확인하고 넓히는 세션으로 둘 것인가?
- **선택:** 사용자의 개인적인 변경 이해를 확인하고 넓히는 세션으로 둔다.
- **이유:** 결정 배경과 변경 기록은 spec, ADR, 이슈에 이미 남으므로 별도의 조직용 이해 산출물을 중복 생성할 필요가 없다.
- **구현상 결과:** 이해 산출물 등록부, 정답지, 점수와 blocking gate를 만들지 않는다. 이해 세션은 PR 작성의 선행 조건도 아니다.
- **spec 영향:** 있음. spec의 기존 이해 기능 설계를 수동 호출형 작업 이해 세션으로 교체했다.

### TA-13: 작업 이해 세션의 호출과 기록

- **질문:** 작업 이해 세션을 워크플로우에서 자동 실행할지, 사용자가 필요할 때 명시적으로 호출할지와 결과를 어디에 남길지 결정한다.
- **선택:** 사용자가 `understand-work`를 명시적으로 호출할 때만 실행하고, 질문·답변·피드백은 현재 대화에만 남긴다.
- **이유:** 사용자가 원하는 시점에 학습 비용을 선택하면서 별도 파일과 PR 절차의 결합을 피한다.
- **구현상 결과:** skill은 파일을 생성하거나 수정하지 않고 PR을 차단하지 않는다. 호출하지 않은 경우에도 필수 워크플로우는 그대로 진행한다.
- **spec 영향:** 있음. 선택형 수동 호출과 대화 내 기록 원칙을 spec에 반영했다.

### TA-14: 작업 이해 질문의 범위와 종료 조건

- **질문:** 실제 변경의 중요한 내용을 빠짐없이 다루면서 질문 수와 세션 종료를 어떻게 통제할 것인가?
- **선택:** 먼저 관련 근거의 핵심 주장을 전수 목록화한 뒤 유지보수 위험으로 우선순위를 정하고, 적용 가능한 다섯 축에서 최대 5문항을 선택해 모두 묻는다.
- **이유:** 중요한 변경을 놓치지 않되 주장마다 문항을 만드는 과도한 인터뷰를 피하고, agent의 조기 종료로 핵심 축이 생략되지 않게 한다.
- **구현상 결과:** 질문 축은 사양 설명, 구조·실행 흐름, 주요 결정·제약, 장애 진단·변경 위치, 검증·영향 범위다. 한 문항은 판단 하나만 요구하고, 답변에 따라 아직 묻지 않은 문항을 조정할 수 있지만 처음 선택한 총 문항 수를 늘리거나 전부 묻기 전에 종료할 수 없다.
- **spec 영향:** 있음. 최대 5문항의 적응형 세션 계약을 spec에 반영했다.

### TA-15: 사용자 명시적 실행 기능의 command 확장 경계

- **질문:** PR 생성이나 TDD 기반 구현처럼 사용자가 직접 실행할 기능을 나중에 구분된 command로 제공할 수 있도록 어떤 경계를 둘 것인가?
- **선택:** 기능마다 독립 skill을 정식 진입점으로 두고, Git 작업은 호스트 공통 command가 대응 skill 하나에 1:1로 위임하는 얇은 adapter로 만든다.
- **이유:** Codex와 Claude Code가 공유하는 동작 계약을 skill 한 곳에 유지하면서도 사용자가 필요한 단계만 분명한 command로 호출할 수 있다.
- **구현상 결과:** `implement-with-tdd`, `verify-test-sensitivity`, `understand-work`, `commit-changes`, `write-issue`, `post-git-comment`, `write-pr`를 분리하고 `orchestrate-work`는 개발 흐름에 필요한 기능만 조합한다. `git-commit`, `git-issue`, `git-comment`, `git-pr` command adapter에는 판단, provider 감지, 상태 전이, 검증 또는 문서 생성 로직을 두지 않는다. GitHub/GitLab 감지와 외부 쓰기 승인 게이트는 각 skill이 담당한다.
- **spec 영향:** 있음. 독립 실행 진입점과 향후 1:1 command adapter 원칙을 spec에 추가했다.

## 파일 구성

- `.codex-plugin/plugin.json`: Codex plugin identity, shared skills path, UI metadata.
- `.claude-plugin/plugin.json`: Claude Code plugin identity; default locations에서 skills/agents 자동 탐색.
- `skills/orchestrate-work/`: 규모 판정과 전체 상태 전이의 단일 진입점.
- `skills/orchestrate-work/references/invocation-contracts.md`: 독립 호출 가능한 skill ID, 책임, 진입 조건, 종료 결과와 향후 command 위임 규칙.
- `skills/setup-orchestration/`: 호스트 식별, 필수 의존성 검사, 대화형 설치 안내와 실행.
- `skills/orchestrate-work/references/work-scale.md`: 로컬 원본에서 채택한 규모 판정 기준과 출처.
- `skills/capture-authoring-voice/`: 인터뷰로 사용자 문체를 수집해 전역 프로파일 생성 및 갱신.
- `skills/decision-first-grill/`: spec 이전 사용자 결정 게이트.
- `skills/apply-conventions/`: 프로젝트 규칙 우선의 convention pack 선택.
- `skills/implement-with-tdd/`: 승인된 작업 기준을 읽고 superpowers TDD로 구현과 일반 검증을 수행하는 독립 진입점.
- `skills/verify-test-sensitivity/`: TDD 이후 임시 결함 주입과 복원 절차.
- `skills/understand-work/`: 실제 변경을 대상으로 수동 호출하는 최대 5문항 이해 세션.
- `skills/write-pr/`: 사용자가 선택한 코딩 에이전트에서 호출하는 플랫폼 중립 PR 작성 절차.
- `skills/*/agents/openai.yaml`: Codex skill picker용 표시 이름, 설명, 기본 프롬프트.
- `agents/*.md`: Claude Code용 전문가 agent.
- `adapters/codex/agents/*.toml`: Codex용 대응 custom agent 원본.
- `conventions/*.md`: 공통, clean code, React convention packs.
- `templates/*.md`: spec, 계획 기술 합의, 테스트 민감도, 문체 프로파일 계약.
- `scripts/validate_plugin.py`: manifest, skill, agent 대응, 링크, 금지 placeholder 검증.
- `scripts/mutation_guard.py`: mutation 대상 파일의 byte snapshot, SHA-256 확인과 정확한 복원.
- `scripts/install_codex_agents.py`: Codex agent를 대상 저장소 `.codex/agents/`에 설치.
- `tests/test_validate_plugin.py`: 구조 검증기 TDD.
- `tests/test_mutation_guard.py`: dirty 파일 snapshot, 복원, hash 불일치 동작 TDD.
- `tests/test_install_codex_agents.py`: 설치기의 생성/충돌 동작 TDD.
- `tests/fixtures/work-scale-cases.json`: 규모별 라우팅 수용 예시.
- `tests/test_contracts.py`: workflow/template 정적 계약 검증.

### 태스크 1: 양쪽 호스트용 플러그인 골격과 검증기

**파일:**
- Create: `.codex-plugin/plugin.json`
- Create: `.claude-plugin/plugin.json`
- Create: `scripts/validate_plugin.py`
- Create: `tests/test_validate_plugin.py`

- [ ] **1단계: 실패하는 manifest 검증 테스트 작성**

```python
# tests/test_validate_plugin.py
import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_plugin import validate_plugin


class ValidatePluginTests(unittest.TestCase):
    def test_requires_matching_dual_manifests(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".codex-plugin").mkdir()
            (root / ".claude-plugin").mkdir()
            (root / ".codex-plugin/plugin.json").write_text(
                json.dumps({"name": "agent-orchestration", "version": "0.1.0"}),
                encoding="utf-8",
            )
            (root / ".claude-plugin/plugin.json").write_text(
                json.dumps({"name": "different-name", "version": "0.1.0"}),
                encoding="utf-8",
            )

            errors = validate_plugin(root)

            self.assertIn("manifest names must match", errors)

    def test_repository_skeleton_is_valid(self):
        root = Path(__file__).parents[1]
        self.assertEqual([], validate_plugin(root))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **2단계: 테스트를 실행해 실패 확인**

실행: `python -m unittest tests.test_validate_plugin -v`

예상 결과: `ModuleNotFoundError: No module named 'scripts.validate_plugin'`.

- [ ] **3단계: 두 manifest 추가**

```json
// .codex-plugin/plugin.json (remove this comment in the real JSON file)
{
  "name": "agent-orchestration",
  "version": "0.1.0",
  "description": "코딩 에이전트를 위한 규모별 기획, 검증, 선택형 작업 이해, PR 워크플로우.",
  "skills": "./skills/",
  "interface": {
    "displayName": "Agent Orchestration",
    "shortDescription": "개발 작업의 라우팅, 검증, 설명, PR 준비",
    "developerName": "kkjuyeon",
    "category": "Developer Tools",
    "capabilities": ["Interactive", "Read", "Write"],
    "defaultPrompt": ["이 개발 작업을 규모에 맞는 워크플로우로 진행해 주세요."]
  }
}
```

```json
// .claude-plugin/plugin.json (remove this comment in the real JSON file)
{
  "name": "agent-orchestration",
  "version": "0.1.0",
  "description": "코딩 에이전트를 위한 규모별 기획, 검증, 선택형 작업 이해, PR 워크플로우.",
  "author": {
    "name": "kkjuyeon"
  }
}
```

- [ ] **4단계: 최소 검증기 구현**

```python
# scripts/validate_plugin.py
import json
import sys
from pathlib import Path


def validate_plugin(root: Path) -> list[str]:
    errors: list[str] = []
    manifests = []
    for relative_path in (
        Path(".codex-plugin/plugin.json"),
        Path(".claude-plugin/plugin.json"),
    ):
        path = root / relative_path
        if not path.is_file():
            errors.append(f"missing manifest: {relative_path.as_posix()}")
            continue
        try:
            manifests.append(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError as error:
            errors.append(f"invalid JSON in {relative_path.as_posix()}: {error.msg}")

    if len(manifests) == 2:
        if manifests[0].get("name") != manifests[1].get("name"):
            errors.append("manifest names must match")
        if manifests[0].get("version") != manifests[1].get("version"):
            errors.append("manifest versions must match")

    return errors


if __name__ == "__main__":
    failures = validate_plugin(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
    for failure in failures:
        print(failure)
    raise SystemExit(1 if failures else 0)
```

- [ ] **5단계: 검증기 테스트 실행**

실행: `python -m unittest tests.test_validate_plugin -v`

예상 결과: 두 테스트가 모두 통과한다.

- [ ] **6단계: 커밋**

```text
git add .codex-plugin .claude-plugin scripts/validate_plugin.py tests/test_validate_plugin.py
git commit -m "feat(plugin): add dual-host plugin skeleton"
```

### 태스크 2: 작업 규모 라우터와 워크플로우 상태 계약

**파일:**
- Create: `skills/orchestrate-work/SKILL.md`
- Create: `skills/orchestrate-work/references/workflow.md`
- Create: `skills/orchestrate-work/references/invocation-contracts.md`
- Create: `tests/fixtures/work-scale-cases.json`
- Create: `tests/test_contracts.py`
- Modify: `scripts/validate_plugin.py`

- [ ] **1단계: 실패하는 워크플로우 계약 테스트 작성**

```python
# tests/test_contracts.py
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]


class WorkflowContractTests(unittest.TestCase):
    def test_scale_cases_cover_small_medium_and_large(self):
        cases = json.loads(
            (ROOT / "tests/fixtures/work-scale-cases.json").read_text(encoding="utf-8")
        )
        self.assertEqual({"small", "medium", "large"}, {case["expected"] for case in cases})

    def test_router_contains_required_ordered_gates(self):
        text = (ROOT / "skills/orchestrate-work/references/workflow.md").read_text(
            encoding="utf-8"
        )
        gates = [
            "규모 판정",
            "범위 탐색",
            "의사결정",
            "spec 승인",
            "계획 기술 합의",
            "TDD 기반 구현",
            "테스트 민감도",
            "선택형 작업 이해",
            "PR 작성",
        ]
        positions = [text.index(f"## {gate}") for gate in gates]
        self.assertEqual(sorted(positions), positions)
```

- [ ] **2단계: 테스트를 실행해 fixture 부재로 실패하는지 확인**

실행: `python -m unittest tests.test_contracts -v`

예상 결과: `work-scale-cases.json` 또는 `workflow.md`에 대한 `FileNotFoundError`가 발생한다.

- [ ] **3단계: 라우팅 인수 사례 추가**

```json
[
  {
    "name": "단일 모듈의 결함 하나",
    "facts": {"kind": "bug", "files": 2, "independent_outputs": 1, "prs": 1},
    "expected": "small",
    "decision_grill": "only-if-ambiguous"
  },
  {
    "name": "하나의 완결된 기능",
    "facts": {"kind": "feature", "modules": 1, "independent_outputs": 1, "prs": 1},
    "expected": "medium",
    "decision_grill": "required"
  },
  {
    "name": "여러 모듈에 걸친 기능 배포",
    "facts": {"kind": "feature", "modules": 3, "independent_outputs": 3, "prs": 3},
    "expected": "large",
    "decision_grill": "required"
  }
]
```

- [ ] **4단계: 라우터 skill 초기화**

설치된 `skill-creator/scripts/init_skill.py`를 다음과 같이 실행한다.

```text
python "C:\Users\kkjuyeon\.codex\skills\.system\skill-creator\scripts\init_skill.py" orchestrate-work --path skills --resources references --interface display_name="작업 오케스트레이션" --interface short_description="개발 작업을 규모에 맞는 게이트로 라우팅" --interface default_prompt="이 개발 작업의 규모를 판정하고 적절한 워크플로우로 진행해 주세요."
```

예상 결과: `skills/orchestrate-work/SKILL.md`, `references/`, `agents/openai.yaml`이 생성된다. 다음 단계에서 생성된 placeholder를 모두 교체한다.

- [ ] **5단계: 라우터 skill 작성**

`skills/orchestrate-work/SKILL.md`에는 다음 제어 정책 전체가 포함되어야 한다.

```markdown
---
name: orchestrate-work
description: 기능 개발, 버그 수정, 리팩터링 등 개발 작업을 구현 전에 규모별로 분류하고 필요한 기획, 테스트와 선택형 작업 이해·PR 절차를 선택한다. 개발 작업을 시작하거나 적용할 워크플로우를 결정할 때 사용한다.
---

# 작업 오케스트레이션

`references/workflow.md`를 읽고 현재 게이트를 정확히 하나만 유지한다.

1. 예상 시간이 아니라 독립적으로 병합하고 검증할 수 있는 산출물을 기준으로 규모를 판정한다.
2. 소형 작업은 spec 결과에 영향을 주는 모호함이 남을 때만 의사결정 우선 그릴을 사용하고, 질문은 최대 두 개로 제한한다.
3. 중형과 대형 작업은 brainstorming에서 모든 실질적 spec 의사결정을 목록화하고, 의사결정 우선 그릴에서 사용자에게 하나씩 확정받은 뒤 spec 승인을 요구한다.
4. plan 작성 중 공동 합의가 필요한 구현 수준의 기술 선택은 선택지, 트레이드오프, 추천안과 함께 하나씩 사용자에게 묻는다. 완성된 plan 전체의 사용자 리뷰는 요구하지 않는다. spec 결정을 바꿔야 하면 spec 수정 단계로 돌아간다.
5. 구현은 독립 진입점 `implement-with-tdd`에 위임한다. 라우터가 TDD 절차를 복제하거나 직접 소유하지 않는다.
6. 일반 검증 후 새 테스트와 영향 범위의 기존 테스트에 `verify-test-sensitivity`를 실행한다.
7. 작업 이해 세션은 사용자가 `understand-work`를 명시적으로 호출할 때만 실행한다. 파일을 만들지 않고 PR을 포함한 다른 절차를 차단하지 않는다.
8. PR 작성은 사용자가 원하는 코딩 에이전트 세션에서 `write-pr` skill로 명시적으로 호출한다. 향후 slash command는 이 skill에만 위임한다.
9. 호출받은 에이전트는 승인된 spec, 실제 diff와 최종 검증 근거를 직접 읽고, 근거가 부족하면 중단한다.
10. 호출받은 에이전트가 PR 초안을 작성하고 외부 PR 생성 전 사용자 승인을 받는다.
11. spec, plan, PR 본문, 사용자 대면 질문과 선택지 문구를 쓰기 전에 문체 프로파일을 로드해 문체에 반영한다. 프로파일이 없으면 `capture-authoring-voice`로 1회 세팅할 수 있다고 한 번만 안내하고 기본 문체로 진행한다. 문체 프로파일 부재는 차단 사유가 아니다.

승인이 필요하거나 게이트가 실패하면 멈춘다. 부족한 근거를 보고하고 다음 단계로 임의 진행하지 않는다.
```

- [ ] **6단계: 순서가 명시된 워크플로우 reference 작성**

`skills/orchestrate-work/references/workflow.md`는 `규모 판정`, `범위 탐색`, `의사결정`, `spec 승인`, `계획 기술 합의`, `TDD 기반 구현`, `테스트 민감도`, `선택형 작업 이해`, `PR 작성` 순서로 제목을 두고 각 단계의 진입·종료 근거를 명시한다. `계획 기술 합의` 절에는 plan 작성 중 공동 합의가 필요한 구현 수준의 기술 선택을 하나씩 질문하고, 단순 세부사항은 agent가 정하며, spec 결정을 바꿔야 하면 spec 수정 단계로 돌아간다고 명시한다. 완성된 plan 자체의 사용자 리뷰는 요구하지 않는다. `TDD 기반 구현` 절은 `implement-with-tdd`에 위임하며 사용자가 이 skill만 직접 호출할 수도 있다고 명시한다. `선택형 작업 이해` 절에는 사용자가 `understand-work`를 명시적으로 호출할 때만 실행하고, 현재 대화에만 질문·답변·피드백을 남기며, 호출하지 않거나 답변이 부족해도 PR을 포함한 다른 절차를 차단하지 않는다고 명시한다. `PR 작성` 절에는 사용자 명시적 호출로만 시작하며, 선택한 코딩 에이전트가 별도 중간 문서 없이 spec, 실제 diff와 최종 검증 근거를 직접 읽는다고 명시한다. 문서와 질문 문구를 생성하는 모든 절에는 문체 프로파일을 로드해 문체 층위에서 플러그인 기본값보다 우선 적용하되, 프로파일 부재는 게이트가 아니며 내용 계약과 템플릿 고정 절 구조는 프로파일이 바꾸지 못한다고 명시한다.

`skills/orchestrate-work/references/invocation-contracts.md`에는 `implement-with-tdd`, `verify-test-sensitivity`, `understand-work`, `commit-changes`, `write-issue`, `post-git-comment`, `write-pr` 각각의 안정된 skill ID, 단일 책임, 필수 입력, 종료 결과와 수동 호출 정책을 기록한다. Git command는 행 하나의 skill에만 1:1로 위임하고 인자 전달 외의 로직을 갖지 않는다고 명시한다.

- [ ] **7단계: skill frontmatter와 UI metadata 검증 추가**

모든 `skills/*/SKILL.md`가 비어 있지 않은 `name`과 `description`을 가진 frontmatter를 포함하는지 검사한다. 각 skill의 `agents/openai.yaml`에 비어 있지 않은 `display_name`, `short_description`, `default_prompt`가 있는지도 검사한다. `invocation-contracts.md`가 `implement-with-tdd`, `verify-test-sensitivity`, `understand-work`, `write-pr`를 서로 다른 안정된 ID로 선언하고, 향후 command의 1:1 위임과 로직 금지 원칙을 포함하는지도 검사한다. manifest, skill, agent, adapter, convention, template에서 skill 초기화 placeholder token을 거부하되 승인된 spec/plan과 기존 루트 컨벤션 초안 3개는 검사 대상에서 제외한다. 범용 YAML parser를 만들지 말고 이 저장소가 쓰는 최상위 scalar field만 처리한다.

- [ ] **8단계: 계약 및 검증기 테스트 실행**

실행: `python -m unittest tests.test_contracts tests.test_validate_plugin -v`

예상 결과: 모든 테스트가 통과한다.

- [ ] **9단계: 커밋**

```text
git add skills/orchestrate-work scripts/validate_plugin.py tests
git commit -m "feat(workflow): route development work by scale"
```

### 태스크 3: 의사결정 우선 그릴과 기획 템플릿

**파일:**
- Create: `skills/decision-first-grill/SKILL.md`
- Create: `templates/spec.md`
- Create: `templates/plan-technical-alignment.md`
- Modify: `tests/test_contracts.py`

- [ ] **1단계: 실패하는 의사결정 게이트 테스트 작성**

`decision-first-grill/SKILL.md`에 실질적 spec 의사결정 전수 목록화, agent 기본값과 추정의 사용자 확인, 한 번에 한 질문, 상호 배타적인 선택지 2~3개, 트레이드오프, 추천안, 사용자 결정, 이유, 결정 coverage 확인, 결정 완료 전 spec 작성 금지, spec 작성 중 새 결정 발견 시 그릴 복귀가 모두 포함되는지 검사한다. `templates/spec.md`에는 `문제`, `목적`, `현재 구조와 제약`, `결정`, `비목표`, `완료 기준`이 포함되는지 검사한다. `templates/plan-technical-alignment.md`에는 기술 질문, 선택지와 트레이드오프, 추천안, 사용자 선택과 이유, 구현상 결과, spec 영향 여부가 포함되는지 검사한다.

- [ ] **2단계: 테스트를 실행해 실패 확인**

실행: `python -m unittest tests.test_contracts.WorkflowContractTests -v`

예상 결과: skill과 template가 없어 실패한다.

- [ ] **3단계: 의사결정 우선 skill 추가**

먼저 `init_skill.py decision-first-grill --path skills --interface display_name="의사결정 우선 그릴" --interface short_description="spec 작성 전 주요 설계 결정을 확정" --interface default_prompt="이 spec에 필요한 모든 실질적 의사결정을 목록화하고 하나씩 함께 확정해 주세요."`로 초기화한 뒤 생성된 placeholder를 모두 교체한다.

skill은 agent에게 다음 순서를 지시해야 한다.

```text
범위 확인 -> 실질적 spec 의사결정 전수 목록화 -> 후속 영향에 따라 우선순위 지정 -> 질문 하나 제시
-> 상호 배타적 선택지 2~3개와 트레이드오프 및 추천안 제시
-> 선택과 이유 기록 -> 목록화한 모든 실질적 의사결정이 확정될 때까지 반복
-> 의사결정 목록 coverage를 사용자와 확인 -> spec 작성 허용
```

중형/대형 작업에서는 필수로 적용하고 소형 작업에서는 모호할 때만 최대 두 질문의 단축형으로 적용한다. 대화에서 이미 드러난 미결정 사항뿐 아니라 agent가 기본값이나 추천안으로 대신 정하려는 항목도 범위, 외부 행위, 계약, 보안, 운영, 완료 기준 또는 PR 경계에 영향을 주면 질문 대상으로 포함한다. 쉽게 되돌릴 수 있는 내부 구현 세부 사항은 제외한다. spec 작성 중 새로운 실질적 결정이 발견되면 작성을 멈추고 그릴로 돌아간다. 결정은 spec과 이후 PR에 기록하고, `CONTEXT.md`에는 용어만 기록하며, domain-modeling의 세 조건을 모두 충족할 때만 ADR을 만든다. 질문 문구와 선택지 설명은 문체 프로파일이 있으면 그 문체로 쓰되, 한 문항에 판단 하나, 상호 배타적 선택지, 트레이드오프와 추천안 제시 같은 질문 구조는 문체가 아니라 계약이므로 프로파일이 바꾸지 못한다.

- [ ] **4단계: 완전한 템플릿 추가**

`templates/spec.md`에는 문제, 목적, 현재 구조/제약, 대안과 이유를 포함한 결정, 비목표, 실패/중단 조건, 완료 기준, 참고 자료의 고정 절을 둔다. `templates/plan-technical-alignment.md`에는 spec 결정 ID 참조, 기술 질문, 검토한 선택지와 트레이드오프, 추천안, 사용자 선택과 이유, 구현상 결과, spec 영향 여부를 기록한다. spec 영향이 `있음`이면 plan 작성을 중단하고 spec 수정으로 돌아가도록 안내한다. spec의 전체 결정 근거는 반복하지 않는다.

- [ ] **5단계: 테스트 실행**

실행: `python -m unittest tests.test_contracts -v`

예상 결과: 모든 의사결정 게이트 테스트가 통과한다.

- [ ] **6단계: 커밋**

```text
git add skills/decision-first-grill templates tests/test_contracts.py
git commit -m "feat(planning): add decision-first specification gate"
```

### 태스크 4: 컨벤션 팩 등록부

**파일:**
- Create: `skills/apply-conventions/SKILL.md`
- Create: `conventions/registry.json`
- Create: `conventions/general-coding.md`
- Create: `conventions/clean-code.md`
- Create: `conventions/react.md`
- Modify: `tests/test_contracts.py`

- [ ] **1단계: 실패하는 컨벤션 선택 테스트 작성**

등록부의 ID가 중복되지 않고 모든 참조 파일이 존재하며 우선순위가 `프로젝트 규칙 > 선택된 플러그인 팩 > 일반 기본값`인지 검사한다. `.tsx`는 `general`, `clean-code`, `react`를 선택하고 `.py`는 초기에는 `general`, `clean-code`만 선택하는 사례를 추가한다.

- [ ] **2단계: 테스트를 실행해 실패 확인**

실행: `python -m unittest tests.test_contracts -v`

예상 결과: 등록부가 없어 실패한다.

- [ ] **3단계: 구조화된 등록부 추가**

```json
{
  "precedence": ["project", "selected-pack", "general-default"],
  "packs": [
    {"id": "general", "path": "conventions/general-coding.md", "extensions": ["*"]},
    {"id": "clean-code", "path": "conventions/clean-code.md", "extensions": ["*"]},
    {"id": "react", "path": "conventions/react.md", "extensions": [".jsx", ".tsx"]}
  ]
}
```

- [ ] **4단계: 기존 컨벤션 메모를 팩으로 정리**

루트 초안 3개에서 실행 가능한 규칙만 새 팩으로 옮기고 중복된 루트 파일은 제거한다. 불확실한 초안 문장과 내용이 없는 제목은 필수 정책으로 만들지 말고 제외한다. 특히 경계 격리, 의미 있는 이름, 명령과 조회 분리, 부수 효과 제한, 가독성을 높이는 early return, 행위 중심 테스트, 작은 PR 범위, React에서 사용자 노출 오류와 내부 오류 구분을 유지한다.

- [ ] **5단계: 컨벤션 선택 skill 추가**

먼저 `init_skill.py apply-conventions --path skills --interface display_name="컨벤션 적용" --interface short_description="변경 스택에 맞는 컨벤션 선택" --interface default_prompt="이 변경에 관련된 프로젝트 및 플러그인 컨벤션 팩을 적용해 주세요."`로 초기화한 뒤 생성된 placeholder를 모두 교체한다.

skill은 먼저 프로젝트 지침과 변경 파일을 확인하고 일치하는 팩만 선택한다. 적용한 팩 ID를 plan과 PR 작성 근거에 기록하고 저장소 규칙이 플러그인 기본값보다 우선한다고 명시한다. 변경 코드가 해당 스택을 사용하지 않는데 사용자 선호만으로 React, Python, Java 규칙을 적용하면 안 된다.

- [ ] **6단계: 테스트 실행 및 커밋**

실행: `python -m unittest tests.test_contracts -v`

예상 결과: 모든 테스트가 통과한다.

```text
git add skills/apply-conventions conventions tests/test_contracts.py
git commit -m "feat(conventions): add stack-aware convention packs"
```

### 태스크 5: 독립 호출형 TDD 구현 진입점

**파일:**
- Create: `skills/implement-with-tdd/SKILL.md`
- Modify: `skills/orchestrate-work/SKILL.md`
- Modify: `skills/orchestrate-work/references/workflow.md`
- Modify: `tests/test_contracts.py`

- [ ] **1단계: 실패하는 TDD 구현 진입점 계약 테스트 작성**

`implement-with-tdd/SKILL.md`가 사용자 직접 호출과 `orchestrate-work` 위임을 모두 허용하는지 검사한다. skill은 승인된 spec과 해당되는 plan·계획 기술 합의를 구현 기준으로 읽고, 구현 전에 외부 `superpowers:test-driven-development`를 호출해야 한다. 책임 범위는 테스트 우선 구현과 원본 상태의 일반 검증까지이며 테스트 민감도 mutation, 작업 이해 질문, PR 작성 또는 PR 생성은 수행하지 않는다. 완료 시 실제 변경 범위, 일반 검증 명령과 결과, 다음 단계인 `verify-test-sensitivity`를 현재 세션에 보고해야 한다.

- [ ] **2단계: 테스트를 실행해 실패 확인**

실행: `python -m unittest tests.test_contracts -v`

예상 결과: `implement-with-tdd` skill이 없어 실패한다.

- [ ] **3단계: TDD 구현 skill 초기화**

먼저 `init_skill.py implement-with-tdd --path skills --interface display_name="TDD 기반 구현" --interface short_description="승인된 작업 기준을 테스트 우선으로 구현" --interface default_prompt="승인된 spec과 plan을 기준으로 TDD 방식으로 구현하고 일반 검증까지 수행해 주세요."`로 초기화한 뒤 생성된 placeholder를 모두 교체한다.

- [ ] **4단계: 단일 책임과 위임 계약 구현**

skill은 다음 순서를 강제한다.

```text
승인된 작업 기준 확인 -> 적용할 컨벤션 확인
-> `superpowers:test-driven-development` 호출
-> 실패 테스트 작성 및 실패 원인 확인
-> 최소 구현 -> 관련 테스트 통과
-> 영향 범위 리팩터링과 일반 검증
-> 변경 범위와 검증 근거 보고 -> `verify-test-sensitivity` 안내
```

직접 호출과 orchestrator 호출은 같은 절차를 사용한다. skill 본문에는 규모 판정, spec 의사결정, mutation, 이해 질문 또는 PR 로직을 복제하지 않는다. 필수 작업 기준이 없거나 spec 수준 결정이 미확정이면 구현하지 않고 `orchestrate-work` 또는 spec 수정 단계로 돌아가야 할 근거를 보고한다.

- [ ] **5단계: 라우터 위임과 독립 호출 계약 검증**

`orchestrate-work`가 구현 단계에서 `implement-with-tdd`를 호출하고 자체적으로 TDD 세부 절차를 반복하지 않는지 검사한다. `invocation-contracts.md`의 TDD 행과 skill의 진입 조건, 종료 결과, 다음 단계가 일치하는지도 검사한다.

- [ ] **6단계: 테스트 실행 및 커밋**

실행: `python -m unittest tests.test_contracts tests.test_validate_plugin -v`

예상 결과: 모든 테스트가 통과한다.

```text
git add skills/implement-with-tdd skills/orchestrate-work tests/test_contracts.py
git commit -m "feat(tdd): add independently invocable TDD implementation workflow"
```

### 태스크 6: 테스트 민감도 하네스

**파일:**
- Create: `skills/verify-test-sensitivity/SKILL.md`
- Create: `skills/verify-test-sensitivity/references/common.md`
- Create: `skills/verify-test-sensitivity/references/typescript-javascript.md`
- Create: `skills/verify-test-sensitivity/references/python.md`
- Create: `skills/verify-test-sensitivity/references/java.md`
- Create: `templates/test-sensitivity-evidence.md`
- Create: `scripts/mutation_guard.py`
- Create: `tests/test_mutation_guard.py`
- Modify: `tests/test_contracts.py`

- [ ] **1단계: 실패하는 하네스 계약 테스트 작성**

skill이 사용자 직접 호출과 `orchestrate-work` 위임을 모두 허용하고, 기준 상태 통과, 행위-테스트 연결, byte snapshot과 SHA-256 기록, mutation 하나 적용, 대상 테스트 실행, `killed`/`survived` 판정, snapshot 복구, hash 일치 확인, 복구 후 통과 순서의 상태 머신을 강제하는지 검사한다. `survived` mutation은 게이트 실패이며 근거에 mutation 위치, 결함을 잡아야 하는 테스트, 실행 명령, 관찰 결과, snapshot hash, 복구 hash와 결과가 포함되는지 검사한다. `tests/test_mutation_guard.py`는 미커밋 상태를 나타내는 임의 바이트를 snapshot한 뒤 파일을 변경하고 정확히 복원하는 경우와, 복원 검증에서 hash가 다르면 실패하는 경우를 포함한다.

- [ ] **2단계: 테스트를 실행해 실패 확인**

실행: `python -m unittest tests.test_contracts -v`

예상 결과: 하네스 파일과 mutation guard가 없어 실패한다.

- [ ] **3단계: mutation snapshot과 복원 helper 구현**

`scripts/mutation_guard.py`에 대상 경로의 원본 바이트와 SHA-256을 process 전용 임시 디렉터리에 저장하는 `snapshot(path)`와, 저장한 바이트를 원래 경로에 기록하고 hash 일치를 검사하는 `restore(snapshot)`을 구현한다. 원본이 아닌 경로에 복원하거나 snapshot이 없어진 경우를 거부한다. `git checkout`, `git restore` 또는 저장소 전체 reset은 사용하지 않는다.

- [ ] **4단계: mutation guard 테스트 실행**

실행: `python -m unittest tests.test_mutation_guard -v`

예상 결과: byte 보존, 복원, hash 불일치 테스트가 통과한다.

- [ ] **5단계: 하네스 skill 작성**

먼저 `init_skill.py verify-test-sensitivity --path skills --resources references --interface display_name="테스트 민감도 검증" --interface short_description="작은 행위 결함을 테스트가 감지하는지 확인" --interface default_prompt="의도한 행위를 작게 깨뜨렸을 때 영향 범위의 테스트가 실패하는지 검증해 주세요."`로 초기화한 뒤 생성된 placeholder를 모두 교체한다.

skill은 `implement-with-tdd` 또는 동등한 TDD 절차와 일반 검증이 완료됐다는 현재 변경 근거를 먼저 요구한다. 직접 호출과 orchestrator 호출은 같은 절차를 사용한다. mutation 검증 범위는 새로 작성한 테스트와 변경된 운영 행위를 다루는 기존 테스트로 제한한다. 저장소 전체 mutation, 여러 mutation 동시 적용, 테스트 코드 mutation을 주 검증으로 사용하는 것, worktree에 mutation이 남은 상태에서 완료하는 것을 금지한다.

- [ ] **6단계: mutation recipe 추가**

각 recipe에는 boolean 반전, 경계값 이동, 예외 제거, 필터 조건 완화, 상태 전이 생략에 대한 선택 지침과 구체적 예시를 둔다. 언어별 팩에는 다음의 관용적 예시만 추가한다.

- TypeScript/JavaScript: predicate inversion, rejected promise converted to resolve, optional guard removal.
- Python: comparison boundary, raised exception removal, filtered comprehension relaxation.
- Java: conditional inversion, validation exception removal, enum/state assignment omission.

컴파일 자체가 검증 대상 계약인 경우가 아니라면 컴파일이나 import 실패를 일으키지 않으면서 명시된 행위를 깨뜨리는 가장 작은 mutation을 선택하라고 모든 recipe에 명시한다.

- [ ] **7단계: 근거 템플릿 추가**

고정 필드는 검증 행위, 운영 코드 위치, 결함을 잡아야 하는 테스트, 기준 명령/결과, mutation, mutation 명령/결과, 판정(`killed` 또는 `survived`), 테스트 보강 변경, 복구 근거, 최종 명령/결과로 구성한다.

- [ ] **8단계: 테스트 실행 및 커밋**

실행: `python -m unittest tests.test_contracts -v`

예상 결과: 모든 하네스 계약 테스트가 통과한다.

```text
git add skills/verify-test-sensitivity templates/test-sensitivity-evidence.md scripts/mutation_guard.py tests/test_mutation_guard.py tests/test_contracts.py
git commit -m "feat(test): add test sensitivity verification harness"
```

### 태스크 7: 수동 호출형 작업 이해 세션과 양쪽 호스트용 agent

**파일:**
- Create: `skills/understand-work/SKILL.md`
- Create: `skills/understand-work/references/question-design.md`
- Create: `agents/work-question-designer.md`
- Create: `adapters/codex/agents/work-question-designer.toml`
- Modify: `scripts/validate_plugin.py`
- Modify: `tests/test_contracts.py`

- [ ] **1단계: 실패하는 작업 이해 세션 계약 테스트 작성**

`understand-work/SKILL.md`가 사용자 명시적 호출만 진입 조건으로 허용하는지 검사한다. 입력은 승인된 spec, 현재 실제 diff, 연결된 이슈·ADR·관련 문서이며, 질문 전에 실제 내용의 핵심 주장을 전수 목록화하고 유지보수 위험으로 우선순위를 정해야 한다. 질문은 최대 5개이고 `사양 설명`, `구조·실행 흐름`, `주요 결정·제약`, `장애 진단·변경 위치`, `검증·영향 범위` 중 적용 가능한 축을 사용하며 문항마다 판단 하나만 요구해야 한다.

또한 질문을 한 번에 하나씩 묻고 답변마다 평가, 설명과 근거 위치를 제공하는지 검사한다. 아직 묻지 않은 질문은 앞선 답변에 맞춰 조정할 수 있지만 총 문항 수를 늘리거나 선택한 문항을 전부 묻기 전에 자율 종료할 수 없어야 한다. 마지막에는 이해한 영역과 보완할 영역을 현재 대화에서만 요약하며 파일, 등록부, 정답지, 점수를 만들거나 PR을 차단하지 않는지 검사한다. Claude와 Codex agent 정의가 같은 논리 이름으로 존재하는지도 검사한다.

- [ ] **2단계: 테스트를 실행해 실패 확인**

실행: `python -m unittest tests.test_contracts tests.test_validate_plugin -v`

예상 결과: 작업 이해 skill과 agent 파일이 없어 실패한다.

- [ ] **3단계: 작업 이해 skill과 로컬 질문 규칙 추가**

먼저 `init_skill.py understand-work --path skills --resources references --interface display_name="작업 이해 세션" --interface short_description="현재 변경을 최대 5문항으로 이해" --interface default_prompt="현재 spec과 실제 diff를 바탕으로 이 변경에 대한 내 이해를 확인하고 넓혀 주세요."`로 초기화한 뒤 생성된 placeholder를 모두 교체한다.

출처를 표시하고 Adept의 실제 질문 설계 규칙을 plugin reference로 옮기되 이 세션 목적에 맞게 조정한다. 핵심 주장은 빠짐없이 목록화하지만 주장마다 질문을 하나씩 만들지 않는다. 상황 우선 질문, 응답 형태 일치, 문항당 판단 하나, 회상 질문 금지, 대부분 성공 가능한 난이도, 사람 간 순위 비교 금지를 불변식으로 유지한다.

skill 흐름은 다음과 같아야 한다.

```text
사용자 명시적 호출 -> 승인된 spec, 실제 diff, 연결된 이슈·ADR·관련 문서 읽기
-> 핵심 주장 전수 목록화 -> 유지보수 위험 순위와 질문 축 연결
-> 최대 5문항 선택 -> 한 문항 질문
-> 답변 평가, 공백 설명, 근거 위치 제시
-> 남은 문항을 총수 한도 안에서 조정 -> 선택한 문항을 모두 질문
-> 현재 대화에 이해한 영역과 보완할 영역 요약
```

- [ ] **4단계: 동등한 플랫폼별 agent 추가**

Claude의 `agents/work-question-designer.md`와 Codex TOML은 모두 읽기 전용으로 둔다. 실제 근거에서 먼저 핵심 주장을 목록화하고 위험 순위를 매긴 뒤 최대 5개 질문 후보와 축을 반환하도록 지시한다. 파일을 생성하거나 수정하지 않고 어느 adapter에도 model을 고정하지 않는다.

- [ ] **5단계: agent 대응 관계 검증 추가**

모든 `agents/{name}.md`에 대응하는 `adapters/codex/agents/{name}.toml`이 있도록 요구하고, `tomllib`으로 TOML의 `name`, `description`, `developer_instructions`를 검증한다.

- [ ] **6단계: 테스트 실행 및 커밋**

실행: `python -m unittest tests.test_contracts tests.test_validate_plugin -v`

예상 결과: 모든 테스트가 통과한다.

```text
git add skills/understand-work agents adapters scripts/validate_plugin.py tests
git commit -m "feat(knowledge): add manual work understanding session"
```

### 태스크 8: Codex agent 설치기

**파일:**
- Create: `scripts/install_codex_agents.py`
- Create: `tests/test_install_codex_agents.py`

- [ ] **1단계: 실패하는 설치기 테스트 작성**

```python
# tests/test_install_codex_agents.py
import tempfile
import unittest
from pathlib import Path

from scripts.install_codex_agents import install_agents


class InstallCodexAgentsTests(unittest.TestCase):
    def test_installs_agents_without_overwriting_existing_files(self):
        with tempfile.TemporaryDirectory() as source_dir, tempfile.TemporaryDirectory() as target_dir:
            source = Path(source_dir)
            target = Path(target_dir)
            (source / "reviewer.toml").write_text('name = "reviewer"\n', encoding="utf-8")
            destination = target / ".codex/agents"
            destination.mkdir(parents=True)
            (destination / "reviewer.toml").write_text("user-owned", encoding="utf-8")

            result = install_agents(source, target)

            self.assertEqual(["reviewer.toml"], result.conflicts)
            self.assertEqual("user-owned", (destination / "reviewer.toml").read_text(encoding="utf-8"))
```

- [ ] **2단계: 테스트를 실행해 실패 확인**

실행: `python -m unittest tests.test_install_codex_agents -v`

예상 결과: `ModuleNotFoundError`가 발생한다.

- [ ] **3단계: 덮어쓰지 않는 명시적 설치 구현**

`installed`와 `conflicts` 목록을 가진 `install_agents(source: Path, project: Path) -> InstallResult`를 구현한다. `*.toml`을 `project / ".codex/agents"`로 복사하고 필요한 디렉터리를 만들며, 대상이 디렉터리가 아니면 거부하고 기존 파일은 절대 덮어쓰지 않는다. CLI smoke test는 `python scripts/install_codex_agents.py --project .`로 실행하며 충돌이 있으면 목록을 출력하고 종료 코드 2를 반환한다.

- [ ] **4단계: 설치와 충돌 보존 동작 테스트**

실행: `python -m unittest tests.test_install_codex_agents -v`

예상 결과: 설치 및 충돌 테스트가 통과한다.

- [ ] **5단계: 커밋**

```text
git add scripts/install_codex_agents.py tests/test_install_codex_agents.py
git commit -m "feat(codex): install project-scoped custom agents safely"
```

### 태스크 9: 수동 호출형 플랫폼 중립 PR 작성

**파일:**
- Create: `skills/write-pr/SKILL.md`
- Modify: `tests/test_contracts.py`

- [ ] **1단계: 실패하는 PR 계약 테스트 작성**

`write-pr/SKILL.md`가 사용자 명시적 호출을 진입 조건으로 요구하는지 검사한다. 호출받은 에이전트는 승인된 spec과 현재 저장소의 실제 diff를 직접 확인하고, 현재 diff를 기준으로 일반 검증과 테스트 민감도 검증을 다시 실행해야 한다. 검증이 실패하거나 실행할 수 없으면 중단하고, 별도 중간 문서를 만들지 않으며, 특정 호스트나 agent를 PR 작성자로 고정하지 않는지도 검사한다. `understand-work` 실행 여부나 결과에 의존하지 않고 한국어 제목과 본문 초안을 먼저 제시하며, 외부 PR 생성 전에 사용자 승인을 받는지도 검사한다.

- [ ] **2단계: 테스트를 실행해 실패 확인**

실행: `python -m unittest tests.test_contracts -v`

예상 결과: 공통 PR 작성 skill이 없어 실패한다.

- [ ] **3단계: 플랫폼 중립 PR 작성 skill 추가**

먼저 `init_skill.py write-pr --path skills --interface display_name="PR 작성" --interface short_description="spec, diff, 검증 근거로 PR 초안 작성" --interface default_prompt="승인된 spec, 실제 diff, 최종 검증 근거를 확인하고 이 변경의 한국어 PR 초안을 작성해 주세요."`로 초기화한 뒤 생성된 placeholder를 모두 교체한다.

skill은 Codex, Claude Code 또는 같은 Agent Skills 형식을 지원하는 다른 코딩 에이전트에서 동일하게 동작한다. orchestrator가 자동으로 실행하거나 다른 세션을 열지 않으며, 사용자가 skill을 직접 호출하거나 `git-pr` command를 호출할 때만 시작한다. command는 이 skill을 1:1로 호출하며 별도 PR 로직을 갖지 않는다.

- [ ] **4단계: PR 근거 확인과 작성 절차 구현**

skill은 다음 순서를 강제한다.

1. 승인된 spec을 읽고 문제 배경, 목적, 비목표, 결정과 이유를 추출한다.
2. 현재 저장소의 실제 diff를 직접 읽고 변경 범위와 리뷰 포인트를 추출한다.
3. 저장소 지침과 plan에서 최종 검증 명령을 식별하고 현재 diff에 대해 일반 검증을 다시 실행한다.
4. `verify-test-sensitivity`를 다시 실행해 현재 테스트가 의도한 결함에 민감한지 확인하고 임시 mutation을 정확히 복원한다.
5. 일반 검증이나 테스트 민감도 검증이 실패하거나 실행할 수 없으면 PR 작성을 중단한다.
6. 문체 프로파일을 로드한다. 있으면 각 축을 PR 제목과 본문 문체에 적용하고, 없으면 기본 문체로 진행하며 차단하지 않는다.
7. 시간순 작업 로그나 폐기한 시행착오 대신 최종 상태 중심의 한국어 PR 제목과 본문을 작성한다. 문체는 프로파일을 따르되, 명령 근거 없이 테스트 결과를 주장하지 않고 결정과 구현 세부를 구분한다는 내용 계약은 프로파일과 무관하게 유지한다.
8. 제목과 본문을 사용자에게 보여주고 명시적 승인이 있을 때만 외부 PR을 생성한다.

- [ ] **5단계: 호스트 중립성 검증**

skill 본문에 특정 호스트 전용 호출, 호스트 간 자동 인계, 플랫폼별 PR writer agent 의존성이 없는지 검사한다. 호스트가 제공하는 git 또는 PR 도구 이름이 다르면 해당 호스트의 동등한 도구를 사용하되 근거 확인과 사용자 승인 계약은 동일하게 유지한다.

- [ ] **6단계: 테스트 실행 및 커밋**

실행: `python -m unittest tests.test_contracts tests.test_validate_plugin -v`

예상 결과: 모든 테스트가 통과한다.

```text
git add skills/write-pr tests
git commit -m "feat(pr): add manually invoked cross-host PR workflow"
```

### 태스크 10: 문체 페르소나 수집과 소비

**파일:**
- Create: `skills/capture-authoring-voice/SKILL.md`
- Create: `skills/capture-authoring-voice/references/voice-axes.md`
- Create: `templates/voice-profile.md`
- Modify: `skills/orchestrate-work/SKILL.md`
- Modify: `skills/orchestrate-work/references/workflow.md`
- Modify: `skills/decision-first-grill/SKILL.md`
- Modify: `skills/implement-with-tdd/SKILL.md`
- Modify: `skills/understand-work/SKILL.md`
- Modify: `skills/write-pr/SKILL.md`
- Modify: `tests/test_contracts.py`

- [ ] **1단계: 실패하는 문체 계약 테스트 작성**

`templates/voice-profile.md`에 고정 축 10개 제목이 모두 있는지 검사한다. `capture-authoring-voice/SKILL.md`에 한 번에 한 질문, 축 전수 질문, 미응답 축 `미정` 유지, 추정으로 채우기 금지, 저장 전 샘플 PR 검증 루프, 사용자 승인 후 저장, 경로 규약 `AGENT_ORCHESTRATION_HOME`과 `~/.agent-orchestration/voice-profile.md`가 모두 있는지 검사한다. 문체 우선순위 문구와, 내용 계약 및 템플릿 고정 절 구조는 프로파일 대상이 아니라는 문구가 있는지도 검사한다. `orchestrate-work`, `decision-first-grill`, `implement-with-tdd`, `understand-work`, `write-pr`가 모두 프로파일을 로드하고 부재 시 차단하지 않는다고 명시하는지 검사한다. 저장 경로가 저장소 밖이므로 실제 파일 존재는 검사하지 않고 경로 규약이 문서에 명시됐는지만 검사한다.

- [ ] **2단계: 테스트를 실행해 실패 확인**

실행: `python -m unittest tests.test_contracts -v`

예상 결과: 문체 skill과 템플릿이 없어 실패한다.

- [ ] **3단계: 문체 수집 skill 초기화**

먼저 `init_skill.py capture-authoring-voice --path skills --resources references --interface display_name="문체 페르소나 수집" --interface short_description="인터뷰로 사용자 문체를 수집해 전역 프로파일 생성" --interface default_prompt="내 문체 페르소나를 인터뷰로 만들어 주세요."`로 초기화한 뒤 생성된 placeholder를 모두 교체한다.

- [ ] **4단계: 고정 축 reference 작성**

`references/voice-axes.md`에 축 10개를 두고 축마다 질문 문구, 상호 배타적 선택지 예시 2~3개, 프로파일에 기록할 값 형식을 명시한다. 축은 문장 길이와 호흡, 어미와 경어체, PR 최상단 내용과 섹션 순서, 비유 허용 범위, 기술용어 원어 유지 정도, 불확실성 표현법, 금지 표현, 강조 수단, 코드와 명령 인용 밀도, 독자 가정이다. 선택지는 예시이며 사용자가 자유 응답으로 대체할 수 있다고 명시한다.

- [ ] **5단계: 수집 skill 작성**

skill은 다음 순서를 강제한다.

```text
기존 프로파일 확인 -> 있으면 갱신할 축만 선택, 없으면 전체 진행
-> 축 전수 목록 제시 -> 한 번에 한 질문
-> 미응답 축은 `미정`으로 기록하고 추정으로 채우지 않는다
-> 초안 프로파일로 짧은 PR 본문 1편 생성해 제시
-> 사용자 확인: 맞으면 저장 단계로, 아니면 어긋난 축만 재질문 후 재생성
-> 사용자 승인 후에만 전역 경로에 저장
```

저장 경로는 `$AGENT_ORCHESTRATION_HOME/voice-profile.md`이고 미설정 시 `~/.agent-orchestration/voice-profile.md`다. Codex와 Claude Code가 홈 경로가 다르므로 호스트별 skill 디렉터리에 저장하지 않는다. 기존 파일을 덮어쓰기 전에 사용자 승인을 받고, 갱신하지 않기로 한 축의 기존 값은 보존한다.

- [ ] **6단계: 프로파일 템플릿 추가**

`templates/voice-profile.md`에 축 10개의 고정 절을 두고, 각 절에 `값`과 선택적 `사용자 원문 예시`를 둔다. 문서 끝에 `미정 축` 목록 절을 둔다. 프로파일은 문체만 기술하며 내용 계약이나 템플릿 절 구조를 기술하지 않는다고 머리말에 명시한다.

- [ ] **7단계: 소비 지점 수정**

`orchestrate-work/SKILL.md` 통제 정책 11번, `references/workflow.md`의 문서 생성 절, `decision-first-grill/SKILL.md`, `implement-with-tdd/SKILL.md`, `understand-work/SKILL.md`의 사용자 대면 문구 규칙, `write-pr/SKILL.md`의 본문 작성 절차에 프로파일 로드와 우선순위, 부재 시 비차단 규칙을 반영한다. 어느 파일에도 문체 지침을 문자열로 다시 박지 않는다.

- [ ] **8단계: 테스트 실행 및 커밋**

실행: `python -m unittest tests.test_contracts tests.test_validate_plugin -v`

예상 결과: 모든 테스트가 통과한다.

```text
git add skills/capture-authoring-voice templates/voice-profile.md skills/orchestrate-work skills/decision-first-grill skills/implement-with-tdd skills/understand-work skills/write-pr tests/test_contracts.py
git commit -m "feat(voice): capture authoring voice profile for spec, plan, and PR"
```

### 태스크 11: 교차 플랫폼 인수 검증

**파일:**
- Create: `tests/acceptance/cases.md`
- Create: `tests/acceptance/expected.md`
- Modify: `scripts/validate_plugin.py`

- [ ] **1단계: 대표 인수 prompt 추가**

소형 버그, 모호한 소형 리팩터링, 중형 기능, 대형 교차 모듈 기능, 두 호스트에서 각각 `implement-with-tdd`만 직접 호출하는 사례, `verify-test-sensitivity`만 직접 호출하는 사례, `survived` mutation, 작업 이해 세션을 호출하지 않는 사례, Codex와 Claude Code에서 각각 `understand-work`를 수동 호출하는 사례, 두 호스트에서 각각 수동 호출하는 PR 작성 사례, 문체 프로파일이 있는 상태의 중형 기능 사례, 문체 프로파일이 없는 상태의 중형 기능 사례를 포함한다. 각 사례에는 예상 내부 답변이 아니라 사용자에게 보이는 작업 맥락만 제공한다. 모든 사용자 prompt는 한국어로 작성한다.

- [ ] **2단계: 예상 관찰 결과 추가**

각 사례에 관찰 가능한 게이트, 필수 질문, 금지된 생략, 예상 산출물, 중단 조건을 정의한다. 독립 호출 사례는 전체 orchestrator를 시작하지 않고 해당 skill의 단일 책임만 수행한 뒤 계약에 명시된 다음 단계를 안내해야 한다. 작업 이해 세션 사례는 사용자 호출이 없으면 실행되지 않고, 호출하면 실제 근거를 바탕으로 선택한 최대 5문항을 한 번에 하나씩 모두 물으며, 파일을 만들거나 PR을 차단하지 않는 것을 관찰 결과로 둔다. Git 커맨드 사례는 host command 파일이 `invocation-contracts.md`의 1:1 adapter 계약대로 단일 skill에 위임하고, provider 미감지 시 외부 쓰기를 하지 않으며, 외부 쓰기 전에는 승인을 요구하는 것을 관찰 결과로 둔다. 문체 사례의 예상 결과는 프로파일이 있으면 PR 초안이 프로파일 축을 따르고 플러그인 기본 문체를 쓰지 않는 것, 프로파일이 없으면 1회 안내 후 차단 없이 진행하는 것이다. forward test 중 정답이 유출되지 않도록 예상 결과는 prompt와 분리한다.

- [ ] **3단계: 모든 결정론적 테스트 실행**

실행: `python -m unittest discover -s tests -v`

예상 결과: 모든 unit 및 계약 테스트가 통과한다.

- [ ] **4단계: 플러그인 검증기 실행**

실행: `python scripts/validate_plugin.py .`

예상 결과: 출력 없이 종료 코드 0을 반환한다.

`plugin-creator`가 제공하는 Codex plugin validator를 이 저장소에 실행한다.

예상 결과: `.codex-plugin/plugin.json`과 참조된 skills가 유효하다.

실행: `claude --plugin-dir .`

예상 결과: Claude Code가 namespaced skills와 `work-question-designer` agent를 표시한 상태로 시작한다. 외부 작업은 실행하지 않고 종료한다.

- [ ] **5단계: 새 세션에서 두 호스트 forward test**

새 Codex 및 Claude Code 세션에서 소형과 중형 prompt를 실행한다. 각 호스트에서 `implement-with-tdd`, `verify-test-sensitivity`, `understand-work`, `write-pr`를 각각 직접 호출해 전체 orchestrator 없이도 자신의 책임만 수행하는지 검증한다. `understand-work`는 최대 5문항 계약을 지키고, `write-pr`은 이해 세션과 독립적으로 같은 근거 확인 절차를 거쳐 PR 초안을 작성해야 한다. worker agent에게 예상 결과 파일을 보여주지 않고 `tests/acceptance/expected.md`의 관찰 결과를 확인한다. 불일치만 기록하고 관련 skill을 수정한 뒤 실패한 사례를 다시 실행한다. 두 호스트 모두 질문과 사용자 대면 산출물을 한국어로 반환하는지도 확인한다.

- [ ] **6단계: 최종 diff와 범위 검증**

실행: `git diff --check`

예상 결과: 공백 오류가 없다.

실행: `git status --short`

예상 결과: plugin 구현, 테스트, `CONTEXT.md`, 승인된 설계/계획 문서만 변경되고 기존 루트 컨벤션 초안은 convention pack으로 이전된 뒤 제거된다.

- [ ] **7단계: 커밋**

```text
git add tests/acceptance scripts/validate_plugin.py
git commit -m "test(plugin): verify cross-host orchestration workflows"
```

## 계획 검토 체크리스트

- 승인된 spec의 모든 초기 완료 기준이 태스크 1~11에 연결된다.
- 플랫폼 중립 skill은 단일 원본을 사용하고 manifest와 agent 형식만 중복한다.
- TDD 구현, 테스트 민감도, 작업 이해, PR 작성은 각각 독립 skill이며 `orchestrate-work`는 세부 절차를 복제하지 않는다.
- Git command는 skill 하나에만 1:1로 위임하고 provider 감지나 업무 로직을 갖지 않는다.
- 계획에 자동 mutation runner가 포함되지 않는다.
- 작업 이해 세션은 사용자 명시적 호출로만 실행하며, 파일이나 등록부를 만들지 않고 PR을 차단하지 않는다.
- 작업 이해 질문은 실제 근거의 핵심 주장을 전수 목록화한 뒤 위험 순으로 최대 5개를 선택하고, 선택한 문항은 한 번에 하나씩 모두 묻는다.
- plan 작성 중 공동 합의가 필요한 기술 선택은 하나씩 질문하며, 완성된 plan 전체는 사용자 승인 대상이 아니다.
- PR 작성자는 사용자가 호출한 코딩 에이전트이며, 외부 PR 생성은 사용자 승인을 요구한다.
- 기존 컨벤션 초안의 실행 가능한 규칙은 팩으로 정리하고 중복 루트 파일은 제거한다.
- 사용자 질문과 spec, plan, PR, 이해 질문은 기본적으로 한국어로 작성한다.
- 문체는 skill과 agent에 문자열로 박지 않고 전역 프로파일 하나에서만 온다. 프로파일 부재는 차단 사유가 아니며, 내용 계약과 템플릿 고정 절 구조는 프로파일이 바꾸지 못한다.
