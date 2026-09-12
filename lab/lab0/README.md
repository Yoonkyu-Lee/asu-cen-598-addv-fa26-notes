# Lab 0 Part I 수집 기록

Lab #0: Tools Tutorial - Fall 2026 의 Part I (Synopsys Online Trainings) 에서
지정된 레슨을 브라우저로 열어 나레이션과 화면 내용을 모은 것이다.

**전부 Synopsys 의 confidential 자료다.** VCS 덱의 `II. Confidential information` 슬라이드가
"You are not permitted to disseminate or use any of the information provided to you in this
presentation outside of Synopsys without prior written authorization" 라고 명시한다.
`lab/` 은 `.gitignore` 에 들어 있으므로 이 폴더는 GitHub 에 올라가지 않는다.
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
  shots/s00..s29.png
Verdi Core Debug/                       Verdi 강좌, TechSmith Smart Player 영상 (34분)
  transcript.md                         목차 30구간: 나레이션 + 화면 텍스트 + 캡처
  shots/s01..s30.png
Design and Technology Data - Part 1/    DC 강좌, Articulate HTML5 (React)
  transcript.md                         슬라이드 34장: 본문 + 강사 노트 + 캡처
  shots/s00..s33.png
Design and Technology Data - Part 2/    같은 형식, 28장
Timing Analysis/                        같은 형식, 18장 (Unit 6)
```

제목은 전부 각 플레이어의 목차에 나온 문자열 그대로다. 임의로 바꾸지 않았다.

## 어떻게 뽑았나

**세 강좌의 플레이어가 전부 다르다.** 다음에 다른 트레이닝을 뽑을 때 이 구분부터 한다.
`sco` 프레임에 들어가서 `DIV#preso` 가 있으면 Articulate, `tsc-smartplayer` 면 TechSmith 다.
Articulate 는 다시 두 종류이고, `index_lms.html` 이냐 `index_lms_html5.html` 이냐로 갈린다.

**Articulate Presenter** (VCS). SCORM iframe 이 두 겹이다.
`browse frame --url scormapi_v60` 로 launcher 에 들어가고 `browse frame --name sco` 로 내용 프레임에 들어간다.
그 안에서 전부 DOM 으로 읽힌다.

- 목차: `.cs-outline .cs-listitem`, 현재 항목은 `.cs-selected`
- 슬라이드 본문: `#slide` (시각용과 접근성용 두 벌이라 텍스트가 중복된다)
- 나레이션: `#transcript-content`. **Transcript 탭을 누르지 않아도 이미 DOM 에 있다**
- 컨트롤: `#play-pause` `#prev` `#next` `#seek`
- 애니메이션으로 쌓이는 슬라이드는 `#seek input` (`type=range`, 단위 ms) 의 값을 max 근처로 밀고
  `input` / `change` 이벤트를 쏘면 최종 프레임이 나온다. 이걸 안 하면 bullet 이 반만 찍힌다

**Articulate HTML5 / React** (Design Compiler). `index_lms_html5.html` 이고 위와 겉만 비슷하다.

- 목차는 같다: `.cs-outline .cs-listitem`
- 슬라이드는 `#slide` 가 아니라 **`.slide`**
- `DS` 전역이 없고 `#play-pause` `#seek input` 같은 ID 도 없다. seekbar 가 div(`.cs-seek`) 라
  값을 못 준다. 합성 마우스 이벤트는 무시되고, `browse click` 은 프레임 안으로 안 닿는다
- **Transcript 탭이 `display:none` 이다.** 대신 슬라이드 안 **"Notes" 블록**에 강사 해설이 들어 있고,
  이 강좌에서는 설명의 대부분이 거기 있다. 34 장 중 11 장이 노트를 가지고 있었다
- **결정적으로 seek 이 필요 없다.** 슬라이드 전체가 처음부터 DOM 에 있다.
  `innerText` 는 지금까지 그려진 것만 주지만 **`textContent` 는 전부 준다** (실측 853 vs 2416 자).
  화면도 처음부터 완성된 상태로 렌더된다. 그래서 목차를 클릭하고 1~2 초 뒤
  TreeWalker 로 텍스트 노드를 읽고 바로 스크린샷을 찍으면 끝이다
- 목차 첫 항목(`Unit 1-1` 같은 섹션 헤더)은 다음 슬라이드와 같은 것을 가리킨다. 중복이라 무시하면 된다

**TechSmith Smart Player** (Verdi). 슬라이드가 아니라 mp4 화면 녹화다. iframe 이 세 겹이다.
`scormapi_v60` → `coredebug.html` → `coredebug_player.html`.

- `TSC.playerConfiguration.getXMPSrc()` 가 설정 XML 이름을 준다 (`*_config.xml`)
- 그 XML 의 `xmpDM:markers` 트랙 셋에 전부 들어 있다:
  `Caption` (나레이션, 시작시각+길이), `ScreenText` (화면에 뜬 글자), `TableOfContents` (목차+시작시각)
- caption 본문은 `{\rtf1 ...}` 로 감싸여 있어 RTF 를 풀어야 한다
- 캡처는 `video.currentTime` 을 목차 구간 끝 직전으로 옮기고 `pause()` 한 뒤 `seeked` 를 기다린다.
  `browse screenshot --clip` 으로 영상 영역만 잘라낸다

`browse eval <file>` 의 함정 두 가지. 파일 경로가 `/tmp` 나 cwd 아래여야 하고 아니면 **조용히 아무것도 안 한다.**
그리고 코드에 `await` 가 있으면 `(async()=>{...})()` 로 한 번 더 감싸므로 `return` 이 필요하고,
`await` 가 없으면 그대로 실행되므로 top-level `return` 이 문법 오류가 된다. 둘 중 하나로 맞춰야 한다.

## Verdi 강좌에서 알아둘 것

목차의 Demo 구간들(27 Incrementally Trace Schematic, 28 nCompare, 29 FSDB utilities)은
영상 안에 데모가 없다. 화면에 `View Video on YouTube` 만 뜨고, 나레이션이
`"Synopsys Unified Debug" on YouTube then you can find our channel for all demos` 라고 안내한다.
**그 데모들은 공개 자료다.** 공개 노트를 쓸 때 걸 수 있는 몇 안 되는 출처다.
