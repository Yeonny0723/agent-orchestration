# Optional authoring skills implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 사용자 검토 대상 글을 공통 skill에서 작성하고, 선택형 `stop-slop`·`humanizer` 규칙과 문체 프로파일을 적용하며, TDD 구현 전에 convention pack을 확정한다.

**Architecture:** 새 `author-reviewable-text` skill이 spec, plan, Git 초안과 `understand-work` 질문의 작성 계약을 소유한다. 호출 skill은 사실, 필수 형식과 산출물 종류를 제공하며 공통 skill은 설치된 외부 작성 스킬과 선택형 문체 프로파일을 읽어 최종 초안을 한 번 생성한다. `implement-with-tdd`는 별도 책임으로 `apply-conventions`를 먼저 호출한 뒤 TDD를 시작한다.

**Tech Stack:** Markdown Agent Skills, YAML skill metadata, Python `unittest` 계약 테스트, Skills CLI, Codex·Claude Code plugin manifests

---

## 파일 구조

새 파일:

- `skills/author-reviewable-text/SKILL.md`: 적용 대상, 입력 계약, 선택형 외부 스킬 호출, 우선순위와 오류 처리를 정의한다.
- `skills/author-reviewable-text/agents/openai.yaml`: Codex UI metadata를 제공한다.

수정 파일:

- `skills/decision-first-grill/SKILL.md`: spec을 제시하기 전에 공통 작성 skill을 호출한다.
- `skills/orchestrate-work/SKILL.md`: plan을 저장하기 전에 공통 작성 skill을 호출하고 직접 문체 로딩을 제거한다.
- `skills/write-issue/SKILL.md`: Issue 승인 초안에 공통 작성 skill을 적용한다.
- `skills/post-git-comment/SKILL.md`: 코멘트 승인 초안에 공통 작성 skill을 적용한다.
- `skills/write-pr/SKILL.md`: PR·MR 승인 초안에 공통 작성 skill을 적용하고 직접 문체 로딩을 제거한다.
- `skills/understand-work/SKILL.md`: 각 질문을 보여주기 전에 공통 작성 skill을 적용하되 피드백에는 적용하지 않는다.
- `skills/implement-with-tdd/SKILL.md`: 직접 문체 로딩을 제거하고 `apply-conventions`를 TDD보다 먼저 호출한다.
- `skills/setup-orchestration/SKILL.md`: `stop-slop`, `humanizer`를 선택형 설치 항목으로 제공한다.
- `tests/test_contracts.py`: 새 skill, 호출 범위, 선택형 설치와 convention 순서를 계약으로 고정한다.
- `tests/acceptance/cases.md`: 작성 스킬 설치 조합과 질문 적용 사례를 추가한다.
- `tests/acceptance/expected.md`: 선택형 동작과 convention 적용 예상 결과를 추가한다.
- `README.md`: 공통 작성 skill, 선택형 설치와 convention 적용을 설명한다.
- `.codex-plugin/plugin.json`: plugin 버전을 `0.1.2`로 올린다.
- `.claude-plugin/plugin.json`: plugin 버전을 `0.1.2`로 올린다.
- `.claude-plugin/marketplace.json`: marketplace와 plugin entry 버전을 `0.1.2`로 맞춘다.

`templates/voice-profile.md`와 `skills/capture-authoring-voice/`는 형식과 저장 책임이 바뀌지 않으므로 수정하지 않는다. `skills/commit-changes/SKILL.md`도 적용 제외 계약을 유지하므로 수정하지 않는다.

### Task 1: `author-reviewable-text` skill 추가

**Files:**
- Modify: `tests/test_contracts.py`
- Create: `skills/author-reviewable-text/SKILL.md`
- Create: `skills/author-reviewable-text/agents/openai.yaml`
- Test: `tests/test_contracts.py`

- [ ] **Step 1: 새 skill의 실패 계약 테스트를 작성한다**

