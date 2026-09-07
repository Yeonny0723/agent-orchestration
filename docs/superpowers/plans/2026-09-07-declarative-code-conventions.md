# 선언적 코드·설명·YAGNI 컨벤션 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 선언적 코드 작성, YAGNI 기반 과설계 검토, 사용자 요청 시 쉬운 설명, Python의 근거 없는 오류 처리 생성을 공통·언어별 컨벤션에 명확히 반영한다.

**Architecture:** 공통 동작 기준은 `conventions/general.md`에 둔다. 기존 언어별 집계 규칙의 G10은 공통 규칙과 겹치는 부분만 예외를 명시하고, Python 오류 처리 생성 제한은 `conventions/python/python-clean-code.md`에 둔다. 계약 테스트는 각 문구가 유지되는지 확인하며 registry 구조는 변경하지 않는다.

**Tech Stack:** Markdown convention packs, Python `unittest`, `scripts/validate_plugin.py`

---

### Task 1: 컨벤션 계약 테스트 추가

**Files:**
- Modify: `tests/test_contracts.py:452-512`
- Test: `tests/test_contracts.py`

- [x] **Step 1: 선언적 코드·YAGNI·설명·오류 처리 문구를 요구하는 실패 테스트를 추가한다**

`ConventionContractTests`에 다음 테스트를 추가한다.

```python
    def test_general_pack_declares_intent_driven_code_and_yagni_rules(self):
        text = read("conventions/general.md")
        for phrase in (
            "코드만 읽어서는 의도를 파악하기 어려운 표현",
            "여러 조건이나 도메인 판단이 결합된 표현",
            "JSX, `if`, 함수 인자에 긴 표현식을 직접 넣지 않는다",
            "단순한 표현식이나 일회성 별칭까지 과도하게 추출하지 않는다",
            "현재 지원해야 하는 시나리오인지 확인한다",
            "실패 가능성이 현실적인지 확인한다",
            "단순 방어 코드인지 실제 요구사항인지 구분한다",
            "미래 확장용 추상화",
            "사용하지 않는 옵션·분기·DTO 필드",
            "const isActiveUser = user.status === \"ACTIVE\";",
            "is_active = user.is_active",
        ):
            self.assertIn(phrase, text)

    def test_general_pack_preserves_delivery_explanation_exception(self):
        text = read("conventions/general.md")
        self.assertIn("장황한 설명이나 자체 비유 대신 정확한 도메인 용어", text)
        self.assertIn("왜 이렇게 되는지 12살한테 설명하듯 알려줘", text)
        self.assertIn("사용자가 복잡한 설명을 명시적으로 요청한 경우", text)

    def test_language_pack_g10_allows_intent_extraction_exception(self):
        expected = (
            "일반 변수는 사용 위치 가까이에 선언한다. "
            "단, 의도를 설명하기 위해 추출한 변수는 코드 흐름과 개념 단위가 더 잘 드러나는 위치에 둘 수 있다."
        )
        for path in (
            "conventions/python/python-clean-code.md",
            "conventions/typescript/typescript-clean-code.md",
        ):
            self.assertIn(expected, read(path))

    def test_python_pack_limits_speculative_error_handling(self):
        text = read("conventions/python/python-clean-code.md")
        for phrase in (
            "요구사항이나 기존 계약에 근거한 오류만 구현한다",
            "임의의 오류 코드",
            "커스텀 예외",
            "범용 `try/except`",
            "추가 validator",
            "예상치 못한 오류를 조용히 삼키거나",
        ):
            self.assertIn(phrase, text)
```

- [x] **Step 2: 새 테스트가 현재 문서에서 실패하는지 확인한다**

Run: `python -m unittest tests.test_contracts.ConventionContractTests -v`

Expected: FAIL because the new convention phrases and the G10 exception do not exist yet.

### Task 2: 공통 컨벤션에 선언적 코드·YAGNI·설명 규칙 반영

**Files:**
- Modify: `conventions/general.md:70-73,117`

- [x] **Step 1: 기존 조건·반복 항목을 선언적 코드와 의도 표현 항목으로 확장한다**

기존 두 bullet을 다음 내용으로 교체한다.

```markdown
### 선언적 코드와 의도 표현

- 코드만 읽어서는 의도를 파악하기 어려운 표현은 의미 있는 변수나 함수로 추출한다.
- 여러 조건이나 도메인 판단이 결합된 표현은 Boolean 판단 변수나 판단 함수로 추출한다. 예를 들어 `isinstance(...)` 같은 조건이 길게 반복되면 `is_table_replacement`처럼 판단 의도를 표현한다.
- 의미 있는 연산은 이름 있는 함수나 변수로 표현한다.
- JSX, `if`, 함수 인자에 긴 표현식을 직접 넣지 않는다.
- 단순한 표현식이나 일회성 별칭까지 과도하게 추출하지 않는다.
- 추출한 변수의 위치는 사용처와의 거리보다 코드 흐름과 개념적 응집성을 기준으로 정한다.
- 복잡한 comprehension은 중간 변수로 풀어 쓴다. 여러 반복문과 조건이 결합되면 입력, 선택 기준, 결과가 각각 드러나도록 단계별 변수와 구문으로 분리한다.
```

