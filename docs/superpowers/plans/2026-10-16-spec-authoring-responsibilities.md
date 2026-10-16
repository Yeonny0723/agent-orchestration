# Spec 작성 책임 분리 Implementation Plan

> 승인 근거: 사용자가 템플릿·완성 샘플·다이어그램 지침·파이프라인의 책임을 나누는 구성을 승인했다. 현재 세션에서 문서와 연결 참조를 수정하고 검증한다. 커밋·배포는 별도 요청 범위다.

**Goal:** Spec 내용과 표기 기준의 원본을 템플릿으로 모으고, 가상의 범용 샘플과 그림 원본을 연결한다.

**Architecture:** `templates/spec.md`는 산출물 기준, `examples/spec/document-generation/`은 적용 예시, `skills/orchestrate-work/references/diagrams.md`는 그림 제작 방법을 맡는다. 기존 스킬은 작성·검토·실행 시점과 참조 의무를 유지한다.

**Tech Stack:** Markdown, draw.io XML, PNG, Python unittest, 플러그인 validator.

## Task 1: 작성 기준과 파이프라인 참조

- [x] 수정 전 지침 검색 시나리오와 기존 테스트를 실행해 누락·기존 실패를 확인한다.
- [x] `templates/spec.md`에 승인된 8개 항목과 표기 규칙을 반영한다. 작은 변경의 생략 기준도 이곳에 모은다.
- [x] `skills/orchestrate-work/references/diagrams.md`에 도구 사용·파일 저장·내보내기 절차를 옮긴다.
- [x] `orchestrate-work/SKILL.md`, `references/workflow.md`, `decision-first-grill/SKILL.md`, `execute-task/SKILL.md`를 각 단계의 책임과 템플릿 참조로 정리한다.
- [x] `README.md`, `CONTEXT.md`, 인수 시나리오와 기존 계약 테스트의 참조를 맞춘다.

완료 기준: 필수 내용·상태 정의·Task 표 기준은 템플릿에서 찾고, 스킬에는 단계별 행동과 참조가 남는다.

## Task 2: 완성 샘플과 다이어그램

- [x] 가상 독서 모임의 활동 요약 PDF 내보내기로 `examples/spec/document-generation/spec.md`를 작성한다. 실제 조직의 결정·구현 현황·식별자는 포함하지 않는다.
- [x] `README.md`에 가상 예시의 성격과 절별 학습 포인트를 적는다.
- [x] `document-generation.drawio`에 사용자 유즈케이스·처리 흐름·엔티티 관계 3페이지를 작성하고 페이지별 PNG를 같은 폴더에 내보낸다.
- [x] 본문에 상대 경로로 삽입하고 그림·API·DB·상태 소유권의 일치를 확인한다.

완료 기준: 샘플에는 빈 작성란이 없고, 본문과 편집 원본 및 PNG가 함께 제공된다. 목업 완료와 실제 연계 완료를 혼동하지 않는다.

## Task 3: 검증과 리뷰 가능한 변경

- [x] 스킬의 참고 문서 연결, 샘플의 이미지·원본 연결 및 draw.io 페이지별 내보내기 대응을 검증한다.
- [x] 수정 전과 같은 검색 시나리오를 다시 실행해 누락된 기준을 참조만으로 찾는지 확인한다.
- [x] PNG 3개를 시각 확인하고 필요한 부분을 수정한다.
- [x] `python -m unittest discover -s tests -v`, `python scripts/validate_plugin.py`, `git diff --check`를 실행한다.
- [x] 변경 이유, 확인한 범위와 남은 제한을 보고한다.

완료 기준: 전체 기존 검증과 새 산출물 연결 확인이 통과하고, 커밋 전 diff로 리뷰할 수 있다.

## 검증 근거

- 수정 전 지침 검색에서 예상 시간·필드별 사용자 행동 근거·목업/실제 연계 분리 규칙의 부재를 확인했다. 수정 후 같은 상황을 읽기 전용으로 재검토해 템플릿 참조로 기준을 찾는 것을 확인했다.
- 가상의 독서 모임 사례로 본문·해설·draw.io·PNG를 구성하고, 이미지의 한글·선 겹침·표 잘림과 본문·관계도 일치를 확인했다.
- `python -m unittest discover -s tests -q`: 66개 통과. 문서 연결·PNG·draw.io 관계 검사와 기존 계약 테스트를 포함한다.
- `python scripts/validate_plugin.py`, `git diff --check`: 통과.
- Codex·Claude Code 각각에서 인수 사례 전체를 실행한 결과나 샘플 기능의 실제 구현·연계 검증 결과를 뜻하지 않는다.
