# Lab 0 Part I 수집 기록

Lab #0: Tools Tutorial - Fall 2026 의 Part I (Synopsys Online Trainings) 에서
지정된 레슨을 브라우저로 열어 나레이션과 화면 내용을 모은 것이다.

**전부 Synopsys 의 confidential 자료다.** VCS 덱의 `II. Confidential information` 슬라이드가
"You are not permitted to disseminate or use any of the information provided to you in this
presentation outside of Synopsys without prior written authorization" 라고 명시한다.
`.gitignore` 가 막는 것은 **`lab/**/materials/`, `lab/**/*.png|jpg|slides.jsonl`,
그리고 `lab/**/report.md`** 다. `lab/` 전체가 아니다.
**이 README 는 추적되어 공개 저장소에 올라간다.** `report.md` 는 증거 스크린샷을 임베드하므로
`materials/` 와 함께 무시된다.
**수집물은 반드시 `materials/` 안에 둔다.** 밖에 두면 그대로 게시된다.
공개 노트(`LAB0-*.html`)에는 여기 있는 슬라이드 이미지나 transcript 를 옮기지 않는다.
공개 쪽은 배운 개념을 직접 다시 쓰고, 근거는 공개된 VCS/Verdi User Guide 와 표준 문서로 단다.

## Lab 0 이 요구하는 것

| 강좌 | 필요한 레슨 | 상태 |
|---|---|---|
| VCS: RTL and Gate Level Simulation (course 290) | Introduction to VCS 중 섹션 1 `VCS Setup and Use model Information`, 섹션 2 `Debugging with VCS` | 수집 완료 |
| Verdi: Debugging with Verdi I (course 132) | `Verdi Core Debug` | 수집 완료 |
| Design Compiler: RTL Synthesis (2022.12) (course 86) | `Design and Technology Data - Part 1`, `- Part 2`, `Timing Analysis` | 수집 완료 (2026-09-08 접근 열림) |

제출물은 강좌마다 완료를 보여주는 스크린샷이다 (20점).

## Design Compiler 접근 기록

한동안 course 86 을 열면 플레이어 대신 `Purchase options $760.00 / ADD TO CART` 가 떴다.
**2026-09-08 에 풀렸다.** 교수가 확인해보라고 알려줬고, 지금은
`Course in progress, 0 of 21 lessons completed` 로 뜨며 세 레슨 모두 열린다. 그날 바로 수집했다.

같은 증상이 다시 보이면 **로그인 세션 만료부터 의심한다.** 실제로 한 번 그랬다.
세션이 끊기면 조용히 `/learn/signin` 으로 리다이렉트되고, 그 상태로 강좌를 열면
비수강자 화면(구매 안내)이 나온다. 카탈로그를 뒤지기 전에 `My Courses` 를 먼저 확인할 것.

Part 3 은 Lab 0 요구사항이 아니라 수집하지 않았다.

## 폴더

```
Introduction to VCS/                    VCS 강좌, Articulate Presenter 덱
  transcript.md                         슬라이드 30장: 나레이션 + 슬라이드 텍스트 + 캡처
  slides.jsonl                          기계 판독용 원본
  shots/00_I_introduction-to-vcs.png ... (목차 번호/이름, 30장)
Verdi Core Debug/                       Verdi 강좌, TechSmith Smart Player 영상 (34분)
  transcript.md                         목차 30구간: 나레이션 + 화면 텍스트 + 캡처
  shots/01_verdi-debug-scenario-training.png ... (30장)
Design and Technology Data - Part 1/    DC 강좌, Articulate HTML5 (React)
  transcript.md                         슬라이드 34장: 본문 + 강사 노트 + 캡처
  shots/00_unit-1-1.png ... (34장)
Design and Technology Data - Part 2/    같은 형식, 28장
Timing Analysis/                        같은 형식, 18장 (Unit 6)
```

제목은 전부 각 플레이어의 목차에 나온 문자열 그대로다. 임의로 바꾸지 않았다.

## 어떻게 뽑았나

