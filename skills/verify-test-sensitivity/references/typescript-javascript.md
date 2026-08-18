# TypeScript와 JavaScript recipe

- predicate inversion: `items.filter(isVisible)`을 `items.filter(item => !isVisible(item))`로 바꾼다.
- promise 결과 반전: 거부해야 하는 분기를 resolve로 바꾼다.
- optional guard 제거: `if (!value) return`을 제거해 빈 입력이 다음 단계로 흐르게 한다.
- comparison boundary: `index < length`를 `index <= length`로 바꾼다.

타입 오류만 만드는 mutation은 피하고 사용자에게 보이는 행위를 깨뜨린다.