`SkillContractTests.test_required_skills_have_metadata`의 `required` 집합에 `author-reviewable-text`를 추가한다. `SkillContractTests`에 다음 테스트를 추가한다.

```python
    def test_author_reviewable_text_preserves_content_contract(self):
        authoring = read("skills/author-reviewable-text/SKILL.md")
        for phrase in (
            "최종 초안을 한 번",
            "stop-slop",
            "humanizer",
            "선택형",
            "차단하지 않는다",
            "사용자의 명시적 지시",
            "필수 형식",
            "확인된 사실",
        ):
            self.assertIn(phrase, authoring)
```

- [ ] **Step 2: 테스트가 skill 부재로 실패하는지 확인한다**

Run:

```powershell
python -m unittest tests.test_contracts.SkillContractTests.test_required_skills_have_metadata tests.test_contracts.SkillContractTests.test_author_reviewable_text_preserves_content_contract -v
```

Expected: `skills/author-reviewable-text/SKILL.md`와 metadata가 없어 ERROR 또는 FAIL.

- [ ] **Step 3: 공통 작성 skill을 생성한다**

`skills/author-reviewable-text/SKILL.md`를 다음 내용으로 만든다.

```markdown
---
name: author-reviewable-text
description: spec, plan, Issue, 코멘트, PR·MR 또는 understand-work 질문처럼 사용자 검토 대상 글을 사실과 형식을 보존하며 작성할 때 사용한다.
---

# 검토 대상 글 작성

## 입력 계약

호출한 skill에서 산출물 종류, 필수 템플릿과 길이 제한, 포함할 확인된 사실과 사용자 지시를 받는다. 근거가 부족하면 내용을 추정하지 않고 부족한 입력을 호출한 skill에 반환한다.

## 작성 준비

1. `$AGENT_ORCHESTRATION_HOME/voice-profile.md`를 확인하고 환경 변수가 없으면 `~/.agent-orchestration/voice-profile.md`를 확인한다.
2. 프로파일이 없거나 읽을 수 없으면 기본 한국어 문체로 계속하며 작성을 차단하지 않는다.
3. 사용자 범위에 설치된 선택형 `humanizer`, `stop-slop`을 확인하고 설치된 skill만 호출한다.
4. 선택형 skill이 없거나 호출에 실패하면 이름과 원인을 보고하고 나머지 규칙으로 계속한다.

## 우선순위

충돌 시 사용자의 명시적 지시, 산출물의 필수 형식과 길이 제한, 확인된 사실과 근거, 문체 프로파일, `humanizer`, `stop-slop`, 기본 한국어 문체 순으로 적용한다. 낮은 순위의 규칙이 높은 순위의 의미나 형식을 바꾸면 적용하지 않는다.

## 작성

1. 준비한 규칙을 처음부터 반영해 최종 초안을 한 번 작성한다.
2. 필수 절, 사실, 수치, 파일명, 명령어와 길이 제한을 확인한다.
3. 문제가 발견된 부분만 고치며 초안 전체를 반복 재작성하지 않는다.
4. 호출한 skill에 최종 초안을 반환한다. 승인과 외부 쓰기는 호출한 skill이 담당한다.

## 적용 경계

spec, plan, Issue 제목과 본문, Issue·PR·MR 코멘트, PR·MR 제목과 본문, `understand-work` 질문에 적용한다. 커밋 메시지, 일반 진행 질문, 코드, 테스트, 로그, 명령어, 구현·검증 결과와 `understand-work` 답변 피드백에는 적용하지 않는다.
```

- [ ] **Step 4: Codex UI metadata를 생성한다**

`skills/author-reviewable-text/agents/openai.yaml`을 다음 내용으로 만든다.

```yaml
interface:
  display_name: "검토 대상 글 작성"
  short_description: "사용자 문체와 선택형 작성 규칙으로 승인 대상 초안을 생성"
  default_prompt: "확인된 사실과 필수 형식을 유지해 사용자 검토용 초안을 작성해 주세요."
```

