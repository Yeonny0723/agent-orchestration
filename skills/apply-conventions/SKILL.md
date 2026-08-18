---
name: apply-conventions
description: 구현 또는 코드 리뷰에서 변경 파일의 언어와 프레임워크에 맞는 프로젝트 규칙과 플러그인 convention pack을 선택해야 할 때 사용한다.
---

# 컨벤션 적용

1. 저장소의 `AGENTS.md`, `CLAUDE.md`, `CONTEXT.md`와 프로젝트별 convention 문서를 먼저 읽는다.
2. 변경 파일과 실제 사용 기술을 식별한다.
3. plugin root의 `conventions/registry.json`에서 일치하는 pack만 선택한다.
4. 우선순위는 프로젝트 규칙, 선택된 plugin pack, 일반 기본값 순이다.
5. 적용한 pack ID와 충돌 시 선택한 상위 규칙을 plan 또는 PR 검증 근거에 기록한다.

`.tsx` 변경에는 general, typescript, react pack을 적용할 수 있다. Python 변경에 사용자 선호만으로 React 규칙을 적용하지 않는다. 프로젝트 규칙을 plugin 기본값으로 덮어쓰지 않는다.
