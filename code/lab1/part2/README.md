# Lab 1 Part 2 — Even/Odd Alternating Circuit

짝수와 홀수가 뒤섞여 들어오는 스트림을 받아, **짝과 홀이 번갈아 나오는** 스트림으로
내보낸다. 각 parity 안에서의 순서는 입력 순서를 그대로 유지한다.

```
입력:  3  7  4  9  6  2  5  8
출력:  3  4  7  6  9  2  5  8
       홀 짝 홀 짝 홀 짝 홀 짝
```

## 두 구현을 같이 둔다

제출하는 것은 **동기 FIFO 판 하나**다. 비동기 판은 **비교를 위해** 둔다.

Part 2 는 클럭이 하나라 비동기 FIFO 가 필요 없다. Lab 도 그렇게 적는다.

> For this part of the lab, you do not need an asynchronous FIFO. So, you can either
> design a synchronous FIFO or just use the asynchronous FIFO designed in part 1.
> No points will be deducted either way.

둘 다 만들어 두면 **"왜 동기를 골랐는가" 를 추측이 아니라 측정으로** 답할 수 있다.
Lecture 7 이 요구하는 읽기가 정확히 그것이다. 기법마다 무엇을 내주는지 보는 것.

## 구조

상위 모듈과 testbench 는 **한 벌뿐**이다. FIFO 만 갈아끼운다. 그래야 두 구현의
차이만 남고 다른 변수가 안 섞인다.

```
rtl/
  even_odd_top.sv      공통. 쓰기 라우팅 + 읽기 FSM. fifo_q 를 두 개 인스턴스
  sync/fifo_q.sv       동기 FIFO. 새로 설계
  async/fifo_q.sv      Part 1 의 async_fifo 를 동기 포트로 감싼 wrapper
tb/
  tb_fifo_q.sv         FIFO 레벨. 두 구현이 공유한다
  tb_even_odd.sv       상위 회로 레벨
Makefile
```

두 `fifo_q.sv` 는 **모듈 이름이 같고 디렉토리로만 갈린다.** 구현을 통째로 갈아끼우는
흔한 방식이고, 상위 모듈은 한 글자도 안 바뀐다.

**Part 1 의 파일은 한 줄도 고치지 않는다.** `async/fifo_q.sv` 가 상대 경로로 참조만 한다.

## `fifo_q` 계약

두 구현이 지켜야 하는 포트 목록. 여기서 어긋나면 갈아끼우기가 성립하지 않는다.

```systemverilog
module fifo_q #(
    parameter int DATA_WIDTH = 8,
    parameter int DEPTH      = 64
)(
    input  logic                  clk,
    input  logic                  rst_n,

    input  logic                  wr_en,
    input  logic [DATA_WIDTH-1:0] wr_data,

    input  logic                  rd_en,
    output logic [DATA_WIDTH-1:0] rd_data,

    output logic                  full,
    output logic                  empty
);
```

`almost_full` 과 `almost_empty` 는 노출하지 않는다. Lab 이 Part 2 에서는 쓰지 않는다고
적었다.

## FIFO 깊이를 어떻게 정했나

**40이다.** 셈은 이렇고, 측정값은 MEASUREMENTS.md 에 있다.

FIFO 크기 계산 문서의 **Case 9** 가 이 Lab 의 사양과 글자 그대로 같다.

> Writing Data = 80 DATA/100 Clock, Outgoing Data = 8 DATA/10 Clock

문서는 최악을 이렇게 잡으라고 한다. **쓰기는 최대 속도, 읽기는 최저 속도.**
즉 80개가 80사이클에 몰려 들어오고, 읽기는 10사이클당 8개다.

그런데 이 회로는 FIFO 가 하나가 아니다. **둘이고, 읽기가 번갈아 간다.**
그래서 문서의 셈을 그대로 쓰면 틀린다.

| | 셈 | 답 |
|---|---|---|
| FIFO 가 하나라면 | 80 들어오는 동안 64 나간다 | 16 |
| 이 회로 (FIFO 둘, 교대 읽기) | 아래 | **40** |

깊이를 정하는 것은 **속도 차가 아니라 parity 쏠림**이다. 평균 속도는 양쪽 다
사이클당 0.8 로 같다. 문제는 짝수만 40개 먼저 들어오는 경우다.

1. 짝수 FIFO 에 1사이클당 하나씩 쌓인다
2. 읽기 쪽은 짝수 하나를 내보낸 뒤 **홀수를 기다리며 멈춘다.** 홀수가 아직
   하나도 안 들어왔기 때문이다. 짝수가 쌓여 있어도 꺼낼 수 없다. 꺼내면 짝수가
   두 번 연속 나가서 설계의 유일한 약속이 깨진다
3. 41번째 사이클에 첫 홀수가 들어올 때까지 짝수 FIFO 는 계속 찬다

**그래서 한 parity 의 최대 점유량이 그 parity 의 전체 개수에 붙는다.**
Lab 이 "40 are even and 40 are odd" 를 중요한 가정이라고 못 박은 이유가 이것이다.
한 parity 가 40개를 넘지 않으므로 **40이 상한이고, 40이면 충분하다.**

측정이 이 셈과 맞는다. `case9_skew` 에서 `peak_even = 39` 다. 하나를 일찍 꺼냈기
때문에 40이 아니라 39다.

**여기서 두 구현이 갈린다.** 동기 FIFO 는 40을 그대로 쓴다. 비동기 FIFO 는 gray
code 포인터 때문에 깊이가 2의 거듭제곱이어야 해서 **64로 올려야 한다.** 24칸 x
8비트 = 192 플롭이 FIFO 하나당 그냥 놀고, 두 개니까 384다.

## 돌리는 법

```bash
source ../part1/env.sh     # Apporto 기본 셸이 bash 다
make fifo                  # FIFO 구현만 먼저 검증
make run                   # 상위 회로, 동기 FIFO (제출본)
make VARIANT=async run     # 상위 회로, 비동기 FIFO
make compare               # 둘 다 돌려 결과를 나란히
make verdi                 # 파형
```

깊이는 Makefile 이 구현에 맞춰 넘긴다. 동기 40, 비동기 64. 바꾸려면
`make run DEPTH_sync=48` 처럼 준다.

테스트 하나만 돌릴 때는 **다시 컴파일하지 않는다.**

```bash
make run TEST=case9_skew
cd build/sync && ./simv +TEST=case8    # 이미 빌드돼 있으면 이쪽이 빠르다
```

빌드 산출물은 `build/sync/` 와 `build/async/` 로 갈라져서 서로 덮어쓰지 않는다.

## 현황

- [x] `async/fifo_q.sv` wrapper 와 FIFO 레벨 검증
- [x] `sync/fifo_q.sv`
- [x] `even_odd_top.sv`
- [x] `tb_even_odd.sv` (문서 Case 9, 8, 7 + parity 완전 쏠림)
- [x] 두 구현 비교 측정 (MEASUREMENTS.md)
- [ ] Verdi 파형 스냅샷과 **손으로 하는** 주석
- [ ] 리포트: 크기 근거, AI 사용 요약, 버그 하나, 파트너 기여 요약
- [ ] Design Compiler 로 두 구현의 면적 비교 (선택)

두 구현 다 네 case 를 통과한다. 자세한 숫자는 MEASUREMENTS.md.