- [ ] **Step 5: 새 skill 계약 테스트가 통과하는지 확인한다**

Run:

```powershell
python -m unittest tests.test_contracts.SkillContractTests.test_required_skills_have_metadata tests.test_contracts.SkillContractTests.test_author_reviewable_text_preserves_content_contract -v
```

Expected: 2 tests PASS.

- [ ] **Step 6: 새 skill과 계약 테스트를 함께 커밋한다**

```powershell
git add tests/test_contracts.py skills/author-reviewable-text
git commit -m "feat: 검토 대상 글 작성 스킬 추가"
```

### Task 2: 적용 대상 skill을 공통 작성 계약에 연결

**Files:**
- Modify: `skills/decision-first-grill/SKILL.md`
- Modify: `skills/orchestrate-work/SKILL.md`
- Modify: `skills/write-issue/SKILL.md`
- Modify: `skills/post-git-comment/SKILL.md`
- Modify: `skills/write-pr/SKILL.md`
- Modify: `skills/understand-work/SKILL.md`
- Modify: `skills/implement-with-tdd/SKILL.md`
- Test: `tests/test_contracts.py`

- [ ] **Step 1: 호출 범위와 voice profile 중앙화 실패 테스트를 작성한다**

기존 `test_voice_profile_is_shared_by_user_facing_skills`를 다음 테스트로 교체한다.

```python
    def test_reviewable_text_authoring_is_centralized_and_scoped(self):
        included = (
            "decision-first-grill",
            "orchestrate-work",
            "write-issue",
            "post-git-comment",
            "write-pr",
            "understand-work",
        )
        for name in included:
            text = read(f"skills/{name}/SKILL.md")
            self.assertEqual(1, text.count("author-reviewable-text"), name)

        for name in ("commit-changes", "implement-with-tdd"):
            self.assertNotIn("author-reviewable-text", read(f"skills/{name}/SKILL.md"), name)

        direct_voice_readers = {
            path.parent.name
            for path in (ROOT / "skills").glob("*/SKILL.md")
            if "voice-profile.md" in path.read_text(encoding="utf-8")
        }
        self.assertEqual(
            {"author-reviewable-text", "capture-authoring-voice"},
            direct_voice_readers,
        )
```

- [ ] **Step 2: 테스트가 기존 분산 구조 때문에 실패하는지 확인한다**

Run:

```powershell
python -m unittest tests.test_contracts.SkillContractTests.test_reviewable_text_authoring_is_centralized_and_scoped -v
```

Expected: 적용 대상 skill에 공통 호출이 없고 여러 skill이 `voice-profile.md`를 직접 읽어 FAIL.

- [ ] **Step 3: spec과 plan 작성 지점을 연결한다**

`skills/decision-first-grill/SKILL.md`의 `## 문체` 절을 제거하고 다음 절을 추가한다.

```markdown
## spec 작성

모든 결정이 확정된 뒤 `author-reviewable-text`에 spec 템플릿, 결정 근거와 사용자 지시를 전달해 최종 초안을 작성한다. 반환된 spec을 사용자에게 제시하고 승인을 받는다. 공통 작성 skill은 질문 루프의 선택지나 판단 계약에는 적용하지 않는다.
```

`skills/orchestrate-work/SKILL.md`의 `## 문체` 절을 제거하고 다음 절을 추가한다.

```markdown
## plan 작성

계획 기술 합의가 끝나면 `author-reviewable-text`에 plan 형식, 승인된 spec과 확정된 기술 결정을 전달해 저장할 최종 plan을 작성한다. plan 전체를 사용자 승인 게이트로 만들지는 않는다.
```

- [ ] **Step 4: Git 초안 작성 지점을 연결한다**

`skills/write-issue/SKILL.md`의 `## 초안 작성`에서 승인 단계 직전에 다음 항목을 추가한다.

