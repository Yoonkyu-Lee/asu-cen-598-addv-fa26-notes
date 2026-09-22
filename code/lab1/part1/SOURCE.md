# 출발점: Cliff Cummings 의 FIFO style #1 레퍼런스 코드

Lab 1 은 **강사가 제공하는 초기 코드가 없다.** 확인한 것:

- Apporto 의 `/usr/local2/COURSES/ADDV/` 에는 `LAB0` 만 있다
- `~/labs/` 에도 `lab0` 만 있다
- Lab 페이지는 스타터 대신 이렇게만 적는다:
  *"You can use code from the Cliff Cummings paper linked above."*

그래서 이 디렉토리의 첫 커밋은 **그 논문의 코드 그대로**다. 다음 커밋이 랩 파트너의
작업물이므로, 두 커밋 사이의 diff 가 곧 **파트너가 실제로 무엇을 바꿨는가**다.

## 출처

Clifford E. Cummings, *Simulation and Synthesis Techniques for Asynchronous FIFO Design*,
SNUG San Jose 2002, Rev 1.2. Lab 1 페이지가 링크한 PDF 에서 그대로 옮겼다.

| 파일 | 논문의 위치 |
|---|---|
| `fifo1.v` | Example 2, p15 |
| `fifomem.v` | Example 3, p16 |
| `sync_r2w.v` | Example 4, p17 |
| `sync_w2r.v` | Example 5, p17 |
| `rptr_empty.v` | Example 6, p18 |
| `wptr_full.v` | Example 7, p19 |

들여쓰기만 복원했고 토큰은 손대지 않았다. 논문 코드 그대로라
`rempty_val` 과 `wfull_val` 이 선언 없이 쓰인다 (implicit wire).

## 이 코드가 Lab 1 요구사항에 못 미치는 것

파트너가 채워야 했던 간극이고, 곧 diff 로 드러난다.

- Verilog-2001 이다. `always_comb` / `always_ff` / `logic` 이 아니다
- `interface` 와 `modport` 가 없다
- `almost_full` / `almost_empty` 가 없다
- 포트 연결이 명시적 이름 연결이고 `.*` 가 아니다
- testbench, Makefile, README 가 없다