**세 강좌의 플레이어가 전부 다르다.** 다음에 다른 트레이닝을 뽑을 때 이 구분부터 한다.
`sco` 프레임에 들어가서 `DIV#preso` 가 있으면 Articulate, `tsc-smartplayer` 면 TechSmith 다.
Articulate 는 다시 두 종류이고, `index_lms.html` 이냐 `index_lms_html5.html` 이냐로 갈린다.

**Articulate Presenter** (VCS). SCORM iframe 이 두 겹이다.
`browse frame --name sco` 하나로 내용 프레임까지 바로 들어간다 (프레임 트리 전체를 뒤진다).
그 안에서 전부 DOM 으로 읽힌다.

- 목차: `.cs-outline .cs-listitem`, 현재 항목은 `.cs-selected`
- 슬라이드 본문: `#slide` (시각용과 접근성용 두 벌이라 텍스트가 중복된다)
- 나레이션: `#transcript-content`. **Transcript 탭을 누르지 않아도 이미 DOM 에 있다**
- 컨트롤: `#play-pause` `#prev` `#next` `#seek`
- 애니메이션으로 쌓이는 슬라이드는 seek input (`input[aria-label="slide progress"]`, 단위 ms) 의
  값을 밀면 최종 프레임이 나온다. 이걸 안 하면 bullet 이 반만 찍힌다
- **클래식은 끝에 닿으면 무조건 다음 장으로 자동 진행한다.** `max - 100` 으로 밀면 넘어간다.
  **0.95 배가 실측 안전선**이다. 끝 신호를 기다려도 안 된다. 기다리면 덱을 계속 걸어간다
  (실측: 3 번에서 11 초 만에 12 번까지)
- 목차 클릭 직후에는 아직 **이전 슬라이드**의 seek input 이다. 0.7 초 기다렸다 민다
- 다 그려졌는지는 **`.slide-object.shown` 개수가 멈췄는가**로 본다. 클래식은 본문 텍스트가
  시각용/접근성용 두 벌이라 글자 수로는 못 센다
- **목차가 아코디언이고 한 번에 하나만 펼쳐진다.** 접힌 섹션의 하위 항목은 클릭이 아예 안 되니
  `is-scene` 행을 먼저 눌러 펼치고 애니메이션을 2~3 초 기다린다

**Articulate HTML5 / React** (Design Compiler). `index_lms_html5.html` 이고 위와 겉만 비슷하다.

- 목차는 같다: `.cs-outline .cs-listitem`
- 슬라이드는 `#slide` 가 아니라 **`.slide`**
- `DS` 전역이 없고 `#play-pause` `#seek input` 같은 ID 도 없다. 겉보기에 컨트롤이 전부 div 라
  손댈 데가 없어 보이는데, **그렇지 않다.** 아래 seekbar 항목을 볼 것
- **Transcript 탭이 `display:none` 이다.** 대신 슬라이드 안 **"Notes" 블록**에 강사 해설이 들어 있고,
  이 강좌에서는 설명의 대부분이 거기 있다. 34 장 중 11 장이 노트를 가지고 있었다
- **텍스트는 seek 없이 다 나온다. 스크린샷은 아니다.** 슬라이드 전체가 처음부터 DOM 에 있어서
  `textContent` 는 전부 주지만 (`innerText` 853 vs `textContent` 2416 자), **화면은 나레이션
  타임라인을 따라 하나씩 그려진다.** 목차 클릭하고 1~2 초 뒤에 찍으면 백지이거나 bullet 한 줄이다
- **seekbar 는 div 가 아니라 진짜 `input[type=range]` 다** (`aria-label="Seekbar"`, max 가 1).
  값을 0.999 로 밀고 `input`/`change` 를 쏘면 그 슬라이드의 최종 프레임이 즉시 나온다.
  한 장에 1 초면 끝난다. `.cs-seekcontrol` 첫 버튼이 `pause` 에서 `play` 로 바뀌는 게 끝 신호다
