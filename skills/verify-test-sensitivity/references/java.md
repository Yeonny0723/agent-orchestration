# Java recipe

- conditional inversion: validation 조건을 반전한다.
- validation exception removal: 예외를 던지는 문장을 생략한다.
- enum 또는 state assignment omission: 필수 상태 전이를 제거한다.
- boundary movement: `<`를 `<=`로 바꾼다.

컴파일 실패가 아닌 행위 실패를 유도하고 mutation은 하나만 적용한다.
