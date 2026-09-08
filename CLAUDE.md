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

## EEE 554 노트와 무엇이 다른가

이 프로젝트는 `D:\Engineering\asu-eee-554-notes`의 구조를 그대로 물려받았다.
리더, 검증 스크립트, 디자인 토큰, 이중 언어 장치는 같은 것을 쓴다.
**하지만 노트가 채워야 하는 간극이 다르다.**

| | EEE 554 (확률) | CEN 598 (ADDV) |
|---|---|---|
| 막히는 지점 | 수식이 안 읽힘 | **용어와 약어가 설명 없이 지나감** |
| 핵심 장치 | `.nota` 기호 뜯어보기 | **`.jargon` 용어 뜯어보기** |
| 비주얼의 목적 | 수식에 그림을 붙임 | **누가·언제·무엇을 넘기는지 흐름을 그림** |
| 예제 | 손으로 푸는 문제 | **현장 감각: 이 판단을 실제로 어떻게 내리나** |
| 함정 | 반례 (수학적으로 틀린 것) | **혼동되는 이웃 용어, 회사마다 다른 이름** |
| 평가 | 숙제 + 시험 | **Lab 45% + Exam 30% + Quiz 20% + Participation 5%** |
| 교재 | Hajek 책이 검증 근거 | **교재 없음.** 아래 [근거](#내용의-근거) 참조 |

EEE 554 규약을 기계적으로 복사하지 않는다. 위 표에서 갈라지는 것은 이 문서가 이긴다.

## 경로

| 용도 | 경로 |
|---|---|
| 저장소 | `D:\Engineering\asu-cen-598-addv-fa26-notes` |
| 슬라이드 원본 (읽기 전용) | `D:\Library\01 Immigration Documents\02 ASU\FA26\CEN 598  ADDV` |
| 강의 사이트 (원천) | https://adventlab.notion.site/addv-fall2026-website |

Drive 미러 폴더는 **절대 수정하지 않는다.** 읽기만 한다.
PDF로 변환할 때도 원본을 건드리지 않는다 (아래 [슬라이드 변환](#슬라이드-변환-pptx--pdf) 참조).

**Drive 원본은 학기 중에 갱신된다.** 강사가 슬라이드를 고치거나 끼워 넣는다.
**노트를 쓰거나 고치기 전에 반드시 다시 변환하고 쪽수를 대조한다.**
낡은 사본으로 앵커를 달면 전부 한 칸씩 어긋난다.

```bash
node scripts/pagecount.mjs
```

## 강의 사이트가 원천이다

교재가 없으므로 **Notion 강의 사이트가 슬라이드 다음가는 1차 자료다.**
Schedule, Syllabus, Lab Assignments, Background Knowledge, Vendor Trainings, Resources 페이지가 있다.

Notion은 SPA라 `WebFetch`로는 빈 페이지가 온다. **브라우저 도구로 열고 DOM에서 긁는다.**
데이터베이스(표)는 `innerText`에도 안 잡히므로 `.notion-collection-item`을 직접 쿼리한다.

```js
[...document.querySelectorAll('.notion-collection-item')].map(r => r.innerText.replace(/\n+/g, ' | '))
```

이렇게 얻은 Schedule 표가 [모듈 목록](#모듈-목록-전체-30강)의 근거다.

### 로그인이 필요한 자료는 gstack browse 로 연다

`~/.claude/skills/gstack/browse/dist/browse connect` 가 별도 Chromium 을 headed 로 띄운다.
프로필이 `~/.gstack/chromium-profile` 에 남으므로 **한 번 로그인하면 재기동 후에도 유지된다.**
ASU SSO 의 Duo 2FA 쿠키와 Synopsys 트레이닝(`training.synopsys.com`) 세션까지 살아남는 걸 확인했다.
사용자의 실제 Chrome 은 건드리지 않는다. 별개 브라우저다.

**서버 상태가 `.gstack/browse.json` 한 파일에만 있고 거기에 인증 토큰이 있다.**
headed 세션이 떠 있는데 `browse` 명령이 그 서버를 못 찾으면 새 headless 서버를 띄우면서
**그 파일을 덮어쓴다. 그러면 살아 있는 창의 토큰이 영구히 날아가고 복구 경로가 없다.**
`browse status` 가 `Mode: headed` 가 아니라 `Mode: launched` 로 나오면 이미 그 상태다.
유령 서버를 `taskkill //PID <pid> //T //F` 로 정리하고 재기동하는 수밖에 없다.
로그인은 디스크에 있으므로 재기동 자체는 싸다.

## 내용의 근거

**강의계획서가 명시한다: "There is no textbook for this course."**
Drive나 도서관에 비슷한 책이 있다고 그것을 교재로 적으면 안 된다.
`index.html` footer에 교재 줄을 넣지 않는다. 이건 EEE 554와 다른 점이다.

그래서 검증 근거가 셋뿐이다.

1. **슬라이드 PDF.** 1차 근거. 시험과 quiz는 여기서 나온다.
2. **강의 사이트가 지정한 외부 자료.** Synopsys/Cadence 트레이닝, Harry Foster의 Wilson Research
   Group 검증 조사, 슬라이드에 URL이 박힌 블로그와 논문. 슬라이드가 출처를 적어놨으면 그 출처를 따라간다.
3. **업계 표준 문서.** IEEE 1800 (SystemVerilog), UVM 클래스 레퍼런스, AMBA APB/AXI 스펙.
   용어의 정확한 뜻이 헷갈릴 때 여기가 최종 심판이다.

**슬라이드 밖에서 가져온 것은 문맥으로 그게 보충이라는 걸 알 수 있게 쓴다.**
`data-slide`를 안 붙이는 것으로 이미 절반은 표시되지만, 본문에서도 "슬라이드에는 이름만
나오는데" 같은 식으로 밝힌다. 사용자는 근거 없는 주장을 바로 잡아낸다.

**용어를 지어내지 않는다.** 이 과목의 위험은 수학처럼 "계산이 틀리는" 게 아니라
**"업계에서 안 쓰는 말을 그럴듯하게 만들어내는 것"**이다. 확신이 없으면 슬라이드의 표현을 쓰고
"강의에서는 이렇게 부른다"라고 범위를 좁힌다.

## 슬라이드 변환 (PPTX → PDF)

EEE 554는 슬라이드가 PDF로 배포됐다. **여기는 PPTX다.** 리더가 PDF만 다루므로 변환이 필요하다.

LibreOffice는 이 머신에 없다. **PowerPoint COM 자동화를 쓴다.**

```powershell
# 원본을 스크래치패드로 복사한 뒤 거기서만 작업한다. Drive 미러는 건드리지 않는다.
$pres = $pp.Presentations.Open($work, $false, $false, $false)
foreach ($s in $pres.Slides) { if ($s.SlideShowTransition.Hidden -ne 0) { $s.SlideShowTransition.Hidden = 0 } }
$pres.SaveAs($dst, 32)   # 32 = ppSaveAsPDF
```

### 숨김 슬라이드를 반드시 포함시킨다

**기본 변환은 숨김 슬라이드를 빼버린다. 그러면 PDF 쪽 번호가 PPTX 슬라이드 번호와 어긋난다.**
실제로 이렇게 어긋났다.

| 덱 | PPTX 장수 | 숨김 | 기본 변환 결과 |
|---|---|---|---|
| 01_Course Intro | 25 | 17 | 24쪽 (17쪽 이후 전부 1칸 밀림) |
| 02_Design and Verification Overview | 59 | 31, 34, 54, 57, 58 | 54쪽 (5번 어긋남) |
| 03_System Verilog for Design | 37 | 11, 25 | 35쪽 (2번 어긋남) |

숨김 슬라이드를 되살려서 변환하면 **PDF 쪽 번호 = PPTX 슬라이드 번호 = 슬라이드에 인쇄된 번호**가
전부 일치한다. 어긋날 자리가 없어진다. 이게 포함시키는 첫 번째 이유다.

두 번째 이유: **숨김 슬라이드 내용이 좋다.** L02에서 빠졌던 게 Design/Verification Gap 그래프,
시뮬레이터 내부 동작, Separation of concerns, Challenges in verification이다. 전부 노트에 넣을 값어치가 있다.

`ExportAsFixedFormat`의 `PrintHiddenSlides` 인자는 PowerShell 후기 바인딩에서
`msoTrue(-1)`를 못 받는다. **숨김을 먼저 풀고 `SaveAs`를 쓴다.**

### pptx2pdf.ps1 을 고칠 때는 BOM 을 지키라

새 강의가 나오면 `$map` 에 한 줄을 더한다. 그때 **스크립트를 UTF-8 BOM 없이 저장하면 안 된다.**
Windows PowerShell 5.1 은 BOM 이 없는 파일을 ANSI 로 읽어서, 주석의 한글이 깨지고
`The string is missing the terminator` 같은 엉뚱한 파서 에러를 낸다. 실제로 이걸로 한 번 헤맸다.
Python 으로 고친다면 `encoding='utf-8-sig'` 로 저장한다.

### 숨김이었다는 사실은 노트에 적는다

수업에서 안 넘긴 장이므로 quiz에 나올 가능성이 낮다. 그 정보를 숨기지 않는다.
해당 섹션에 `.chip.dim` 또는 `.callout`으로 **"강의에서는 넘긴 슬라이드"**라고 표시한다.
숨김 목록은 이렇게 확인한다.

**다만 숨김이라고 다 넘어간 것은 아니다.** L04 의 25쪽은 24쪽과 글자가 완전히 같은 사본인데
**강사가 수업 중에 그 위에 그린 판서가 남아 있다.** 즉 실제로 수업에서 쓴 장이다.
(내용은 "multiple driver 금지"의 예외인 tristate bus 를 그림으로 설명한 것이라 값어치가 크다.)
**숨김 목록을 뽑았으면 그 쪽을 렌더해서 눈으로 볼 것.** 판서가 있으면 "넘긴 슬라이드"라고
적으면 안 되고, 무엇이 다른지를 밝혀야 한다.

```bash
python scripts/hidden-slides.py "<pptx 경로>"
```

## 파일 명명

```
index.html                                   허브 (모듈 목록)
glossary.html                                약어·용어 사전 (아래 참조)
L01-course-intro.html                        Lecture 1
L02-design-and-verification-overview.html    Lecture 2
L04-system-verilog-for-design.html           Lecture 4  (PPTX 는 03_ 로 시작한다)
L{NN}-{kebab-case-영문주제}.html

LAB{N}-{kebab-case-과제제목}.html            Lab 공략 (아래 참조)

slides/L01-course-intro.pdf                  Lecture 1 슬라이드 (노트와 같은 stem)
slides/L02-design-and-verification-overview.pdf

reader.js  reader.css                        슬라이드 리더 (모든 노트가 공유)
vendor/pdf.js/                               pdf.js 런타임
```

`{NN}`은 **강의 사이트 Schedule 표의 Lecture 번호**를 따른다. PPTX 파일 앞의 번호가 아니다.
둘은 대체로 같지만 Schedule이 기준이다. **실제로 어긋난다.** `03_System Verilog for Design.pptx`
는 Schedule 의 **Lecture 4** 다. 3강이 Lab 0 overview 라서 슬라이드 덱이 없기 때문이다.
Lab overview 강의가 나올 때마다 이 간격이 한 칸씩 더 벌어진다. Schedule에서 9강과 10강이 날짜순과 어긋나 있는데
(10강 Assertion Based Verification이 11강보다 뒤 날짜다), **번호를 따르고 날짜를 병기한다.**

**슬라이드 사본은 노트와 stem을 맞춰서 이름을 바꾼다.** `02_Design and Verification Overview.pptx`
→ `slides/L02-design-and-verification-overview.pdf`. 그러면 `reader.js`가 노트 파일명에서
슬라이드 경로를 바로 유도하므로 하드코딩된 매핑 표가 필요 없다.

### scripts/

| 스크립트 | 하는 일 |
|---|---|
| `verify.mjs` | 노트 검증. exit 0 이어야 통과 |
| `pptx2pdf.ps1` | PPTX → `slides/*.pdf`. 숨김 슬라이드를 되살려서 변환한다 |
| `pptx-text.py` | 슬라이드 본문 + **발표자 노트** 추출 |
| `hidden-slides.py` | 숨김 슬라이드 번호 목록 |
| `pagecount.mjs` | `slides/*.pdf`의 쪽 수. PPTX 장수와 대조용 |
| `pdftext.mjs` | PDF **쪽별** 텍스트. `data-slide` 앵커를 달기 전 대조용 |
| `render-slides.mjs` | PDF 쪽을 PNG로 렌더 → `shots/slides/` |
| `crop.mjs` | 스크린샷 일부만 잘라 보기 |
| `serve.mjs` | 로컬 서버. `.mjs` MIME 을 제대로 내보낸다 (아래 [슬라이드 리더](#슬라이드-리더-데스크톱-전용) 참조) |
| `readercheck.mjs` | 섹션으로 스크롤하며 리더가 실제로 그 쪽으로 따라오는지 대조 |
| `langcheck.mjs` | 영어 모드에 남은 한글 찾기. 번역 누락은 눈으로 못 잡는다 |

### 슬라이드를 눈으로 봐야 한다

**텍스트 추출만으로 도해를 옮기면 반드시 틀린다.** 실제로 이런 일이 있었다.

- L01 s13의 빨간 화살표가 어디를 가리키는지는 텍스트에 안 나온다. 렌더해서 보니
  **Design 박스**였다. "이 수업 1부가 집중하는 단계"가 정확히 어느 칸인지가 여기서 정해졌다.
- L01 s14의 Front-End / Back-End 괄호가 **Synthesis 한가운데에서 만난다.** 텍스트로는
  두 라벨만 보이니 아무 데나 선을 그었을 것이다.
- L01 s25의 회사별 용어 표는 텍스트 추출에서 **열 순서가 뒤섞여 나왔다.** 렌더해서 봐야
  Intel의 "Pre-Si Validation"이 Design Verification 행이라는 걸 알 수 있다.

이 머신에 poppler(`pdftoppm`)가 없어서 `render-slides.mjs`가 vendor의 pdf.js와
playwright로 대신 렌더한다.

```bash
node scripts/render-slides.mjs slides/L01-course-intro.pdf 12-18
```

**도해가 있는 쪽은 전부 렌더해서 열어본다.** 표·블록도·타임라인·그래프가 있는 쪽이 대상이다.

### 슬라이드가 아직 없는 강의

30강 중 대부분이 아직 안 나왔고, 외부 강사 강의는 당일에야 올라오는 일이 있다.
슬라이드 없이 노트를 쓰지 않는다. **`index.html`에서 `soon` 상태로 두고 기다린다.**

예외는 강의 사이트가 이미 자료를 지정한 경우뿐이다 (Background Knowledge의 CSE 320 자료 등).
그때는 EEE 554의 규칙을 따른다: 헤더에 `.chip.warn`으로 **슬라이드 미배포**를 표시하고,
00번 첫 블록을 `.trap`으로 두고 무엇을 근거로 썼는지 적고, `data-slide`와 `reader.js`를 빼고,
**"슬라이드가 올라오면 그쪽을 기준으로 삼아라"를 노트에 적는다.**

## 언어와 문체

- **모든 본문은 한국어.** 반말체, 설명하듯이. "~야", "~거야", "~돼".
- **em dash(—) 금지.** 콜론, 쉼표, 마침표를 쓴다. (SVG 안이나 구분선 용도는 예외)
- **업계 용어와 약어는 영어를 유지한다.** netlist, tapeout, slack, scan chain, testbench, coverage,
  assertion, DUT, RTL, ECO, DFT, UVM, BFM, VIP.
  **번역해서 쓰면 안 된다.** 사용자가 실제로 부딪힐 문서, 면접, 코드리뷰는 전부 영어다.
  "넷리스트"처럼 음차하지도 않는다. 영어 그대로 쓰고 처음 나올 때 `.jargon`으로 푼다.
- 반면 **일반 명사는 한국어로 쓴다.** "이 단계에서 넘기는 산출물", "여기서 갈라진다".
  용어는 영어, 서술은 한국어. 이 경계를 흐리지 않는다.
- 과장 금지. "놀랍게도", "사실은" 같은 수사보다 정확한 서술.
- **"업계에서는 ~한다"는 근거가 있을 때만 쓴다.** 슬라이드나 강사 발언(발표자 노트)에 있으면
  그렇게 밝히고, 없으면 쓰지 않는다. 이 과목은 실무 이야기라 지어내기 딱 좋고 검증도 어렵다.

### 발표자 노트를 읽는다

PPTX의 notes에 강사가 수업에서 할 말을 적어놨다. 슬라이드 본문에 없는 정보가 여기 있다.
예: L02 s4의 노트가 Intel FDIV 버그를 "약 10억 달러"라고 적어놨는데 슬라이드 본문에는 없다.
**슬라이드 텍스트만 뽑지 말고 노트도 같이 뽑는다.**

```bash
python scripts/pptx-text.py "<pptx 경로>"   # 슬라이드 본문 + 발표자 노트
```

노트에서 가져온 내용은 **"강사가 수업에서 덧붙인 이야기"**라는 게 드러나게 쓴다.
발표자 노트는 초안이라 슬라이드와 어긋나거나 다른 강의에서 복사된 흔적이 있다
(L02 s12의 노트는 정리 증명 이야기인데 슬라이드는 timing constraint다). **그대로 믿지 않는다.**

## 강의 노트의 5단 구조

각 개념 섹션은 이 순서를 반복한다. EEE 554의 5단을 이 과목에 맞게 바꾼 것이다.

1. **목차와 요약** — 이 강의가 무슨 일을 하는지, 새 용어가 뭔지, 나중에 어디서 쓰이는지.
   섹션 00에 배치. **"오늘 나오는 약어" 목록**과 그중 뭐가 제일 중요한지 명시.
2. **용어 정리** — 슬라이드의 정의를 그대로. `.def` 블록.
   그리고 **바로 뒤에 `.jargon`**을 붙인다. 이게 이 노트의 핵심 장치다.
3. **비주얼** — **흐름과 경계를 그린다.** 수식이 없는 과목이라 그림의 역할이 다르다.
   무엇이 무엇으로 변환되는지, 누가 누구에게 무엇을 넘기는지, 어디가 front-end이고
   어디가 back-end인지. **이게 이 프로젝트의 존재 이유다.**
4. **현장 감각** — 시험과 실무 양쪽 대비. `<details>`로 답을 접어둔다.
   "이 상황에서 어떤 판단을 내리나" 형태. 계산 문제가 아니라 **분류와 판단** 문제다.
5. **함정과 혼동** — 헷갈리는 이웃 용어, 회사마다 다른 이름, 흔한 오해. `.trap` 블록.
   사용자가 가장 가치 있게 여기는 부분.

마지막 섹션은 항상 **정리 & 다음 강의**: 한 장 요약 표 + Lab/Quiz 대응 + 다음 강의 예고.

## `.jargon` — 용어 뜯어보기

**이 노트의 차별점이다.** EEE 554의 `.nota`(기호 뜯어보기)가 있던 자리를 대신한다.

사용자는 Verilog를 쓸 줄 알지만 **"tapeout 전에 ECO를 쳤다"** 같은 문장은 못 읽는다.
개념이 어려운 게 아니라 **그 말이 어느 세계의 말인지 몰라서** 막힌다. 그 말만 따로 푼다.

```html
<details class="jargon" open>
  <summary><span lang="ko">용어 뜯어보기 · ECO</span><span lang="en">Unpacking the jargon · ECO</span></summary>
  <div class="body">
    <table class="parts">
      <tr><td>풀네임</td><td>Engineering Change Order</td></tr>
      <tr><td>한 줄</td><td>합성을 다시 돌리지 않고 netlist를 직접 고치는 것</td></tr>
      <tr><td>언제</td><td>Logic Freeze 이후, tapeout 전</td></tr>
      <tr><td>누가</td><td>설계 엔지니어가 요청하고 승인을 받아야 한다</td></tr>
      <tr><td>헷갈리는 것</td><td>일반 버그 수정과 다르다. RTL을 고치는 게 아니다</td></tr>
    </table>
  </div>
</details>
```

- **기본은 펼쳐둔다(`open`).** 모르는 사람에게 안 보이면 있으나 마나다.
  대신 접을 수 있다. 알고 나면 매번 지나가야 하는 장애물이 되면 안 된다.
- 정의 블록(`.def`)이나 그 용어가 처음 나오는 문단 **바로 다음**에 둔다.
- **다섯 줄을 채운다.** 풀네임 / 한 줄 정의 / 언제 / 누가 / 헷갈리는 것.
  이 중 **"언제"와 "누가"가 이 과목의 핵심**이다. 같은 단어가 단계에 따라 다른 뜻이 되고,
  직군에 따라 다른 이름으로 불린다. 사전적 정의만 적으면 노트를 만든 의미가 없다.
- 약어는 **풀네임을 반드시 적는다.** DUT를 "테스트 대상"이라고만 적고 넘어가지 않는다.
  Device Under Test라는 걸 알아야 문서에서 마주쳤을 때 읽힌다.
- 같은 용어를 두 번 풀지 않는다. **처음 나오는 곳에서 풀고, 뒤에서는 그리로 링크한다.**
  강의를 건너뛰어 링크할 때는 `href="L02-....html#s7"` 형태로 다른 파일도 가리킨다.
  `verify.mjs`가 대상이 실제로 있는지 검사한다.
- 새 강의에서도 **정의에 처음 보는 용어가 있으면 같이 넣는다.** 나중에 몰아서 하지 않는다.

### 회사마다 다른 이름

이 과목의 시그니처 함정이다. L01 s25에 Intel / Freescale-NXP / NVIDIA가 같은 일을
**서로 다른 이름으로 부르는 표**가 실제로 있다. NVIDIA의 "Pre-Si Validation"이
Intel에서는 "Emulation"이다.

**용어가 회사마다 갈리면 `.trap`으로 따로 뺀다.** `.jargon` 안에 묻으면 안 된다.
면접과 이직에서 실제로 사고 나는 지점이고, 사용자가 이 노트를 쓰는 이유에 직결된다.

## 약어 사전 (`glossary.html`)

`.jargon`은 **강의 → 용어** 방향이다. 읽다가 "아 ECO가 이거구나"를 알려준다.
공부할 때는 이게 맞지만, **문서나 코드를 펴놓고 앉았을 때는 방향이 반대다.**
"BFM이 뭐였지"에 답하는 곳이 따로 필요하다.

**별도 페이지로 만든다.** 인라인으로는 구조적으로 안 되기 때문이다.
용어가 강의 30개에 흩어지므로 어느 노트에도 전체 목록이 생길 수 없다.

- **알파벳순으로 정렬한다.** 강의순이 아니다. 진입점이 약어 그 자체이기 때문이다.
- 항목마다: **풀네임 / 한 줄 정의 / 처음 나온 강의로 가는 링크.**
  자세한 설명은 복제하지 않고 링크로 보낸다. 양쪽에 두면 갈라진다.
- 검색 상자를 둔다. 목록이 길어지면 스크롤로는 못 찾는다. 브라우저 저장소는 쓰지 않는다.
- `data-slide`를 붙이지 않고 `reader.js`도 넣지 않는다.
- **강의 노트를 쓸 때마다 같이 갱신한다.** 나중에 몰아서 하면 반드시 빠뜨린다.

## 함정 섹션 작성 원칙

이게 노트의 차별점이므로 대충 쓰지 않는다.

- **혼동되는 이웃 용어를 짝으로 잡는다.** 이 과목의 함정은 대부분 이 모양이다.
  Verification vs. Testing vs. Validation. Architecture vs. Microarchitecture vs. Design.
  Simulation time vs. Wall clock time. Code coverage vs. Functional coverage.
  Lint vs. Compile error. **"둘 다 맞는 말인데 가리키는 게 다른" 경우가 제일 위험하다.**
- **구별 기준을 하나로 못 박는다.** "언제 하는가"인지 "무엇을 잡는가"인지 "누가 하는가"인지.
  기준을 안 밝히고 나열하면 읽고 나서도 구별이 안 된다.
  Verification/Testing은 **"만들기 전이냐 후냐"** 하나로 갈린다. 그 한 줄을 먼저 준다.
- 시험에서 실제로 틀릴 만한 것 위주. quiz가 MCQ라서 **정확히 이런 짝이 문제로 나온다.**
- **회사마다 다른 이름은 반드시 짚는다.** 위 참조.
- **"왜 이걸 배우는지"를 함정 섹션 마지막에 넣으면 효과가 좋다.**

## 강의 간 연결

**필수 작업이다.** 각 강의에서 이전 강의의 개념이 실제로 어디서 일하는지 명시적으로 짚는다.
이 과목은 30강이 SoC 설계 → SoC 검증이라는 한 줄기로 이어지는데,
**강사가 "lab 순서 때문에 좀 어수선할 것"이라고 미리 밝혔다** (L01 s9).
그래서 연결을 노트가 대신 만들어줘야 한다.

- `.callout` 블록으로 "Lecture N의 X가 여기서 일한다" 형태로 쓴다.
- **Design Flow 그림(L01 s13-16)이 이 과목 전체의 지도다.** 새 강의를 쓸 때
  "이 강의는 그 그림의 어디인가"를 00번 섹션에서 먼저 말한다.
- 마지막 정리 섹션에 이전 강의 ↔ 현재 강의 대응표를 넣으면 좋다.

## Lab과 Quiz 처리 원칙

성적 비중이 **Lab 45% / Exam 30% / Quiz 20% / Participation 5%**다.
숙제가 아니라 **Lab이 이 과목의 중심**이다. EEE 554와 가장 크게 다른 점이다.

- Lab은 **6개**. 앞 3개가 설계(FIFO, Pipelined MIPS, Systolic Matmul),
  뒤 3개가 검증(FIFO Checker+DPI, MIPS Random Stimulus+Coverage, APB agent+Assertions).
- **2인 1조**이고 **AI 도구 사용이 허용**되며 AI 사용 내역을 제출물에 적어야 한다.
- 제출 정책이 특이하다: **늦으면 24시간당 15% 감점(최대 3구간), 일찍 내면 24시간당 5% 가산점(최대 10%).**
  이건 노트 헤더 chip과 Lab 공략 페이지에 명시한다. 놓치면 그냥 점수를 버리는 것이다.
- Quiz는 **6개**, Canvas + Lockdown Browser, **AI 사용 금지**, MCQ와 코딩 문제.
  강의 내용 기반이므로 **각 강의 노트 마지막에 "이 강의에서 quiz로 나올 만한 것"을 적는다.**

### Lab 공략 페이지 (`LAB{N}-*.html`)

과제를 펴놓고 앉았을 때 "이거 풀려면 뭘 봐야 하지"에 답하는 곳.

- 파일명은 `LAB{N}-{과제 제목 kebab-case}.html`. 과제 문서 제목을 그대로 쓴다.
- **요구사항 항목 순서로 정렬한다.** 개념순이 아니다. 진입점이 요구사항이기 때문이다.
- 항목마다 네 가지: **필요한 개념 → 노트 링크 / 첫 수 / 빠뜨리기 쉬운 것 / 제출물**.
- **과제 원문을 그대로 싣지 않는다.** repo가 Public이라 인터넷에 게시하는 것이다.
  요구사항 요약 수준으로 쓴다. 채점 방침처럼 인용이 필요한 대목만 짧게 따온다.
- **AI 사용 기록 제출 요구를 공략에 적는다.** 코드만 내고 이걸 빠뜨리면 감점이고,
  실제로 빠뜨리기 딱 좋은 항목이다.
- `data-slide`를 붙이지 않고 `reader.js`도 넣지 않는다.

`verify.mjs`의 HW 번호 대조 검사는 `HW*.html`을 찾는다. **Lab 페이지를 만들 때
`LAB*.html`도 보도록 스크립트를 고친다.** 안 고치면 조용히 검사가 안 돈다.

## HTML 기술 규격

### 자체완결형

**CDN 금지.** 네트워크에서 뭔가를 받아오는 코드를 쓰지 않는다.
노트 본문의 CSS, SVG, JS는 전부 그 HTML 파일 하나에 인라인한다.
오프라인에서 열어도 노트는 완전히 동작해야 한다.

예외는 PDF 리더 하나뿐이다. `vendor/pdf.js/`와 `slides/*.pdf`는 repo 안에 있는
로컬 파일이므로 "외부 의존성 없음"은 유지된다. 다만 **리더는 없어도 되는 부가 기능이다.**
`vendor/`나 `slides/`가 없거나 로드에 실패해도 노트 본문은 그대로 읽혀야 한다.

### 코드 표기

이 과목은 수식 대신 **SystemVerilog 코드**가 나온다. EEE 554의 `.m` / `.eq`는 거의 안 쓴다.

```html
<code>always_ff</code>                          <!-- 인라인 식별자 -->
<pre class="code"><span class="k">assert property</span> (@(<span class="k">posedge</span> clk) start ##2 transfer);</pre>
```

- **하이라이팅은 손으로 `<span>`을 넣는다.** 라이브러리를 쓰지 않는다 (CDN 금지).
  칠하는 것은 키워드(`.k`), 문자열(`.s`), 주석(`.c`), 숫자(`.n`) 넷뿐이다. 더 늘리면 유지가 안 된다.
- **색은 토큰으로만 준다.** `.k{color:var(--violet)}` 처럼. 하드코딩하면 다크모드에서 안 바뀐다.
- `<pre class="code">`는 **가로 스크롤을 자기 안에서 처리한다.** `overflow-x:auto`.
  안 그러면 모바일에서 페이지 전체가 가로로 밀린다. `verify.mjs`가 이걸 잡는다.
- 슬라이드의 코드는 **오타까지 그대로 옮기지 않는다.** 실제로 L02 s5의 예제 코드가
  `and_gate g(.(), .(), .())` 처럼 포트 이름이 비어 있다. 슬라이드가 개념 설명용으로
  줄인 것이므로, 노트에서는 동작하는 형태로 고쳐 쓰고 **슬라이드는 이렇게 줄여 썼다고 밝힌다.**
- 신호 파형이나 타이밍은 코드가 아니라 **SVG로 그린다.** 아스키 아트를 쓰지 않는다.

### 디자인 토큰 (모든 파일 공통)

색마다 **RGB 성분을 따로 둔다.** 도해에서 같은 색을 여러 농도로 쓰기 때문이다.
이렇게 해두면 다크모드에서 RGB 하나만 바꿔도 모든 농도 변형이 같이 따라온다.

```css
--blue-rgb:18,80,196;
--blue:rgb(var(--blue-rgb));
/* 농도 변형은 rgba(var(--blue-rgb),.16) 형태로 쓴다 */
```

`index.html`, `glossary.html`, `L01`, `L02`의 `:root` 블록은 **한 글자도 다르지 않게 동일**하다.
새 파일도 그대로 복사한다. 여기 없는 변수를 새로 만들지 않는다.

**EEE 554 저장소의 토큰에서 딱 하나가 다르다.** `--brown`이 리터럴이었는데 여기서는
`--brown-rgb:163,83,43`(다크 `201,138,90`) + `--brown:rgb(var(--brown-rgb))`로 쪼갰다.
back-end와 물리 쪽을 brown으로 칠하면서 `rgba(var(--brown-rgb),.13)` 같은 농도 변형이
필요해졌기 때문이다. 이 하나 말고는 값이 같다.

**스타일 블록은 손으로 복사하지 않는다.** L01에서 뽑아서 다른 파일에 끼워 넣는다.
그래야 세 파일이 갈라지지 않는다.

```bash
python -c "import io; s=io.open('L01-course-intro.html',encoding='utf-8').read();   io.open('/tmp/style.html','w',encoding='utf-8').write(s[s.index('<style>'):s.index('</style>')+8])"
```

`.play` 안에서 쓰는 `.presets`와 `.verdict`도 이 공통 블록에 들어 있다.
인터랙티브 도구를 새로 만들 때 스타일을 따로 정의하지 말고 이걸 쓴다.

**SVG 안에서도 CSS 변수를 쓴다.** `fill="var(--blue)"`는 프레젠테이션 속성에서도 정상 동작한다.

**색을 하드코딩하지 않는다.** 하드코딩하면 다크모드에서 그 부분만 안 바뀐다.
`verify.mjs`가 소스에서 리터럴 색을 잡아 실패시킨다.
**예외는 `<mask>` 안뿐이다.** 마스크의 `#000`/`#fff`는 색이 아니라 알파 채널이다.

### 의미 고정 색상

**EEE 554와 의미가 다르다.** 저기는 집합 A/B/C였다. 여기는 **직군과 단계**다.

| 대상 | 색 |
|---|---|
| Design 쪽 (RTL, 설계자, front-end 산출물) | `--blue` |
| Verification 쪽 (testbench, DUT 바깥, 검증 엔지니어) | `--pink` |
| 도구와 자동화 (synthesis, STA, lint, simulator, EDA tool) | `--violet` |
| 통과·정답·sign-off | `--green` |
| 버그, 함정, 실패, 틀린 것 | `--amber` |
| 물리·back-end (P&R, mask, fab, silicon) | `--brown` |
| 이 강의 범위 밖 / 나중에 배울 것 | `--ink3` |

**이 규칙이 지켜지면 독자가 색만 보고 "이건 설계쪽 일" / "이건 검증쪽 일"을 읽게 된다.**
Design Flow 그림, testbench 구성도, "무엇이 언제 일어나는가" 타임라인이 전부 같은 색 체계를
쓰므로 세 그림이 한 이야기로 붙는다. 이게 이 노트의 시그니처다.

**규칙을 어기면 인접한 도해끼리 색이 충돌한다.** 새 도해를 그릴 때뿐 아니라
**기존 도해를 손볼 때도 색이 규칙에 맞는지 확인한다.**
자동 검사는 색이 토큰인지만 보지 의미까지는 못 본다.

## 다크모드

기본은 OS 설정(`prefers-color-scheme`)을 따르고, 좌하단 버튼으로 덮어쓸 수 있다.

- 다크 팔레트는 `@media (prefers-color-scheme:dark){:root:not([data-theme="light"])}`와
  `:root[data-theme="dark"]` 두 곳에 같은 값을 적는다. 앞은 자동, 뒤는 수동 전환용.
- **의미 고정 색상의 의미는 유지하고 밝기만 올린다.** Design은 여전히 파랑, Verification은 분홍이다.
- 토글 상태는 **저장하지 않는다.** 브라우저 저장소 금지 규칙 때문에 페이지를 옮기면
  다시 OS 설정을 따른다.
- 슬라이드 PDF는 원본 문서라 다크모드에서도 흰 종이 그대로 둔다.

### 블록 클래스

| 클래스 | 용도 | 시각 |
|---|---|---|
| `.def` | 정의 | 검은 좌측 바 |
| `.jargon` | **용어 뜯어보기 (기본 펼침)** | 점선 테두리 + 회색 배경 |
| `.trap` | 함정, 혼동되는 용어 | amber 배경 + 좌측 바 |
| `.ex` | 현장 감각 문제 (내부에 `<details>` 답) | 흰 카드, 파란 태그 |
| `.callout` | 강의 간 연결, 강조 | 상하 실선 |
| `pre.code` | SystemVerilog 코드 블록 | 회색 배경, 가로 스크롤 |
| `figure` + `figcaption` | SVG 도해 | 흰 카드 |
| `.mini` | 작은 SVG 카드 (grid2/3/4 안에) | 흰 카드 |
| `.play` | 인터랙티브 도구 | 흰 카드 |

기존 `L01`, `L02` 파일의 `<style>` 블록을 그대로 복사해서 시작하고, 필요한 것만 추가한다.

### SVG 규칙

- 항상 `viewBox` 지정, `width`/`height` 속성은 쓰지 않는다 (CSS가 100% 폭 처리).
- `role="img"` + `aria-label` 필수.
- 텍스트는 `.svgtxt`(본문), `.svglab`(모노, 라벨), `.svgnum`(모노, 숫자) 클래스 사용.
  **이 과목은 수식이 없으므로 `.svgtxt`도 세리프가 아니라 산세리프로 둔다.**
  블록도와 흐름도에 세리프를 쓰면 도면이 아니라 논문처럼 보인다.
- **크기와 색은 반드시 인라인 `style`로 준다. 프레젠테이션 속성은 클래스에 진다.**
  `.svgtxt{font-size:15px}`이 있으므로 `font-size="24"`는 무시된다.
  `style="font-size:24px"`로 쓴다.
- **좌표는 짐작하지 말고 재서 맞춘다.** `<g transform="translate(…)">`로 패널을 늘어놓은
  도해에서는 `getBBox()`가 조상의 transform을 반영하지 않으므로
  **`getBoundingClientRect()`를 쓴다.**
- **여러 패널을 가로로 늘어놓을 때는 간격을 먼저 계산한다.** 패널 폭 × 개수가 viewBox를
  넘으면 패널끼리 겹치고, 사이에 둘 화살표가 놓일 자리가 사라진다.
- **화살표는 방향과 의미를 라벨로 밝힌다.** 이 과목 도해는 대부분 "무엇이 무엇으로 변환되는지"라
  화살표가 주인공이다. 라벨 없는 화살표는 그리지 않는다.
  `<marker>`를 `<defs>`에 두고 재사용한다.
- `<defs>` 안의 id는 파일 내에서 유일해야 한다. 여러 SVG에 같은 id를 쓰면 렌더링이 깨진다.
- 도형 밖으로 텍스트가 나가지 않게 좌표를 계산한다. **검증 스크립트가 이걸 잡는다.**

### 인터랙티브 요소

강의마다 하나씩, 그 강의의 핵심 개념을 손으로 만져볼 수 있는 도구를 만든다.

원칙: **결과를 보여주는 게 아니라 사용자가 조작해서 발견하게 한다.**

이 과목에 맞는 형태 (수식 조작이 아니다):
- **분류기.** 항목을 주고 "이건 Verification인가 Validation인가 Testing인가"를 고르게 하고
  즉시 채점한다. L01의 용어 혼동에 딱 맞는다.
- **단계 탐색기.** Design Flow 위에서 단계를 누르면 산출물, 담당, 도구, 되돌릴 수 있는지를 보여준다.
- **testbench 조립기.** Stimulus → Driver → Monitor → Checker → Coverage를 하나씩 붙여가며
  "이게 빠지면 무엇을 못 잡는가"를 보여준다. 슬라이드 47-51이 실제로 이 순서로 쌓아 올린다.
- **커버리지 시뮬레이터.** 테스트를 몇 개 돌리면 code coverage는 100%인데 functional coverage는
  구멍이 남는 상황을 만들어 보여준다.

브라우저 저장소(localStorage 등) 사용 금지. 모든 상태는 JS 변수로만.

## 슬라이드 리더 (데스크톱 전용)

노트 오른쪽에 강의 슬라이드 PDF를 띄우고, **노트를 스크롤하면 슬라이드가 따라온다.**
`reader.js` / `reader.css` / `vendor/pdf.js/`는 EEE 554에서 그대로 가져온 것이고 수정하지 않았다.
동작 규칙과 구현 세부는 그쪽 `CLAUDE.md`의 "슬라이드 리더" 절이 여전히 유효하다.

노트는 `<script src="reader.js" type="module"></script>` 한 줄만 넣는다.
`reader.css`는 `reader.js`가 직접 주입하므로 `<link>`를 쓰지 않는다.

`file://`로 열면 브라우저가 PDF fetch를 막는다. 로컬에서 리더까지 보려면 서버로 열어야 한다.

```bash
node scripts/serve.mjs      # http://127.0.0.1:4599/
```

**`python -m http.server` 를 쓰면 안 된다.** `.mjs` 를 `text/javascript` 로 안 내보내서
브라우저가 pdf.js 모듈 로드를 거부한다. 리더가 "슬라이드를 불러오지 못했어 /
Failed to fetch dynamically imported module" 만 띄운다. 실제로 이걸로 한 번 헤맸다.
`verify.mjs` 는 자기 서버를 띄우면서 MIME 을 직접 지정하므로 영향이 없다.
GitHub Pages 도 `.mjs` 를 제대로 내보내므로 배포본은 문제없다.

### 앵커 규칙

동기화의 기반은 노트 안에 박아둔 슬라이드 쪽수다. 이건 **노트를 쓸 때 같이 넣는다.**
나중에 몰아서 붙이려 하면 슬라이드를 다시 다 읽어야 한다.

```html
<div class="sec-head" data-slide="14"><span class="sec-num">03</span><h2>Synthesis</h2></div>
<div class="sec-head" data-slide="26-28">…</div>   <!-- 여러 쪽에 걸친 구간 -->
<h3 data-slide="17">Technology Library</h3>         <!-- 섹션보다 잘게 끊고 싶을 때 -->
```

**앵커는 `<section>`이 아니라 `.sec-head`(와 `h3`)에 붙인다.** CSS가 `attr(data-slide)`로
출처 라벨을 직접 만들기 때문이고, `attr()`은 자기 자신의 속성만 읽는다.

- `data-slide`는 **1부터 시작하는 PDF 쪽 번호**다.
  **이 저장소에서는 숨김 슬라이드를 되살려 변환하므로 PDF 쪽 = 슬라이드에 인쇄된 번호 = PPTX
  슬라이드 번호가 전부 같다.** 이건 우연이 아니라 [변환 규칙](#슬라이드-변환-pptx--pdf)이
  만들어낸 성질이므로, 변환 방식을 바꾸면 이 성질이 깨진다는 걸 기억한다.
  그래도 **앵커를 달기 전에 `scripts/pdftext.mjs`로 해당 쪽 텍스트를 확인한다.**
- 슬라이드 내용을 다루는 모든 섹션의 `.sec-head`에 붙인다. 한 섹션이 여러 장에
  걸치면 `h3`에 더 잘게 붙인다. 섹션 범위가 그 안의 `h3` 범위를 포함하는 건 정상이다.
- **앵커를 붙이면 독자에게 출처 라벨이 자동으로 보인다.** 라벨을 손으로 적지 않는다.
- 슬라이드에 없는 내용(보충 설명, 함정, `.jargon`의 "누가/언제" 줄, 인터랙티브 도구)에는
  **붙이지 않는다.** 앵커가 없는 구간은 리더가 직전 앵커를 유지한다.
  이게 "이건 슬라이드 밖 내용"이라는 신호도 된다.
- **한 슬라이드는 그것을 실제로 다루는 곳 한 군데에만 앵커를 단다.**
  범위가 겹치면 역방향 동기화(PDF → 노트)가 어디로 갈지 정해지지 않는다.
  `verify.mjs`가 겹침을 잡는다.
- **노트를 따라 내려갈 때 슬라이드 번호가 뒤로 가면 안 된다.** `verify.mjs`가 경고로 알려준다.
  경고가 나오면 앵커를 고치는 게 아니라 **노트 순서를 슬라이드에 맞추는 걸 먼저 검토한다.**
- 본문에 쓰는 "슬라이드 14~15쪽" 같은 표현은 사람이 읽는 문장이고 `data-slide`는 기계가 읽는
  값이라 역할이 다르다. 다만 **값이 어긋나면 안 된다.**

### 아이스브레이커와 로지스틱스 슬라이드

이 과목 덱에는 학습 내용이 아닌 장이 섞여 있다.
"Let's break the ice", "Logistics", "Kickoff Survey Results", 강사·TA 소개, 섹션 표지.

**노트로 옮기지 않는다.** 그 대신:
- 학기 운영에 실제로 영향을 주는 것(Zoom 대체 주간, Synopsys 로그인 문제, 과제 정책)은
  **`index.html`의 공지 배너**에 모으고 강의 노트에는 넣지 않는다. 유효기간이 있는 정보다.
- 그 쪽들은 앵커가 안 걸리므로 리더에서 **`노트에 없음` 배지**가 붙는다. 이게 정상이다.
  `verify.mjs`도 경고로 알려주는데, 이 경우는 무시해도 되는 경고다.
- 다만 **강사 소개는 한 번은 쓸모가 있다.** Aman Arora가 NVIDIA에서 Design/Verification/
  Architecture를 8년 했다는 것은 "이 수업이 왜 실무 이야기인지"의 근거다. L01 노트의
  00번 섹션에서 한 줄로 처리하고 앵커는 s3에 단다.

## 모듈 목록 (전체 30강)

강의 사이트 Schedule 표 기준. **이 표가 `index.html`의 뼈대다.**
Lab overview 강의(3, 7, 12, 16, 19, 23, 27)는 별도 노트를 만들지 않고 `LAB{N}` 공략 페이지로 간다.

| # | 날짜 | 주제 | 강사 |
|---|---|---|---|
| 1 | 8/24 | Course Intro and Design Flow | Aman Arora |
| 2 | 8/26 | Digital Design and Verif Review | Aman Arora |
| 3 | 8/31 | Lab 0 (EDA Tools) overview | Aman Arora |
| 4 | 9/2 | System Verilog for Design | Aman Arora |
| 5 | 9/7 | Clock and Reset (Timing, CDC, RDC) | Chetan Sudarshan |
| 6 | 9/9 | FIFO design | Igor Miranda |
| 7 | 9/14 | Lab 1 (FIFO) overview | Aman Arora |
| 8 | 9/16 | Pipelined CPU design | Aman Arora |
| 9 | 9/21 | Floating point arithmetic unit design | Prashant Joshi |
| 11 | 9/23 | Efficient design tips + Catch up | Aman Arora |
| 12 | 9/28 | Lab 2 (Pipelined MIPS) overview | Aman Arora |
| 13 | 9/30 | Matrix multiplication accelerator design | Aman Arora |
| 14 | 10/5 | SoC architecture and on-chip interfaces | Aman Arora |
| 15 | 10/7 | Case study: SoC interconnect design | Eric Taylor |
| 16 | 10/12 | Lab 3 (Systolic Matmul) overview | Aman Arora |
| 17 | 10/14 | System Verilog for Verification | Aman Arora |
| 10 | 10/19 | Assertion Based Verification | Aman Arora |
| 18 | 10/21 | Case study: CPU verification | Aman Arora |
| 19 | 10/26 | Lab 4 (FIFO Checker, DPI) overview | Aman Arora |
| 20 | 10/28 | UVM 1 | Joel Feldman |
| 21 | 11/2 | UVM 2 | Joel Feldman |
| 22 | 11/4 | UVM 3 | Joel Feldman |
| 23 | 11/9 | Lab 5 (MIPS Random Stimulus, Coverage) overview | Aman Arora |
| 24 | 11/11 | Efficient verification tips + Catch up | Aman Arora |
| 25 | 11/16 | Case study: High-speed I/O design and verification | Aman Arora |
| 26 | 11/18 | Case study: SoC verification | Brendan Donahe |
| 27 | 11/23 | Lab 6 (Systolic Matmul, APB agent, Assertions) overview | Aman Arora |
| 28 | 11/25 | Formal verification overview | Amin Rezai |
| 29 | 11/30 | Emulation | Vivek Tiwari |
| 30 | 12/2 | Testing | Aman Arora |

**Lecture 10과 11의 번호가 날짜순과 어긋나 있다.** Schedule 표가 그렇게 되어 있고,
강사가 "guest speaker 사정으로 순서가 바뀔 수 있다"고 밝혔다 (L01 s9).
**번호를 따르고 날짜를 병기한다.** 순서를 임의로 고치지 않는다.

**학기 중에 이 표가 바뀐다.** 새 노트를 쓰기 전에 Schedule을 다시 긁어서 대조한다.

## 워크플로우

새 강의 노트를 만들 때:

1. **Drive 원본이 갱신됐는지 확인한다.** 슬라이드 파일이 새로 올라왔거나 바뀌었을 수 있다.
2. **PPTX를 PDF로 변환한다.** 숨김 슬라이드를 포함시킨다.
   `slides/L{NN}-{topic}.pdf`로 저장하고 노트와 stem을 맞춘다.
   `node scripts/pagecount.mjs`로 PPTX 장수와 PDF 쪽 수가 같은지 확인한다. 다르면 변환이 잘못된 것이다.
3. **슬라이드 본문과 발표자 노트를 뽑아 읽는다.**
   `python scripts/pptx-text.py "<pptx>"`. 필요하면 강의 사이트의 Material 링크도 확인한다.
   **읽으면서 어느 개념이 몇 쪽인지 기록해둔다.** 5번에서 `data-slide`로 쓴다.
4. **오늘 나오는 새 용어를 먼저 뽑는다.** 이게 이 과목 노트의 출발점이다.
   각각에 대해 풀네임 / 한 줄 / 언제 / 누가 / 헷갈리는 것을 채울 수 있는지 확인한다.
   못 채우는 게 있으면 그건 아직 이해 못 한 것이다. 슬라이드나 표준 문서로 돌아간다.
5. **`L{NN}-{topic}.html`을 작성한다.** 기존 `L01`/`L02`의 `<style>` 블록을 그대로 복사해서 시작한다.
   각 `.sec-head`에 `data-slide`를 붙인다. 슬라이드에 없는 보충 내용에는 붙이지 않는다.
6. **`glossary.html`을 갱신한다.** 이 강의에서 새로 푼 용어를 전부 넣는다. 미루지 않는다.
7. `node scripts/verify.mjs L{NN}-{topic}.html` 실행. exit code 0이어야 통과다.
   - `shots/` 폴더에 전체 스크린샷 2장과 **도해별 개별 스크린샷** `-fig01.png…`이 생긴다.
   - **도해 스크린샷을 한 장씩 다 열어본다.** 자동 검사가 통과해도 건너뛰지 않는다.
     테두리가 글자를 관통하는 것, 화살표가 엉킨 것, 의미 고정 색상 위반은 눈으로만 잡힌다.
8. **슬라이드 리더가 실제로 따라오는지 확인한다.**

   ```bash
   node scripts/readercheck.mjs L{NN}-{topic}.html s1,s3,s9,s18
   ```

   섹션마다 `data-slide` 와 리더가 실제로 띄운 쪽을 나란히 찍어준다.
   **한두 쪽 뒤진 값이 나오는 것은 정상이다.** 리더의 판정선이 화면 맨 위가 아니라
   조금 아래에 있어서, 섹션 머리가 딱 위에 걸린 순간에는 직전 앵커를 유지한다.
   L01·L02 도 똑같이 나온다. **몇 쪽씩 어긋나면 그때 앵커를 의심한다.**

   손으로 볼 때는 `node scripts/serve.mjs` 로 띄우고 노트를 위에서 아래로 훑는다.
   브라우저 콘솔에서 섹션으로 뛰어 대조하면 빠르다.

   ```js
   document.getElementById('s12').scrollIntoView();
   // 잠깐 기다린 뒤 리더의 쪽 번호를 읽는다
   document.querySelector('aside').innerText.split('
').slice(0,3).join(' ')
   ```

   **어긋난 앵커는 있으나 마나가 아니라 적극적으로 해롭다.** 근거를 잘못 가리킨다.
   **포트를 바꿔가며 확인한다.** 한 번 잘못된 MIME 으로 받은 `.mjs` 는 브라우저 캐시에
   남아서, 서버를 고쳐도 같은 주소로는 계속 실패한다. 실제로 이걸로 한 번 헤맸다.
9. **`node scripts/langcheck.mjs L{NN}-{topic}.html` 실행.** 영어 모드에 한글이 남으면 실패한다.
   **코드 블록 주석에서 제일 많이 걸린다.** 위 [검사](#검사) 절 참조.
10. 문제가 있으면 고치고 7번 반복.
11. **`index.html`을 갱신한다:**
    - 해당 강의 카드의 `<div class="mod soon">` → `<a class="mod" href="...">`
    - `<span class="status wait">준비 중</span>` → `<span class="status done">읽기</span>`
    - 닫는 `</div>` → `</a>`
    - 태그 목록을 실제 내용에 맞게 갱신
    - 헤더의 "N / 30강" chip 갱신
12. 커밋하고 푸시한다. 커밋 메시지는 한 줄, 영어: `Add Lecture 3: SystemVerilog for design`
    **슬라이드 PDF가 노트보다 늦게 들어가면 안 된다.** 노트만 먼저 올라가면 리더가 404를 받는다.

## 검증

`verify.mjs`는 저장소 루트를 **임시 http 서버로 띄우고** 그 주소로 연다.
`file://`에서는 브라우저가 PDF와 모듈 로드를 막아 리더를 검증할 수 없기 때문이고,
GitHub Pages와 같은 조건으로 맞추기 위해서다.

**자동으로 잡는 것** (하나라도 걸리면 exit 1):
- 페이지 로드 시 JS 콘솔 에러
- 소스에 하드코딩된 색 리터럴 (`<mask>` 안과 `:root` 정의부는 예외)
- SVG `<text>`가 부모 viewBox를 벗어나는 경우
- 중복된 DOM id, 해결되지 않는 `url(#...)` 참조.
  **`<a>` 안에 `<a>`를 넣으면 여기서 걸린다.**
- 모바일(390px) 가로 오버플로우. **`<details>`를 전부 펼친 상태로 잰다.**
  `.jargon`이 기본 펼침이라 여기가 특히 중요하다. `pre.code`도 이 검사에 걸린다.
- 슬라이드 리더가 실제로 떠서 첫 쪽을 렌더하는지
- `data-slide` 값이 PDF 쪽 수를 벗어나는지 (오타 잡기)
- `data-slide` 범위가 서로 겹치는지 (포함 관계는 정상, 부분 겹침만 잡는다)
- 다른 페이지를 가리키는 `href="x.html#id"`의 대상이 실제로 있는지.
  **`glossary.html` ↔ 강의 노트 링크가 여기 걸린다.**
- 본문과 목차 링크가 **라이트/다크 양쪽에서** 배경 대비 3:1 이상인지
- 모든 `<details>`가 **양쪽 언어에서 열리는지** (`<summary>`가 2개면 실패)
- 도해 안에서 **글자끼리 겹치는지**
- 리더가 뜨는 최소 폭에서 본문이 480px 이상 남는지

**경고만 하는 것** (exit code에 영향 없음):
- 도해에서 글자가 다른 그룹의 도형 위에 있는 곳
- 노트를 따라 내려가는데 슬라이드 번호가 뒤로 가는 곳
- 어떤 앵커에도 안 걸린 슬라이드. **이 과목은 아이스브레이커와 표지가 많아서
  이 경고가 정상적으로 여러 건 나온다.** 목록을 보고 진짜 빠뜨린 게 있는지만 확인한다.

**전혀 못 잡는 것**: 설명의 질, 용어 풀이가 실제로 이해되는지, 함정이 진짜 함정인지.
**그리고 용어를 지어냈는지도 못 잡는다.** 이게 이 과목의 가장 큰 위험이다.
사용자 피드백이 유일한 신호다. **완성했다고 단정하지 말고 확인을 요청한다.**

### 모바일 오버플로우가 났을 때

| 원인 | 방어 |
|---|---|
| 그리드 트랙이 `1fr`이라 넓은 자식이 레이아웃 전체를 밀어냄 | `grid-template-columns:minmax(0,1fr)` |
| 표의 min-content가 화면보다 넓음 | `@media(max-width:900px){table{display:block;overflow-x:auto}}` |
| **긴 코드 줄이 안 접힘** | `pre.code{overflow-x:auto}` |
| **`.jargon .parts` 첫 칸이 `nowrap`** | `@media(max-width:900px){.jargon .parts td:first-child{white-space:normal}}` |

세 번째와 네 번째가 이 과목에서 새로 생긴 것이다. EEE 554 스타일 블록에는 없다.

## 커밋하는 것과 안 하는 것

repo는 **Public**이고 GitHub Pages로 서빙된다. 여기 올리는 건 인터넷에 게시하는 것이다.

**강의계획서의 Student Copyright Responsibilities가 이렇게 적고 있다:**

> Students may not share outside the class, including uploading, selling or distributing
> course content or notes taken during the conduct of the course.

**사용자에게 이 조항을 알렸고, 슬라이드를 커밋하기로 결정했다.**
결정은 사용자의 것이므로 그대로 진행하되, **footer에 저작권 귀속을 반드시 밝힌다**
(아래 [footer 문구](#footer-문구) 참조). 이 결정을 조용히 뒤집지 않는다.
사용자가 나중에 내려달라고 하면 `slides/` 커밋을 지우고 `.gitignore`에 `slides/*.pdf`를
추가하면 된다. 리더는 슬라이드가 없어도 노트 본문을 막지 않게 되어 있다.

`.gitignore`:
```
node_modules/
shots/
package-lock.json
*.pdf
!slides/*.pdf
```

`*.pdf`로 전부 막고 `!slides/*.pdf`로 슬라이드만 되살린다.

| 파일 | 커밋 |
|---|---|
| `slides/L{NN}-*.pdf` (강의 슬라이드) | O |
| `vendor/pdf.js/` | O |
| `*.pptx` 원본 | **X.** PDF만 올린다. 발표자 노트가 딸려 들어간다 |
| Lab 문제지, 제출 코드 | **X.** 2인 1조 과제다. 학문적 정직성 문제로 직결된다 |
| Quiz, Exam 문제 | X |
| `shots/`, `node_modules/` | X |

**PPTX를 커밋하지 않는 이유를 한 번 더.** 발표자 노트에는 강사가 수업에서 할 말이 초안 상태로
들어 있다. PDF로 변환하면 노트가 빠지므로 PDF만 올린다. 스크래치패드의 PPTX 사본도
repo 안에 두지 않는다.

커밋 전에 `git status`로 의도하지 않은 파일이 스테이징됐는지 확인한다.

### footer 문구

각 노트와 `index.html` footer에 이렇게 밝힌다:

- 강의 슬라이드의 저작권은 담당 강사(Aman Arora)와 ASU에 있다는 것
- 이 사이트는 수강생이 만든 개인 학습 자료이고 공식 강의 자료가 아니라는 것
- 노트 본문은 슬라이드를 재구성하고 보충한 것이라는 것
- **교재 줄을 넣지 않는다.** 이 과목은 교재가 없다. 없는 것을 적으면 안 된다.
  대신 강의 사이트 링크를 둔다.

## 상단 미니 헤더

노트가 길어서 한참 내리면 큰 제목이 안 보인다. 그래서 목차 맨 위에 작은 헤더를 둔다.

- 내용: `← 강의 목록` 링크 / `LECTURE N` / 영문 제목.
  **제목은 `header.top`의 `h1.title`에 있는 영문 그대로 쓴다.** 번역하거나 줄이지 않는다.
- **목차(`nav.toc`)가 이미 sticky이므로 그 안에 넣는다.** 별도의 고정 장치를 만들지 않는다.
- `header.top`의 `h1.title`을 IntersectionObserver로 감시해서, 화면에서 사라지면 `.on`을 붙인다.
- 모바일에서는 목차가 static이라 의미가 없으므로 숨긴다.
- **강의 목록으로 돌아가는 링크는 헤더와 미니 헤더 양쪽에 있어야 한다.**

## 이중 언어 (한국어 / 영어)

한 파일 안에 두 언어를 나란히 두고 보이는 쪽만 남긴다. 좌하단 버튼으로 전환한다.

```html
<p lang="ko">…</p>
<p lang="en">…</p>
```

- **도해·앵커·CSS·리더를 공유하므로 두 언어의 구조가 어긋날 수 없다.** 파일이 커지는 게 비용이다.
- SVG 텍스트도 같은 좌표로 두 벌 겹쳐 둔다.
- **언어 규칙에는 `!important`가 필요하다.** 더 구체적인 선택자가 `display:none`을 되살린다.
- **`<details>` 하나에 `<summary>`를 두 벌 넣지 않는다.** 개폐 버튼이 되는 건 첫 번째
  `<summary>` 하나뿐이라, 두 벌을 넣으면 숨겨지는 언어에서 **내용에 영원히 도달할 수 없다.**
  `<summary><span lang="ko">…</span><span lang="en">…</span></summary>`로 쓴다.
  **`.jargon`이 전부 이 형태다.** 여기서 실수하면 노트의 핵심 장치가 통째로 안 열린다.
- **`data-slide`가 붙은 `h3`를 두 벌로 만들면 앵커가 중복된다.** 숨겨진 쪽은
  `getBoundingClientRect()`가 전부 0이라 리더가 "화면 맨 위"로 오인한다.
- JS가 찍는 문자열은 `L(ko, en)` 헬퍼로 처리하고, `langchange` 이벤트에서 다시 그린다.

### 영어 문체

**번역문이 아니라 처음부터 영어로 쓴 글이어야 한다.** 한국어 어순을 따라가지 않는다.

- 2인칭 대화체. 축약형(you'll, that's, it's)을 쓴다.
- em dash 금지는 영어에도 적용한다.
- **업계 용어는 원래대로 영어 유지.** 한국어판에서 영어로 둔 용어가 영어판에서 달라지면 안 된다.
- **`.jargon`의 영어판은 한국어판보다 짧아진다.** 풀네임과 한 줄 정의는 영어권 독자에게
  이미 절반이 자명하기 때문이다. **그래도 "언제 / 누가 / 헷갈리는 것"은 반드시 남긴다.**
  그게 이 블록의 값어치다.

### 검사

번역 누락은 눈으로 못 잡는다. 스크립트로 확인한다.

```bash
node scripts/langcheck.mjs L{NN}-{topic}.html    # exit 0 이어야 통과
```

- 영어 모드로 바꾸고 `lang="ko"` 조상이 없는데 한글이 남은 요소를 찾는다.
- **`<html lang="ko">` 때문에 `closest('[lang="ko"]')`가 모든 요소에서 참이 된다.**
  루트를 제외해야 한다.
- **SVG 요소에는 `offsetParent`가 없다.** 가시성은 계산된 `display`로 판정한다.
- **`dataset.lang` 을 직접 바꾸면 안 된다. 토글 버튼을 눌러야 한다.** `langchange` 이벤트가
  안 돌면 인터랙티브 도구와 glossary 의 항목 수처럼 **JS 가 찍는 문자열이 한국어로 남아**
  가짜 실패가 무더기로 나온다.
- 좌하단 토글 버튼 두 개(`.lang-btn`, `.theme-btn`)는 일부러 한국어이므로 검사에서 뺀다.

### 코드 블록의 주석도 번역 대상이다

이게 놓치기 제일 쉽다. `pre.code` 안의 **한국어 주석은 영어 모드에서 그대로 남는다.**
이 과목은 코드가 많아서 한 강의에 열 개 넘게 생긴다. 두 가지 방법이 있다.

- 주석만 짝을 짓는다: `<span class="c"><span lang="ko">// …</span><span lang="en">// …</span></span>`
  대부분 이걸로 충분하고 파일도 덜 커진다.
- **코드 자체가 언어별로 다르면** (설명용 주석이 코드 줄마다 붙는 경우) `<pre class="code" lang="ko">`
  와 `lang="en">` 두 벌을 둔다. **두 벌을 두고 `lang` 을 안 붙이면 영어 모드에서 둘 다 보인다.**