- [x] **Step 2: YAGNI 기반 과설계 리뷰 기준을 추가한다**

`선언적 코드와 의도 표현` 다음에 다음 항목을 추가한다.

```markdown
### 과설계와 YAGNI

- 현재 지원해야 하는 시나리오인지 확인한다.
- 실패 가능성이 현실적인지 확인한다.
- 단순 방어 코드인지 실제 요구사항인지 구분한다.
- 발생 확률이 매우 낮은 예외 케이스, 미래 확장용 추상화, 사용하지 않는 옵션·분기·DTO 필드, production에 불필요한 호환·중복 검증 코드는 제거 후보로 둔다.
```

- [x] **Step 3: 공통 규칙에 React와 Python 대표 예시를 추가한다**

`선언적 코드와 의도 표현` 항목의 규칙 아래에 다음 예시를 추가한다.

````markdown
#### React

```tsx
const isActiveUser = user.status === "ACTIVE";
const canEdit = permissions.includes("WRITE");

if (isActiveUser && canEdit) {
  return <EditButton />;
}

const isSelected = selected.includes(item.id);
const nextSelected = isSelected
  ? selected.filter(id => id !== item.id)
  : [...selected, item.id];

setSelected(nextSelected);
```

#### Python

```python
is_active = user.is_active
can_write = "write" in user.permissions
can_update = is_active and can_write

if can_update:
    update()
```
````

- [x] **Step 4: 복잡한 설명 요청을 기존 전달 규칙의 예외로 명시한다**

기존 전달 규칙을 다음 두 bullet로 교체한다.

```markdown
- 일반적인 코드·PR 전달에서는 장황한 설명이나 자체 비유 대신 정확한 도메인 용어를 사용한다.
- 사용자가 복잡한 설명을 명시적으로 요청한 경우에는 “왜 이렇게 되는지 12살한테 설명하듯 알려줘”를 기준으로 쉬운 말, 단계적 설명과 필요한 예시를 사용한다.
```

### Task 3: 언어별 G10과 Python 오류 처리 규칙 반영

**Files:**
- Modify: `conventions/python/python-clean-code.md:34`
- Modify: `conventions/typescript/typescript-clean-code.md:34`
- Modify: `conventions/python/python-clean-code.md:116-127`

- [x] **Step 1: Python과 TypeScript의 G10을 의도 설명용 변수 예외와 함께 수정한다**

두 파일의 G10을 다음 한 줄로 교체한다.

```markdown
- G10: 일반 변수는 사용 위치 가까이에 선언한다. 단, 의도를 설명하기 위해 추출한 변수는 코드 흐름과 개념 단위가 더 잘 드러나는 위치에 둘 수 있다
```

- [x] **Step 2: Python 팩의 에이전트 행동 규칙 앞에 오류 처리 생성 제한을 추가한다**

`## 에이전트 행동 규칙` 직전에 다음 절을 추가한다.

```markdown
## 오류 처리와 과잉 생성 제한

- 요구사항이나 기존 계약에 근거한 오류만 구현한다.
- 임의의 오류 코드, 커스텀 예외, 범용 `try/except`, 추가 validator와 호환성 처리 코드를 만들지 않는다.
- 예상치 못한 오류를 조용히 삼키거나 근거 없이 다른 오류로 변환하지 않는다.
- 실제로 지원해야 하는 입력 경계와 실패 경로의 검증은 생략하지 않는다.
```

- [x] **Step 3: 언어별 집계 규칙의 기존 G16·G19·G28과 새 공통 규칙이 중복 설명을 만들지 않는지 확인한다**

새 규칙을 언어별 집계 파일에 복제하지 않고, G16·G19·G28·N1이 공통 규칙을 보강하는 기존 요약으로 유지되는지 확인한다.

### Task 4: 전체 검증

**Files:**
- Verify: `tests/test_contracts.py`
- Verify: `scripts/validate_plugin.py`
- Verify: `conventions/registry.json`

- [x] **Step 1: 컨벤션 계약 테스트를 실행한다**

Run: `python -m unittest tests.test_contracts.ConventionContractTests -v`

Expected: all convention contract tests pass.

- [x] **Step 2: 전체 테스트를 실행한다**

Run: `python -m unittest discover -s tests -v`

Expected: all tests pass.

- [x] **Step 3: plugin 구조 검증을 실행한다**

Run: `python scripts/validate_plugin.py .`

Expected: validator succeeds without registry or metadata errors.

- [x] **Step 4: diff와 문서 중복을 확인한다**

Run: `git diff --check; rg -n "사용 위치 가까이|12살|YAGNI|임의의 오류 코드|복잡한 조건" conventions/general.md conventions/python/python-clean-code.md conventions/typescript/typescript-clean-code.md`

Expected: no whitespace errors; G10 includes the approved exception; new rules appear in their intended files; no separate declarative pack is added.

- [x] **Step 5: 변경 상태를 보고한다**

Report the modified files, test commands, validator result, and any remaining ambiguity. Do not add a new error abstraction, convention pack, or unrelated refactor.