```markdown
7. 제목과 본문을 제시하기 전에 `author-reviewable-text`에 선택한 템플릿, 확인된 사실, 제목과 본문 필수 항목을 전달해 최종 초안을 작성한다.
```

`skills/post-git-comment/SKILL.md`의 `## 초안과 승인` 3번 앞에 다음 항목을 넣고 이후 번호를 조정한다.

```markdown
3. 사용자가 제공한 원문의 의미와 확정된 사실을 입력으로 `author-reviewable-text`를 호출해 게시할 최종 초안을 작성한다.
```

`skills/write-pr/SKILL.md`의 `## 작성과 provider 감지`에서 직접 `voice-profile.md`를 읽는 1번을 다음 내용으로 교체하고 이후 항목 번호를 유지한다.

```markdown
1. 승인된 spec, 실제 diff, 검증 결과와 PR 템플릿을 `author-reviewable-text`에 전달해 한국어 제목과 본문 최종 초안을 작성한다.
```

- [ ] **Step 5: `understand-work` 질문만 연결한다**

`skills/understand-work/SKILL.md`의 `## 문체` 절을 제거한다. `## 진행`의 질문 제시 단계 앞에 다음 절을 추가한다.

```markdown
## 질문 작성

선정한 각 질문을 사용자에게 보여주기 전에 판단 대상, 관련 근거와 질문 길이 제약을 `author-reviewable-text`에 전달한다. 반환된 문구를 질문에 사용하되 판단 하나만 묻는 계약은 유지한다. 답변 뒤의 기술적 피드백, 근거 설명과 마지막 이해 요약에는 공통 작성 skill을 적용하지 않는다.
```

- [ ] **Step 6: 구현 보고에서 기존 직접 문체 로딩을 제거한다**

`skills/implement-with-tdd/SKILL.md`의 `## 문체` 절 전체를 삭제한다. 이 작업에서는 convention 호출 순서를 아직 바꾸지 않는다.

- [ ] **Step 7: 공통 작성 계약 테스트가 통과하는지 확인한다**

Run:

```powershell
python -m unittest tests.test_contracts.SkillContractTests.test_reviewable_text_authoring_is_centralized_and_scoped -v
```

Expected: PASS.

- [ ] **Step 8: 호출 지점 변경과 테스트를 커밋한다**

```powershell
git add tests/test_contracts.py skills/decision-first-grill/SKILL.md skills/orchestrate-work/SKILL.md skills/write-issue/SKILL.md skills/post-git-comment/SKILL.md skills/write-pr/SKILL.md skills/understand-work/SKILL.md skills/implement-with-tdd/SKILL.md
git commit -m "feat: 검토 대상 글 작성을 공통 계약으로 통합"
```

### Task 3: 선택형 외부 스킬 설치 계약 추가

**Files:**
- Modify: `tests/test_contracts.py`
- Modify: `skills/setup-orchestration/SKILL.md`
- Test: `tests/test_contracts.py`

- [ ] **Step 1: 선택형 설치 계약의 실패 테스트를 작성한다**

`SkillContractTests`에 다음 테스트를 추가한다.

```python
    def test_setup_offers_optional_authoring_skills_without_blocking(self):
        text = read("skills/setup-orchestration/SKILL.md")
        for dependency in ("stop-slop", "humanizer"):
            self.assertIn(dependency, text)
        for command in (
            "npx skills add hardikpandya/stop-slop --global --skill stop-slop",
            "npx skills add blader/humanizer --global --skill humanizer",
        ):
            self.assertIn(command, text)
        for phrase in (
            "선택형",
            "둘 다 선택하지",
            "자동 업데이트하지 않는다",
            "작업을 차단하지 않는다",
            "다른 원본",
        ):
            self.assertIn(phrase, text)
        for path in (
            "skills/setup-orchestration/SKILL.md",
            "skills/author-reviewable-text/SKILL.md",
        ):
            self.assertNotIn("unslop", read(path), path)
```

- [ ] **Step 2: 테스트가 선택형 설치 문구 부재로 실패하는지 확인한다**

