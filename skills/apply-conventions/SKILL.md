---
name: apply-conventions
description: 구현 또는 코드 리뷰에서 변경 파일의 언어와 프레임워크에 맞는 프로젝트 규칙과 플러그인 convention pack을 선택해야 할 때 사용한다.
---

# 컨벤션 적용

1. 저장소의 `AGENTS.md`, `CLAUDE.md`, `CONTEXT.md`, `UBIQUITOUS_LANGUAGE.md`, `docs/glossary/`와 프로젝트별 convention 문서를 먼저 읽는다.
2. 변경 파일과 실제 사용 기술을 식별한다.
3. plugin root의 `conventions/registry.json`에서 일치하는 pack만 선택한다.
4. 우선순위는 프로젝트 규칙, 선택된 plugin pack, 일반 기본값 순이다.
5. 용어집의 canonical term을 코드 네이밍에 적용하고, 적용한 pack ID와 충돌 시 선택한 상위 규칙을 plan 또는 PR 검증 근거에 기록한다.

`.tsx` 변경에는 general, typescript, react pack을 적용할 수 있다. Python 변경에 사용자 선호만으로 React 규칙을 적용하지 않는다. 프로젝트 규칙을 plugin 기본값으로 덮어쓰지 않는다.

## Python 공통

- 파일은 도메인이나 기능의 응집도를 유지하도록 구성한다.
- `constants.py`, `exceptions.py`처럼 파일 역할을 나타내는 이름을 사용하되,
  이름만으로 역할이 분명하지 않은 새 모듈에는 한 줄 docstring을 추가한다.
- 함수와 상수 이름은 동작과 의미를 드러내도록 작성한다.
- import는 모듈 상단에 둔다. 의존 방향과 응집도를 고려해 모듈을 나누고,
  순환 import는 구조 문제의 신호로 다룬다.

## FastAPI / Pydantic

- 외부 HTTP 입력과 출력은 Pydantic 모델로 정의한다.
- DTO 이름에는 도메인과 용도를 드러낸다.
  예: `CreateUserRequestDTO`, `UserResponseDTO`
- 여러 DTO가 실제로 공유하는 도메인 필드로는 `Base<Domain>DTO`를 만든다.
- 검증 책임은 입력 파싱, DTO 제약, 도메인 규칙, 저장소 제약의 경계에 둔다.
  동일한 규칙을 불필요하게 반복하지 않으며, 각 경계에 필요한 검증은 유지한다.
- FastAPI Best Practices 문서는 참고하되, 프로젝트의 버전·구조·기존 관례에 맞는 항목만 적용한다.