- 목차 첫 항목(`Unit 1-1` 같은 섹션 헤더)은 다음 슬라이드와 같은 것을 가리킨다. 중복이라 무시하면 된다
- **끝까지 밀면 자동 진행이 켜진 슬라이드는 다음 장으로 넘어간다.** 짧은 타이틀/Agenda 가 그렇다.
  찍기 전에 `.cs-selected` 의 index 를 확인하고 어긋나면 0.95 → 0.85 → 안 밀기 순으로 낮춘다
- 퀴즈 슬라이드에는 seekbar 가 없다. `innerText` 가 자라기를 멈출 때까지 기다렸다 찍는다
- **`browse screenshot` 은 `--viewport` 를 붙인다.** 기본값(전체 페이지)으로 찍으면 lightbox
  플레이어 영역이 통째로 하얗게 비어 나온다

**TechSmith Smart Player** (Verdi). 슬라이드가 아니라 mp4 화면 녹화다. iframe 이 세 겹이다.
`scormapi_v60` → `coredebug.html` → `coredebug_player.html`.

- `TSC.playerConfiguration.getXMPSrc()` 가 설정 XML 이름을 준다 (`*_config.xml`)
- 그 XML 의 `xmpDM:markers` 트랙 셋에 전부 들어 있다:
  `Caption` (나레이션, 시작시각+길이), `ScreenText` (화면에 뜬 글자), `TableOfContents` (목차+시작시각)
- caption 본문은 `{\rtf1 ...}` 로 감싸여 있어 RTF 를 풀어야 한다
- 캡처는 `video.currentTime` 을 목차 구간 끝 직전으로 옮기고 `pause()` 한 뒤 `seeked` 를 기다린다.
  `browse screenshot --clip` 으로 영상 영역만 잘라낸다

**Chromium 은 창이 가려지면 rAF 와 setTimeout 을 초당 1 회로 조인다.** `document.hidden` 은 false,
`hasFocus()` 는 true 라 증상만 보면 원인을 못 찾는다. 이 플레이어는 GSAP(rAF) 로 그리므로
그 상태에서는 슬라이드가 사실상 얼어붙는다. 수집하는 동안 창을 최상위로 올려둔다.
seek 으로 미는 방식은 타임라인이 도는지에 의존하지 않아서 이 문제에 덜 깨진다.

`browse frame` 은 `--name sco` 를 쓴다. CSS 선택자는 main 페이지만 뒤져서 중첩 프레임에 안 닿는다.
`browse click` 은 **지금 들어가 있는 프레임 안에 닿는다.** 오히려 React 컨트롤은 `el.click()` 을
무시하고 `browse click` 만 먹는다 (레슨 시작 때 뜨는 `Resume where you left off?` 프롬프트).

`browse eval <file>` 의 함정 두 가지. 파일 경로가 `/tmp` 나 cwd 아래여야 하고 아니면 **조용히 아무것도 안 한다.**
그리고 코드에 `await` 가 있으면 `(async()=>{...})()` 로 한 번 더 감싸므로 `return` 이 필요하고,
`await` 가 없으면 그대로 실행되므로 top-level `return` 이 문법 오류가 된다. 둘 중 하나로 맞춰야 한다.

## 2026-09-12 재수집

**DC 3 개 강좌와 VCS 의 shot 을 전부 다시 찍었다.** 2026-09-08 판은 목차를 클릭하고 1~2 초 뒤에 바로
찍어서 **80 장 중 52 장이 덜 그려진 상태**였다. `slides.jsonl` 에 `renderedLen`/`fullLen` 을
나란히 적어놓고도 둘을 비교하지 않아서 그때는 몰랐다.

이제 절차가 스크립트로 굳어 있다.

| 파일 | 하는 일 |
|---|---|
| `scripts/open-lesson.sh` | 레슨 열기. 투어/쿠키/Retake/Resume 프롬프트를 치우고 `sco` 프레임까지 들어간다 |
| `scripts/articulate-step.js` | 프레임 안. 슬라이드를 끝으로 밀고 판정 JSON 을 돌려준다 |
| `scripts/collect-articulate.sh` | 목차 클릭 → step → `--viewport` 스크린샷 루프. 어긋나면 재시도 |
| `scripts/shotcheck.py` | 검사. 로그(`shots.jsonl`)와 픽셀 양쪽으로 본다 |
| `scripts/rename-shots.py` | 파일 이름을 목차에 맞추고 문서 참조까지 고친다 |

