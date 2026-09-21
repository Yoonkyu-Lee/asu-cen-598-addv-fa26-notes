# 강의 일정

강의 사이트 Schedule 표 기준. **`index.html` 의 뼈대이고, `write-note` 와
`convert-slides` 가 함께 참조하는 단일 출처다.** 여기만 고친다.

## 번호 규칙

**Lab overview 는 강의로 세지 않는다.** 강의 23 개와 Lab 7 개를 따로 센다.
강의 번호는 Lab 을 뺀 날짜순이다.

**강사가 자료 앞에 붙인 번호는 5번까지만 강의 번호와 일치한다.** 강사가 Lab 1 릴리스를
`06_Lab1_Release.pptx` 로 넣으면서 6번부터 한 칸씩 밀렸다. Lab 자료가 더 끼어들면 또 밀린다.
**파일 번호를 강의 번호로 믿지 말고 이 표의 주제와 날짜로 대조한다.**

| 강사 파일 | 여기 번호 |
|---|---|
| `01_Course Intro` ~ `05_FIFO_Design_Igor` | 1 ~ 5 강 |
| `06_Lab1_Release` | 강의 아님 (Lab 1) |
| `07_Pipelined CPU Design` | **6 강** |
| `08_Efficient Design` | **7 강** |

강의 사이트의 Schedule 번호는 Lab 을 함께 세므로 여기 번호와 다르다.
아래 표의 `site` 열이 그 번호다. **강의 사이트와 대조할 때만 쓴다.**
사이트 번호는 10 과 11 이 날짜순과 어긋나 있는데, 여기서는 날짜순으로 정리되어 사라졌다.

## 강의 (23)

| # | site | 날짜 | 주제 | 강사 |
|---|---|---|---|---|
| 1 | 1 | 8/24 | Course Intro and Design Flow | Aman Arora |
| 2 | 2 | 8/26 | Digital Design and Verif Review | Aman Arora |
| 3 | 4 | 9/2 | System Verilog for Design | Aman Arora |
| 4 | 5 | 9/9 | Clock and Reset (Timing, CDC, RDC) | Chetan Sudarshan |
| 5 | 6 | 9/11 | FIFO design | Igor Miranda | (금요일 보강) |
| 6 | 8 | 9/16 | Pipelined CPU design | Aman Arora |
| 7 | 9 | 9/21 | Efficient design methods + Catch up | Aman Arora |
| 8 | 11 | 9/23 | Floating point arithmetic unit design | Prashant Joshi |
| 9 | 13 | 9/30 | Matrix multiplication accelerator design | Aman Arora |
| 10 | 14 | 10/5 | SoC architecture and on-chip interfaces | Aman Arora |
| 11 | 15 | 10/7 | Case study: SoC interconnect design | Eric Taylor |
| 12 | 17 | 10/14 | System Verilog for Verification | Aman Arora |
| 13 | 10 | 10/19 | Assertion Based Verification | Aman Arora |
| 14 | 18 | 10/21 | Case study: CPU verification | Aman Arora |
| 15 | 20 | 10/28 | UVM 1 | Joel Feldman |
| 16 | 21 | 11/2 | UVM 2 | Joel Feldman |
| 17 | 22 | 11/4 | UVM 3 | Joel Feldman |
| 18 | 24 | 11/11 | Efficient verification methods + Catch up | Aman Arora |
| 19 | 25 | 11/16 | Case study: High-speed I/O design and verification | Aman Arora |
| 20 | 26 | 11/18 | Case study: SoC verification | Brendan Donahe |
| 21 | 28 | 11/25 | Formal verification overview | Amin Rezai |
| 22 | 29 | 11/30 | Emulation | Vivek Tiwari |
| 23 | 30 | 12/2 | Testing | Aman Arora |

## Lab (7)

Lab overview 강의는 별도 노트를 만들지 않고 `LAB{N}` 공략 페이지로 간다.

| Lab | site | 날짜 | 과제 |
|---|---|---|---|
| 0 | 3 | 8/31 | EDA Tools |
| 1 | 7 | 9/14 | FIFO |
| 2 | 12 | 9/28 | Pipelined MIPS |
| 3 | 16 | 10/12 | Systolic Matmul |
| 4 | 19 | 10/26 | FIFO Checker, DPI |
| 5 | 23 | 11/9 | MIPS Random Stimulus, Coverage |
| 6 | 27 | 11/23 | Systolic Matmul, APB agent, Assertions |

## 기말

| site | 날짜 | |
|---|---|---|
| 31 | 12/7 (월) | Final exam |

## 2026-09-21 에 고친 것

강의 사이트 Schedule 을 다시 긁어서 네 군데를 고쳤다. **긁기 전에는 전부 틀린 채였다.**

- **4강 9/7 -> 9/9, 5강 9/9 -> 9/11.** 9/7 이 Labor Day 라 한 주가 통째로 밀렸고,
  FIFO 는 금요일 보강으로 들어갔다
- **7강과 8강의 주제가 맞바뀌었다.** Floating point (Prashant Joshi) 가 9/23 으로 밀리고
  Efficient design methods 가 9/21 로 당겨졌다. L01 s9 에서 강사가 예고한
  "guest speaker 사정으로 순서가 바뀔 수 있다" 가 실제로 일어난 것이다.
  **site 번호와 날짜는 원래 맞았고 주제만 어긋나 있었다.** 날짜만 대조했으면 못 잡는다

**학기 중에 이 표가 바뀐다.** 새 노트를 쓰기 전에 Schedule을 다시 긁어서 대조한다.
외부 강사 강의는 "guest speaker 사정으로 순서가 바뀔 수 있다"고 강사가 밝혔다 (L01 s9).
순서가 실제로 바뀌면 **날짜를 먼저 고치고 번호를 다시 매긴다.**
