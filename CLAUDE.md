# CEN 598 ADDV 학습 노트 프로젝트

## 이 저장소가 하는 일

ASU CSE 494 / CSE 598 / CEN 598 (Advanced Digital Design and Verification, Aman Arora, Fall 2026)
강의 슬라이드를 한 장씩 분해해서, **업계 용어를 모르는 사람도 읽히는** 개인 학습 노트 HTML로
재구성한다. 노트 옆에 원본 슬라이드 PDF를 띄우고 스크롤을 동기화해서, 지금 읽는 문단이
슬라이드 몇 쪽에서 나온 것인지 바로 보이게 한다.
GitHub Pages로 배포된다: https://yoonkyu-lee.github.io/asu-cen-598-addv-fa26-notes/

사용자(YK)는 UIUC Computer Engineering 학부를 졸업하고 ASU에서 MS 중인 한국인 학생이다.
디지털 설계 / 반도체 배경이 있고, ECE 385, 391, 408, 411, 444를 들었다.
**Verilog로 설계해본 경험은 있지만 산업 현장의 워크플로우와 용어는 처음이다.**
이 간극이 이 노트가 존재하는 이유다.

## 착수 — 스킬 라우터

**절차는 전부 `.claude/skills/` 에 있다. 이 문서는 어겼을 때 되돌리기 비싼 것만 담는다.**

| 하려는 일 | 읽을 스킬 |
|---|---|
| 새 강의 노트를 쓴다 | `convert-slides` → `write-note` → `note-html` **셋 다** |
| 기존 노트의 문구·도해를 고친다 | `note-html` |
| Lab 공략 페이지를 쓴다 | `write-note` → `note-html` |
| 슬라이드만 저장소에 넣는다 | `convert-slides` |
| Synopsys 트레이닝을 수집한다 | `synopsys-training` (또는 `-chrome`) |
| `index.html` 허브를 고친다 (카드·chip·공지 배너) | `note-html`, 노트를 새로 올리는 경우는 `write-note` 도 |
| `glossary.html` 에 용어를 추가한다 | `write-note` |

강의 번호·날짜·강사는 `docs/schedule.md` 가 단일 출처다.

**불변식은 이 문서가 이긴다. 각 절차의 단일 출처는 해당 스킬이다.**
규약을 고쳤으면 스킬도 같이 고친다. 스킬은 요약이지 사본이 아니다.

## 경로

| 용도 | 경로 |
|---|---|
| 저장소 | `D:\Engineering\asu-cen-598-addv-fa26-notes` |
| 강의 자료 원본 (스테이징) | `lecture/` (저장소 안, `.gitignore` 로 제외) |
| 강의 사이트 (원천) | https://adventlab.notion.site/addv-fall2026-website |

**예전에는 Drive 미러가 원본이었으나 머신 초기화로 사라졌다.** 이제 강의 사이트에서
`lecture/` 로 직접 받는다. 여기 있는 것은 **하나도 커밋되지 않는다.** 원본 PPTX,
Lab 문제지, 폰트 zip 이 전부 여기 남고, 저장소에 올라가는 것은 변환된 `slides/*.pdf` 뿐이다.
변환과 쪽수 대조 절차는 `convert-slides` 참조.

## 브라우저 고르기

**gstack browse 와 `claude --chrome` 은 상호보완이다.** 둘 다 쓸 수 있으면 아래로 고른다.

| 상황 | 쓸 것 |
|---|---|
| 덱 전체처럼 **양이 많은** 수집 | `browse`. 한 번의 eval 로 통째로 가져온다 |
| **iframe 안**에 든 콘텐츠 (SCORM 등) | `browse`. Chrome 도구는 프레임 안에 못 들어간다 |
| **오래 도는** 작업 (영상 재생, 완료 판정) | `browse`. 사용자의 실제 브라우저를 묶지 않는다 |
| **이미 로그인된** 세션을 그대로 쓰고 싶을 때 | Chrome. 재로그인이 없다 |
| **화면이 어떻게 보이는지**가 판단 대상일 때 | Chrome. 스크린샷을 직접 본다 |
| 몇 장만 **눈으로 확인**하면 될 때 | Chrome. 띄우는 비용이 없다 |

**바이너리는 `~/.claude/skills/gstack/browse/dist/browse.exe` 다.** Windows 에서는 확장자가 붙는다.
로그인 유지, `.gstack/browse.json`, 유령 서버 정리 같은 운용 상세는 `synopsys-training` 참조.