```bash
bash scripts/open-lesson.sh "Timing Analysis"
bash scripts/collect-articulate.sh "lab/lab0/materials/Timing Analysis" 0 17
python scripts/shotcheck.py lab/lab0/materials
```

수집기의 판정 근거는 `shots.jsonl` 에 들어간다 (`stable` `ended` `renderedLen` `bodyLen`
`selectedIdx`). 기존 `slides.jsonl` 과 `transcript.md` 는 텍스트 수집 결과라 건드리지 않았다.
**텍스트 수집은 원래 멀쩡했다.** 깨진 것은 스크린샷뿐이다.

**VCS 30 장도 같은 날 다시 찍었다.** 클래식 플레이어라 위의 함정이 전부 여기서 나왔다.
목차 index 0..29 가 Lab 0 이 요구하는 범위(intro + 섹션 1, 2)이고 예전 수집과 같다.
`1.4. Mixed-Language Flow (3-step)` 한 장만 타임라인 75% 에서 멈추는데, 그 뒤로는 아무것도
안 그려져서 **내용은 완전하다** (예전 수집도 같은 자리에서 78% 였다).
검사기가 `SEEK_SHORT` 로 계속 표시하니 다음 사람도 눈으로 한 번 보면 된다.

Verdi 30 장은 TechSmith 영상이라 구조가 달라 다시 찍지 않았다. 검사를 통과한다.

## 파일 이름

shot 은 **목차 번호와 이름**을 달고 있다. `s00.png` 로는 나중에 어느 장인지 알 수 없다.

```
00_I_introduction-to-vcs.png
09_1.3_pure-verilog-flow-2-step.png
11_how-is-the-target-library-used.png      목차에 번호가 없는 강좌
```

`<인덱스>_<목차번호>_<이름>.png` 다. 인덱스를 맨 앞에 둬야 정렬이 목차 순서와 맞는다.
목차 번호만 쓰면 `1.10` 이 `1.2` 앞에 온다.

```bash
python scripts/rename-shots.py lab/lab0/materials
```

`transcript.md` 안의 `shots/...` 참조도 같이 고친다. 다시 돌려도 안전하다.

## Part II 환경: Apporto

**EDA 도구는 Apporto 에서만 돌아간다.** 밖에서 들어가는 SSH 는 설계상 불가능하고 ASU VPN 으로도 안 된다.
도구는 Apporto 의 AWS 스토리지에 있고 ASU 는 라이선스만 준다. ASU 쪽에 도구가 깔린 접속 가능한
머신이 없다. 유연성은 **Apporto 에서 밖으로 나가는 SSH 가 열려 있다**는 한 군데뿐이고,
그래서 강사가 권한 GitHub 경유가 실질적인 작업 방식이 된다. 홈이 NFS 라 노드가 바뀌어도 키와 작업물이 남는다.

노드는 **여러 명이 동시에 쓰는 공유 리눅스 서버**다 (실측: 같은 노드에 홈 86 개, 실행 중 사용자 3+ 명).
자원은 공유지만 홈은 `700` 이라 남이 내 코드를 못 본다. Sol(ASU RC)에는 FPGA 툴만 있고 Synopsys 는 없다.

실측 전체 (접근 경로, VPN, Sol 비교, 공유/격리 실험, 브라우저 원격 조작법) 는
**`materials/apporto-access.md`** 탐방 일지에 있다. 계정명과 내부 호스트명이 들어 있어
`materials/` 안에 두고 커밋하지 않는다.

## Verdi 강좌에서 알아둘 것

목차의 Demo 구간들(27 Incrementally Trace Schematic, 28 nCompare, 29 FSDB utilities)은
영상 안에 데모가 없다. 화면에 `View Video on YouTube` 만 뜨고, 나레이션이
`"Synopsys Unified Debug" on YouTube then you can find our channel for all demos` 라고 안내한다.
**그 데모들은 공개 자료다.** 공개 노트를 쓸 때 걸 수 있는 몇 안 되는 출처다.
