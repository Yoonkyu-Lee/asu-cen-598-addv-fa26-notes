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
| `09_Floating Point Formats and Designs_Prashant` | **8 강** |
| `10_Lab2_Release` | 강의 아님 (Lab 2) |
| `11_Matrix Multiplier Accelerator Design` | **9 강** |
| `12_SoC Architecture and Interfaces` | **10 강** |
| `13 SoC Interconnect Design Eric` | **11 강** |
| `14_Lab3_Release` | 강의 아님 (Lab 3) |
| `15_System Verilog for Verification` | **12 강** (녹화 강의) |
| `16_Verification Concepts` | **13 강** |
| `17_Efficient Verification Tips` | **14 강** |
| `18_Lab4_Release` | 강의 아님 (Lab 4) |
| `20_Introduction to UVM Part 1` (PDF) | **16 강** |
| `21_Introduction to UVM Part 2` (PDF) | **17 강** |
| `22_Introduction to UVM Part 3` (PDF) | **18 강** |
| `23_Lab5_Release` | 강의 아님 (Lab 5) |
| `24_UVM_Review` | **19 강** |
| `19_CPU verification` | **15 강** (Material 에 `risc-v-verification_techniques.pdf` 가 딸려 있다) |

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
| 8 | 11 | 9/25 | Floating point arithmetic unit design | Prashant Joshi | (금요일 2:00-3:15pm 으로 이동) |
| 9 | 13 | 9/30 | Matrix multiplication accelerator design | Aman Arora |
| 10 | 14 | 10/5 | SoC architecture and on-chip interfaces | Aman Arora |
| 11 | 15 | 10/7 | Case study: SoC interconnect design | Eric Taylor |
| 12 | 17 | 녹화 | System Verilog for Verification | Aman Arora | (Dropbox 영상, 00:15~1:43. 10/19 수업에 참여 quiz) |
| 13 | 10 | 10/19 | Verification Concepts | Aman Arora | (예전 이 자리의 Assertion Based Verification 을 대체) |
| 14 | 19 | 10/21 | Efficient verification methods + Catch up | Aman Arora | (11/11 에서 당겨짐) |
| 15 | 21 | 10/28 | Case study: CPU verification | Aman Arora |
| 16 | 22 | 11/2 | UVM 1 | Joel Feldman |
| 17 | 23 | 11/4 | UVM 2 | Joel Feldman |
| 18 | 24 | 11/9 | UVM 3 | Joel Feldman | (11/11 에서 당겨짐) |
| 19 | 26 | 11/16 | UVM review | Aman Arora | (예전 이 자리의 High-speed I/O case study 를 대체) |
| 20 | 27 | 11/18 | Case study: SoC verification | Brendan Donahe |
| 21 | 29 | 11/25 | Formal verification overview | Amin Rezai |
| 22 | 30 | 11/30 | Emulation | Vivek Tiwari |
| 23 | 31 | 12/2 | Testing | Aman Arora |

## Lab (7)

Lab overview 강의는 별도 노트를 만들지 않고 `LAB{N}` 공략 페이지로 간다.

| Lab | site | 날짜 | 과제 |
|---|---|---|---|
| 0 | 3 | 8/31 | EDA Tools |
| 1 | 7 | 9/14 | FIFO |
| 2 | 12 | 9/28 | Pipelined MIPS |
| 3 | 16 | 10/14 | Systolic Matmul |
| 4 | 20 | 10/26 | FIFO Verification (plan, DPI, scoreboard, SVA) |
| 5 | - | 11/10 (화) | MIPS Verification (instruction generator, coverage, ISS) | (녹화 영상) |
| 6 | 28 | 11/23 | Systolic Matmul, APB agent, Assertions |

## 기말

| site | 날짜 | |
|---|---|---|
| 32 | 12/7 (월) | Final exam (BAC 116) |

## 2026-11-11 에 고친 것

강의 사이트 Schedule 을 다시 긁었다.