**gstack `v1.81` 부터 브라우징 스킬이 Aside 를 1 순위 드라이버로 쓴다. Aside 는 macOS 전용이라
Windows 인 이 머신에서는 번들 브라우저가 그대로 쓰인다.** `./setup` 도 그렇게 보고한다.
gstack 스킬 문서에 Aside 이야기가 나와도 여기서는 fallback 경로가 정상이다.

되돌릴 수 없는 버튼(제출, 삭제, 결제)은 사용자의 진짜 계정에서 실제로 눌린다.
**누르기 전에 확인을 받는다.**

## 절대 어기지 않는 것

스킬을 안 읽고 들어와도 이것만은 어기면 안 된다. **판단 기준은 "어겼을 때 되돌리기가 비싼가" 다.**

- **교재가 없다.** 강의계획서가 "There is no textbook for this course" 라고 명시한다.
  비슷한 책을 교재로 적지 않는다. footer 에 교재 줄을 넣지 않는다
- **용어를 지어내지 않는다.** 이 과목의 최대 위험이다. 업계에서 안 쓰는 말을 그럴듯하게
  만들어내는 것. 확신이 없으면 슬라이드 표현을 쓰고 "강의에서는 이렇게 부른다" 로 범위를 좁힌다.
  **자동 검사가 못 잡는다**
- **em dash(—) 금지.** 콜론, 쉼표, 마침표를 쓴다 (SVG 안과 구분선은 예외)
- **업계 용어는 영어 유지, 서술은 한국어.** netlist, tapeout, DUT, RTL 을 번역하거나 음차하지 않는다
- **`lecture/` 는 통째로 커밋 금지.** 원본 PPTX, Lab 문제지, 라이선스 붙은 폰트가 여기 있다
- **색을 하드코딩하지 않는다.** 그리고 의미가 고정돼 있다

| 대상 | 색 |
|---|---|
| Design (RTL, 설계자, front-end) | `--blue` |
| Verification (testbench, 검증 엔지니어) | `--pink` |
| 도구와 자동화 (synthesis, STA, simulator) | `--violet` |
| 통과·정답·sign-off | `--green` |
| 버그, 함정, 실패 | `--amber` |
| 물리·back-end (P&R, fab, silicon) | `--brown` |
| 이 강의 범위 밖 | `--ink3` |

## 커밋하는 것과 안 하는 것

repo는 **Public**이고 GitHub Pages로 서빙된다. 여기 올리는 건 인터넷에 게시하는 것이다.

**강의계획서의 Student Copyright Responsibilities가 이렇게 적고 있다:**

> Students may not share outside the class, including uploading, selling or distributing
> course content or notes taken during the conduct of the course.

**사용자에게 이 조항을 알렸고, 슬라이드를 커밋하기로 결정했다.** 이 결정을 조용히 뒤집지 않는다.
나중에 내려달라고 하면 `slides/` 커밋을 지우고 `.gitignore`에 `slides/*.pdf`를 추가하면 된다.
리더는 슬라이드가 없어도 노트 본문을 막지 않는다.

무엇이 무시되는지는 `.gitignore` 파일이 단일 출처다. 커밋 전에 `git status` 로 확인한다.

| 파일 | 커밋 |
|---|---|
| `slides/L{NN}-*.pdf` (강의 슬라이드) | O |
| `vendor/pdf.js/` | O |
| `*.pptx` 원본 | **X.** PDF만 올린다. 발표자 노트가 딸려 들어간다 |
| `lecture/` 전체 | **X.** 원본 스테이징 폴더다. 폰트 zip 은 재배포 금지 자산이다 |
| Lab 문제지, 제출 코드 | **X.** 2인 1조 과제다. 학문적 정직성 문제로 직결된다 |
| Quiz, Exam 문제 | X |
| `shots/`, `node_modules/` | X |

커밋 전에 `git status`로 의도하지 않은 파일이 스테이징됐는지 확인한다.

**footer 문구**로 각 노트와 `index.html`에 이렇게 밝힌다: 강의 슬라이드의 저작권은
담당 강사(Aman Arora)와 ASU에 있다는 것, 이 사이트는 수강생이 만든 개인 학습 자료이고
공식 강의 자료가 아니라는 것, 노트 본문은 슬라이드를 재구성하고 보충한 것이라는 것.
**교재 줄은 넣지 않는다.** 대신 강의 사이트 링크를 둔다.
