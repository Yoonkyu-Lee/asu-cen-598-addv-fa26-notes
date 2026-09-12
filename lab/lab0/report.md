# Lab #0: Tools Tutorial — Part I Report

**CEN 598 · Advanced Digital Design and Verification · Fall 2026**
Instructor: Aman Arora · Individual assignment (no groups)

> 초안이다. 제출 전에 아래 **AI 사용 기록**을 본인이 읽고 사실과 맞는지 확인할 것.
> Part II (Apporto) 는 아직 안 했고 별도로 채운다.
>
> **Part I 은 세 트레이닝 모두 끝났다.** 상태와 증거는 아래 표에 있다.

---

## Part I: Synopsys Online Trainings

Part I 은 지정된 트레이닝의 **필수 레슨**을 완료하는 것이다 (20점).
과제 문서가 요구하는 것은 강좌 전체가 아니라 아래 표의 레슨뿐이다.

| # | Training | 필수 레슨 | 상태 |
|---|---|---|---|
| 1 | VCS: RTL and Gate Level Simulation (course 290) | `Introduction to VCS` 중 <br>· VCS Setup and Use model Information <br>· Debugging with VCS | 필수 구간 전부 열람 |
| 2 | Verdi: Debugging with Verdi I (course 132) | `Verdi Core Debug` | **Completed** (1 / 4) |
| 3 | Design Compiler: RTL Synthesis 2022.12 (course 86) | · Design and Technology Data - Part 1 <br>· Design and Technology Data - Part 2 <br>· Timing Analysis | **Completed** (3 / 3) |

### 증거 스크린샷

`lab/lab0/materials/completion/` 에 있다. 이 폴더는 공개 저장소에 올라가지 않는다.

| 파일 | 무엇을 보여주는가 |
|---|---|
| `01-vcs-introduction-to-vcs-menu.png` | `Introduction to VCS` 의 메뉴. 섹션 1·2 와 그 하위 항목이 전부 열람 표시(흐린 글씨)이고, 요구사항이 아닌 섹션 3·4 는 미열람(진한 글씨)으로 남아 있다 |
| `02-verdi-core-debug.png` | course 132 레슨 목록. `Verdi Core Debug` 에 `Completed` 배지 |
| `03-design-compiler-lessons.png` | course 86 레슨 목록. 세 레슨이 `Completed` |

**스크린샷은 메뉴와 레슨 목록만 잘라서 찍었다.** Synopsys 슬라이드 본문에는 배포 금지 표시가
있어서, 완료 증거에 필요 없는 본문은 일부러 프레임 밖으로 뺐다.

### 강좌별로 완료 판정이 다르다

같은 "완료"라도 플레이어에 따라 기준이 다르다. 증거 형태가 강좌마다 다른 이유다.

- **Design Compiler** (Articulate): 레슨의 모든 슬라이드를 방문하면 LMS 가 `Completed` 로 기록한다.
  세 레슨 모두 그렇게 잡혀 있다.
- **VCS** (Articulate): 과제가 레슨 전체가 아니라 **두 섹션만** 요구한다. 그래서 레슨 단위
  `Completed` 배지는 뜨지 않고, 메뉴에 남는 **항목별 열람 표시**가 증거가 된다.
- **Verdi** (TechSmith 영상): 끝으로 이동해 재생 종료 이벤트를 띄우는 것만으로는 완료로 안 잡힌다.
  **실제로 재생된 구간의 비율**을 보기 때문에 처음부터 끝까지 재생해야 한다.

---

## AI 사용 기록

이 과목은 AI 도구 사용을 허용하되 사용 내역 기재를 요구한다. 실제로 한 일을 그대로 적는다.

**도구**: Claude Code (Anthropic), 헤드 브라우저 자동화(Playwright 기반) 포함.

**무엇에 썼나**

1. **트레이닝 진행.** Synopsys Learning Center 에 로그인된 브라우저를 자동화해서 레슨을 열고,
   목차 항목을 차례로 눌러 각 슬라이드를 타임라인 끝까지 보냈다. Verdi 는 영상이라
   음소거 상태로 2배속으로 처음부터 끝까지 재생했다.
   **실시간으로 앉아서 본 것이 아니라 도구가 진행시킨 것이다.**
2. **자료 수집.** 각 레슨의 슬라이드 텍스트, 나레이션(또는 강사 노트), 화면 텍스트를 DOM 에서
   추출해 개인 학습용으로 `lab/lab0/materials/` 에 저장했다. 외부에 공개하지 않는다.
3. **학습 노트 작성.** 수집한 내용을 근거로 VCS / Verdi / Design Compiler 개념 정리 페이지를
   직접 다시 썼다. Synopsys 슬라이드 이미지나 나레이션 문장은 옮기지 않았다.
4. **이 리포트 초안.**

**하지 않은 것**: 계정 등록이나 결제 같은 계정 행위, Quiz 응시.

---

## Part II: Apporto server (미완료)

Apporto 에서 세 도구를 실제로 돌리는 부분. 아직 하지 않았다.

| Task | 내용 | 상태 |
|---|---|---|
| 1 | VCS: compile and simulate | 미완료 |
| 2 | Verdi: view waveforms | 미완료 |
| 3 | Design Compiler: synthesis | 미완료 |

시작할 때 주의할 것 두 가지.

- 실습 파일은 `/usr/local2/COURSES/ADDV/LAB0` 에 있고 **자기 작업 디렉토리로 복사한 뒤** 시작한다.
- `env.cshrc` 는 **tcsh 용이라 bash 에서 돌지 않는다.** `tcsh` 로 들어간 다음 source 한다.