Run:

```powershell
python -m unittest tests.test_contracts.SkillContractTests.test_setup_offers_optional_authoring_skills_without_blocking -v
```

Expected: `stop-slop` 또는 `humanizer` 문구를 찾지 못해 FAIL.

- [ ] **Step 3: setup skill에 필수와 선택형 의존성을 분리한다**

`skills/setup-orchestration/SKILL.md`의 절차를 다음 계약으로 갱신한다.

```markdown
## 필수 의존성

사용자 범위에서 `superpowers`, `grill-with-docs`, `domain-modeling`을 각각 검사한다. 누락된 필수 항목은 설치 위치, 명령과 변경 범위를 보여주고 항목별 승인을 받는다. 승인되지 않은 필수 항목은 설치 미완료로 보고한다.

## 선택형 작성 보조 스킬

`stop-slop`, `humanizer`의 설치 상태와 원본을 확인하고 사용자가 원하는 항목만 선택하게 한다. 둘 다, 하나만 또는 둘 다 선택하지 않는 결정을 허용한다. 선택하지 않은 항목은 설치하지 않으며 workflow 작업을 차단하지 않는다.

설치 명령은 다음과 같다.

```powershell
npx skills add hardikpandya/stop-slop --global --skill stop-slop
npx skills add blader/humanizer --global --skill humanizer
```

설치 전 원본 URL, 대상 경로와 명령을 보여주고 항목별 승인을 받는다. 설치할 때 최신 `main`을 사용하며 기존 설치를 자동 업데이트하지 않는다. 사용자가 명시적으로 업데이트를 요청했을 때만 별도 승인 후 갱신한다.

같은 이름과 같은 원본이면 설치 완료로 판단한다. 같은 이름이 다른 원본을 가리키거나 대상 경로가 기대한 skill 링크가 아니면 덮어쓰지 않고 충돌을 보고한다.
```

기존 단일 원본, junction·symbolic link, 충돌 시 중단, marketplace 등록과 최종 상태 보고 규칙은 유지한다. `설치 후 각 workflow 실행 때 의존성을 반복 검사하지 않는다`는 금지 문구는 필수 의존성의 설치 절차를 반복하지 않는다는 뜻으로 좁힌다. `author-reviewable-text`는 현재 세션에서 사용할 수 있는 선택형 작성 skill만 확인하며 설치나 업데이트를 실행하지 않는다.

- [ ] **Step 4: setup 관련 계약 테스트를 실행한다**

Run:

```powershell
python -m unittest tests.test_contracts.SkillContractTests.test_setup_is_interactive_and_never_overwrites_conflicts tests.test_contracts.SkillContractTests.test_setup_offers_optional_authoring_skills_without_blocking -v
```

Expected: 2 tests PASS.

- [ ] **Step 5: 선택형 설치 변경을 커밋한다**

```powershell
git add tests/test_contracts.py skills/setup-orchestration/SKILL.md
git commit -m "feat: 작성 보조 스킬 선택 설치 지원"
```

### Task 4: TDD 전에 convention 적용을 보장

**Files:**
- Modify: `tests/test_contracts.py`
- Modify: `skills/implement-with-tdd/SKILL.md`
- Test: `tests/test_contracts.py`

- [ ] **Step 1: 호출 순서 계약의 실패 테스트를 작성한다**

`SkillContractTests`에 다음 테스트를 추가한다.

```python
    def test_tdd_applies_conventions_before_test_driven_development(self):
        text = read("skills/implement-with-tdd/SKILL.md")
        self.assertIn("apply-conventions", text)
        self.assertLess(
            text.index("apply-conventions"),
            text.index("superpowers:test-driven-development"),
        )
        for phrase in ("프로젝트 규칙", "새로운 언어", "다시 확인"):
            self.assertIn(phrase, text)
```

- [ ] **Step 2: 테스트가 명시적 호출 부재로 실패하는지 확인한다**

Run:

```powershell
python -m unittest tests.test_contracts.SkillContractTests.test_tdd_applies_conventions_before_test_driven_development -v
```

Expected: `apply-conventions`를 찾지 못해 FAIL.

- [ ] **Step 3: `implement-with-tdd` 실행 순서를 갱신한다**

진입 조건 3번의 모호한 확인 문구를 제거한다. `## 실행`을 다음 순서로 바꾼다.

```markdown
## 실행

1. `apply-conventions`를 호출해 프로젝트 규칙과 변경 대상의 언어·프레임워크에 맞는 convention pack을 선택한다.
2. 선택한 pack과 충돌 시 우선한 프로젝트 규칙을 구현 입력으로 유지한다.
3. 외부 `superpowers:test-driven-development`를 호출한다.
4. 한 행위를 설명하는 실패 테스트를 먼저 작성한다.
5. 테스트를 실행해 구현 부재 또는 결함 때문에 실패하는지 확인한다.
6. 통과에 필요한 최소 구현을 작성한다.
7. 관련 테스트를 통과시킨 뒤 중복과 이름을 정리한다.
8. 구현 중 새로운 언어 또는 프레임워크 파일이 범위에 들어오면 `apply-conventions`로 적용 pack을 다시 확인한다.
9. 변경 영향 범위의 일반 검증을 실행한다.
10. 실제 변경 범위, 적용한 pack, 검증 명령과 결과를 현재 세션에 보고한다.
11. 다음 독립 단계로 `verify-test-sensitivity`를 안내한다.
```

`## 책임 경계`에는 convention 선택 로직을 복제하지 않고 `apply-conventions`에 위임한다는 문장을 추가한다.

- [ ] **Step 4: TDD 진입점 계약 테스트를 실행한다**

Run:

```powershell
python -m unittest tests.test_contracts.SkillContractTests.test_tdd_entrypoint_delegates_without_crossing_boundaries tests.test_contracts.SkillContractTests.test_tdd_applies_conventions_before_test_driven_development -v
```

Expected: 2 tests PASS.

- [ ] **Step 5: convention 연결을 커밋한다**

```powershell
git add tests/test_contracts.py skills/implement-with-tdd/SKILL.md
git commit -m "feat: TDD 전에 코드 컨벤션 적용"
```

### Task 5: 사용자 문서, 인수 사례와 plugin 버전 갱신

**Files:**
- Modify: `README.md`
- Modify: `tests/acceptance/cases.md`
- Modify: `tests/acceptance/expected.md`
- Modify: `.codex-plugin/plugin.json`
- Modify: `.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Test: `tests/test_contracts.py`
- Test: `tests/test_validate_plugin.py`

- [ ] **Step 1: 인수 사례에 작성 보조 조합과 convention 기대 동작을 추가한다**

`tests/acceptance/cases.md`의 `## 문체 프로파일`을 `## 검토 대상 글 작성`으로 바꾸고 다음 사례를 둔다.

```markdown
## 검토 대상 글 작성

### 작성 보조 스킬 없음

"stop-slop과 humanizer가 없는 환경에서 voice profile 없이 중형 기능 spec을 작성해 줘."

### 하나만 설치

"humanizer만 설치된 환경에서 PR 초안을 작성해 줘."

### 둘 다 설치

"stop-slop과 humanizer가 설치되고 voice profile이 있는 환경에서 plan을 작성해 줘."

### 작업 이해 질문

"작성 보조 스킬이 설치된 상태에서 understand-work를 진행해 줘. 질문과 답변 피드백의 적용 범위를 구분해 줘."
```

`tests/acceptance/expected.md`의 대응 절을 다음으로 바꾼다.

