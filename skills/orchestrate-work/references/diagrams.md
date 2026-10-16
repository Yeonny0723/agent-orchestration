# Spec 다이어그램 작성 지침

그림의 필수 내용과 생략 판단은 [Spec 템플릿](../../../templates/spec.md)을 따른다. 이 문서는 도구 사용과 편집 원본·미리보기 관리 방법을 다룬다. [완성 샘플](../../../examples/spec/document-generation/README.md)에서 실제 파일 구성을 확인할 수 있다.

## 생성과 편집

Draw.io MCP가 연결돼 있으면 사용한다. Mermaid로 표현하기 쉬운 flow chart·ERD·Class diagram은 `open_drawio_mermaid`, UML Use Case나 세밀한 배치가 필요한 그림은 `open_drawio_xml`을 사용할 수 있다. UML Use Case를 상태 전이나 처리 순서 그림으로 대신하지 않는다.

기존 `.drawio`는 `list_pages`로 페이지를 찾고 `get_page`로 해당 원본을 읽은 뒤 `set_page`로 수정한다. 다른 페이지는 보존한다. 새 파일은 편집 가능한 노드·관계로 저장하며 PNG 한 장을 붙여 원본이라고 부르지 않는다.

## 파일과 본문 연결

Spec과 가까운 폴더에 `.drawio` 원본과 페이지별 PNG를 보관한다. 하나의 `.drawio`에 여러 페이지를 둘 수 있다. 예시 파일 구성은 다음과 같다.

```text
spec.md
document-generation.drawio             # use-cases / flow / entities 페이지
document-generation-use-cases.png
document-generation-flow.png
document-generation-entities.png
```

Spec 상단에서 원본을 상대 경로로 연결하고, 각 PNG는 관련 절에 `![설명](./파일명.png)`으로 삽입한다. 페이지 이름·ID와 PNG 대응은 샘플 해설 또는 본문에 표시한다. ERD는 파일명과 제목에서도 Class diagram과 구별한다.

## 내보내기와 시각 확인

draw.io 편집기 또는 사용 가능한 CLI의 페이지별 내보내기를 사용한다. 제목·주요 관계·범례가 잘리지 않는 여백과 읽을 수 있는 해상도를 선택한다. PNG를 열어 한글, 화살표, 선의 교차, 표의 긴 필드와 내용 잘림을 확인한다. 문서에서 상대 경로로 미리보기가 열리는지도 확인한다.

목업·현재 구현·목표 구조 중 그림이 나타내는 기준을 제목이나 인접 본문에 명시한다. 색이나 점선을 의미 있게 쓰면 범례를 제공한다. API 호출 방향과 응답 데이터의 이동을 혼동하지 않도록 화살표에 전달 내용을 표시한다.

## 동시 갱신

설계나 구현 사실이 바뀌면 영향받는 `.drawio` 페이지를 수정하고 해당 PNG를 다시 내보낸다. 본문·API·DB·Task의 기준을 맞추며, PNG만 수정하거나 원본만 고친 상태를 완료로 보고하지 않는다.

도구 연결이나 저장·내보내기가 불가능하면 가능한 편집 경로를 사용한다. 생성하지 못한 원본·PNG와 미확인 정합성을 구체적으로 기록하고, 실제로 만들거나 확인하지 않은 산출물을 완료로 표시하지 않는다.
