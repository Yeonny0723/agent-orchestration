# Python recipe

- comparison boundary: `amount < limit`를 `amount <= limit`로 바꾼다.
- raised exception removal: validation 분기의 `raise`를 생략한다.
- filtered comprehension relaxation: 필터 조건 하나를 제거한다.
- state assignment omission: 상태 변경 할당을 생략한다.

SyntaxError나 ImportError만 만드는 mutation은 피한다.