- **UVM 3 이 11/11 에서 11/9 (월) 로 당겨졌다.** 11/11 은 Veterans Day 다
- **Lab 5 overview 는 11/10 (화)** 이고 Schedule 에 Dropbox 영상이 붙어 있다. 설명서 제목은 "MIPS Verification" 이다
- **11/16 (월) 은 UVM review (Aman Arora) 다.** 예전 이 자리의 Case study: High-speed I/O design and verification 은 표에서 사라졌다.
  강의 수는 그대로 23 이다. 19 강의 주제만 바뀌었다
- **기말은 12/7 (월), BAC 116** 이다
- site 번호가 14 강부터 한 칸씩 밀려 있었다 (UVM 1 이 22 번). 14~23 강과 Lab 4~6 의 `site` 열을 고쳤다. Lab 5 행은 사이트에 번호가 없다 (25 번은 Veterans Day 가 가져갔다)

## 2026-11-01 에 고친 것

강의 사이트 Schedule 을 다시 긁었다. **13강부터 순서가 크게 바뀌었다.**

- **10/19 는 Verification Concepts 다.** 원래 이 자리의 Assertion Based Verification 은 표에서 사라졌다.
  SVA 는 Verification Concepts 덱 33쪽에 들어 있다
- **Efficient verification methods 가 11/11 에서 10/21 로 당겨졌다** (덱 `17_Efficient Verification Tips`)
- **CPU verification 은 10/21 에서 10/28 로 밀렸다.** UVM 1~3 은 11/2, 11/4, 11/11 이고 UVM 3 이 Lab 5 overview (11/9) 뒤로 갔다
- 강의 수는 그대로 23 이다. 13~18 강의 번호가 전부 바뀌었다
- **Lab 4 설명서 페이지가 Schedule 에서 다시 링크됐다.** 2 인 1 조다. 마감은 규칙상 Lab 5 overview (11/9) 전날 밤
- Lab 3 설명서 페이지도 Schedule 에서 링크가 살아났다

## 2026-10-14 에 고친 것

- **12강은 수업일이 없는 녹화 강의다.** Schedule 의 Material 칸이 Dropbox 영상 (00:15 부터 1:43 까지 보라) 이다.
  Lab 3 릴리스 덱 2쪽: "이번 주 두 번째 강의 영상" 이 금요일에 올라오고 **월요일 (10/19) 수업에 그 영상 기반 짧은 참여 quiz** 가 있다.
  **그 영상이 12강 영상인지 또 다른 영상인지는 덱만으로 확실하지 않다.** 금요일에 강의 사이트를 다시 볼 것
- **Lab 은 다음 Lab 릴리스 전날 밤이 마감이다** (Lab Assignments 페이지). Lab 2 는 Lab 3 덱 2쪽 기준 10/14 정오 마감이었다
- **Lab 3 는 4 인 1 조다** (Lab 3 덱 2쪽). Lab Assignments 페이지는 아직 "Lab 1~6 은 2 인 1 조" 라고 적혀 있다
- 개별 Lab 설명서 페이지는 Lab Assignments 에서 링크가 사라졌다. Lab 3 공략은 릴리스 덱만으로 썼다

## 2026-10-04 에 고친 것

강의 사이트 Schedule 을 다시 긁었다.

- **10/12 (월) 이 Fall Break 로 표시됐다.** Lab 3 overview 가 10/12 에서 10/14 (수) 로 밀렸다
- **12강 System Verilog for Verification 은 날짜 칸이 비었다.** 원래 10/14 였던 자리를 Lab 3 이 가져갔다.
  다음 Schedule 갱신 때 다시 확인한다
- **8강 Floating point 는 이제 사이트도 9/25 (금) 다.** 9/22 의 슬라이드 근거와 일치한다

## 2026-09-22 에 고친 것

**8강이 9/23 수요일에서 9/25 금요일 오후 2:00-3:15 로 옮겨졌다.** 근거는 `08_Efficient Design.pptx`
슬라이드 2쪽의 Logistics 다. "No lecture on Wednesday / Friday 2-3:15pm instead / The lecture has
been set up on the Canvas calendar" 라고 적혀 있다.

**강의 사이트 Schedule 표는 아직 9/23 수요일 그대로다** (2026-09-21 확인). 슬라이드가 더 최신이라
그쪽을 따랐다. Canvas 캘린더로 한 번 더 확인할 것.

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