```markdown
## 검토 대상 글 작성

- 외부 작성 보조 스킬이 없어도 기본 한국어 문체로 산출물을 작성한다.
- 설치된 `stop-slop`, `humanizer`만 사용하며 미설치 항목을 반복 권유하지 않는다.
- voice profile이 있으면 외부 작성 규칙보다 우선하되 사실과 필수 형식을 바꾸지 않는다.
- `understand-work` 질문에는 공통 작성 계약을 적용하고 답변 피드백에는 적용하지 않는다.
- `implement-with-tdd`는 TDD를 시작하기 전에 `apply-conventions`를 호출한다.
```

- [ ] **Step 2: README에 새 동작을 설명한다**

`README.md`의 독립 skill 목록 아래에 내부 작성 helper인 `author-reviewable-text` 설명을 별도 문단으로 추가한다. 독립 실행 진입점으로 소개하지 않는다. 설치와 의존성 절에서 세 필수 의존성과 별도로 다음 선택형 항목을 설명한다.

```markdown
사용자 검토 대상 글에는 선택형 작성 보조 스킬을 사용할 수 있습니다.

- `stop-slop`
- `humanizer`

둘 다, 하나만 또는 설치하지 않는 구성을 허용합니다. 설치된 항목만 spec, plan, Issue, 코멘트, PR·MR과 `understand-work` 질문 작성에 사용합니다. 커밋 메시지와 구현 결과에는 적용하지 않습니다.
```

`implement-with-tdd` 설명에는 `apply-conventions`를 먼저 호출한다고 명시한다.

- [ ] **Step 3: plugin 버전을 `0.1.2`로 맞춘다**

다음 값을 모두 `0.1.2`로 변경한다.

```text
.codex-plugin/plugin.json -> version
.claude-plugin/plugin.json -> version
.claude-plugin/marketplace.json -> top-level version
.claude-plugin/marketplace.json -> plugins[0].version
```

- [ ] **Step 4: 인수 문서와 manifest 계약 테스트를 실행한다**

Run:

```powershell
python -m unittest tests.test_contracts.AcceptanceContractTests tests.test_validate_plugin.ValidatePluginTests -v
```

Expected: 모든 테스트 PASS.

- [ ] **Step 5: 문서와 버전 변경을 커밋한다**

```powershell
git add README.md tests/acceptance/cases.md tests/acceptance/expected.md .codex-plugin/plugin.json .claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "docs: 선택형 작성 워크플로우 안내 추가"
```

### Task 6: 전체 검증과 민감도 확인

**Files:**
- Verify: `tests/test_contracts.py`
- Verify: `scripts/validate_plugin.py`
- Verify: all changed files

- [ ] **Step 1: 전체 단위 테스트를 실행한다**

Run:

```powershell
python -m unittest discover -s tests -v
```

Expected: exit code 0, 모든 테스트 PASS.

- [ ] **Step 2: plugin 구조 검증을 실행한다**

Run:

```powershell
python scripts/validate_plugin.py .
```

Expected: exit code 0, 출력 없음.

- [ ] **Step 3: diff와 placeholder를 검사한다**

Run:

```powershell
git diff --check
rg -n "TBD|TODO|\[TODO|미정" skills tests README.md .codex-plugin .claude-plugin
```

Expected: `git diff --check` 출력 없음. `rg`는 새 변경에 placeholder가 없으며, 기존 문맥상 의도된 문자열만 있으면 해당 위치를 직접 검토한다.

- [ ] **Step 4: 계약 테스트 민감도를 확인한다**

`verify-test-sensitivity`를 호출해 `skills/understand-work/SKILL.md`의 `author-reviewable-text` 참조를 임시로 제거한다. `test_reviewable_text_authoring_is_centralized_and_scoped`가 실패하는지 확인한 뒤 byte snapshot과 SHA-256으로 원본을 정확히 복원한다.

Expected: mutation은 `killed`, 복원 전후 hash 일치, 복원 후 대상 테스트 PASS.

- [ ] **Step 5: 최종 상태를 확인한다**

Run:

```powershell
git status --short
git log --oneline -7
```

Expected: 계획에 포함되지 않은 변경이 없고, Task별 커밋이 현재 branch에 순서대로 존재한다.
