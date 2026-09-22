# Lab 제출 코드

학습 노트가 링크하는 **Lab 제출 코드 원본**이다. 노트 본문에는 발췌만 싣고
전문은 여기 둔다. 그 이유는 두 가지다.

1. `pre.code` 안의 한국어 주석은 영어 모드에서 그대로 남아 `langcheck.mjs` 가 실패시킨다.
   수백 줄에 주석 영어 짝을 다는 것은 유지가 안 된다.
2. 코드는 파일로 읽는 게 맞다. 노트는 왜 그렇게 짰는지를 나른다.

## 무엇이 여기 있고 무엇이 없나

| | |
|---|---|
| RTL, testbench, Makefile, README, 환경 파일 | **있다** |
| Lab 문제지 원문 | **없다.** 우리 저작물이 아니다 |
| 리포트 PDF, 파형 원본, 제출 zip | **없다** |

게시 결정과 그 근거는 저장소 루트 `CLAUDE.md` 의 "커밋하는 것과 안 하는 것" 절에 있다.

## lab1 · FIFO Design

노트: [Lab 1 기록](https://yoonkyu-lee.github.io/asu-cen-598-addv-fa26-notes/notes/LAB1-fifo-design.html)

```
part1/                     비동기 FIFO
  SOURCE.md                출발점이 무엇이었는지. 먼저 읽을 것
  fifo_if.sv               memory 용 interface + modport
  fifo_mem.sv              저장소
  fifo_wptr.sv             쓰기 포인터, wfull, almost_full
  fifo_rptr.sv             읽기 포인터, rempty, almost_empty
  sync_w2r.sv sync_r2w.sv  2 단 동기화기
  async_fifo.sv            최상위
  tb_async_fifo.sv         testbench. +TEST_* 로 셋 중 하나를 고른다
  Makefile  README  env.sh  env.cshrc

part2/                     Even/Odd Alternating Circuit
  rtl/even_odd_top.sv      공통 상위 모듈. FIFO 두 개와 2 상태 FSM
  rtl/sync/fifo_q.sv       동기 FIFO. 제출본이 쓰는 쪽
  rtl/async/fifo_q.sv      Part 1 의 async_fifo 를 동기 포트로 감싼 wrapper
  tb/tb_fifo_q.sv          FIFO 레벨. 두 구현이 공유한다
  tb/tb_even_odd.sv        상위 회로 레벨. 깊이 문서의 case 를 태운다
  MEASUREMENTS.md          두 구현을 같은 testbench 로 잰 값
  Makefile  README.md
```

**`part1/SOURCE.md` 부터 읽는 것을 권한다.** 이 Lab 은 강사가 준 스타터 코드가 없고
출발점이 Cliff Cummings 의 공개 논문 코드였다. 그 문서가 **무엇이 주어진 것이고 무엇을
얹은 것인지**의 경계를 적어둔다. 그게 없으면 이 디렉토리만 보고는 구별할 수 없다.

## 돌리는 법

Synopsys VCS 가 필요하다. ASU 의 Apporto (ECEE CAD Desktop, RHEL 8) 에서 돌렸다.

```bash
source part1/env.sh        # Apporto 기본 셸이 bash 다. csh 면 env.cshrc
cd part1 && make compile && make test1
cd part2 && make run       # 동기 FIFO
cd part2 && make compare   # 두 구현을 나란히
```
