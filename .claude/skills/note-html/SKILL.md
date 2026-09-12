---
name: note-html
description: 이 저장소의 노트 HTML 을 만들거나 고칠 때 쓴다. 디자인 토큰, 의미 고정 색상, 블록 클래스, SVG 규칙, 코드 표기, 다크모드, 이중 언어, 미니 헤더, 슬라이드 리더 앵커, 파일 명명까지. 기존 노트의 문구나 도해만 손볼 때는 이 스킬 하나로 끝난다. "노트 고쳐 / 도해 추가 / 다크모드 / 앵커 / 레이아웃 깨짐"에서 호출한다.
---

# 노트 HTML 저작 규격

**같이 필요한 스킬**
- 새 강의 노트를 처음부터 쓰는 거면 `write-note` 를 먼저 읽는다. 거기가 무엇을 쓸지를 정하고
  여기는 어떻게 만들지만 정한다
- 슬라이드 PDF 가 아직 없으면 `convert-slides`

**이 스킬만으로 끝나는 것**: 기존 노트의 문구 수정, 도해 추가·수정, 레이아웃·다크모드 문제 해결

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

이 표가 `CLAUDE.md` 의 불변식과 어긋나면 `CLAUDE.md` 가 이긴다.

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

## 상단 미니 헤더

노트가 길어서 한참 내리면 큰 제목이 안 보인다. 그래서 목차 맨 위에 작은 헤더를 둔다.

- 내용: `← 강의 목록` 링크 / `LECTURE N` / 영문 제목.
  **제목은 `header.top`의 `h1.title`에 있는 영문 그대로 쓴다.** 번역하거나 줄이지 않는다.
- **목차(`nav.toc`)가 이미 sticky이므로 그 안에 넣는다.** 별도의 고정 장치를 만들지 않는다.
- `header.top`의 `h1.title`을 IntersectionObserver로 감시해서, 화면에서 사라지면 `.on`을 붙인다.
- 모바일에서는 목차가 static이라 의미가 없으므로 숨긴다.
- **강의 목록으로 돌아가는 링크는 헤더와 미니 헤더 양쪽에 있어야 한다.**

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
  슬라이드 번호가 전부 같다.** 이건 우연이 아니라 `convert-slides` 스킬의 변환 규칙이
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

## 파일 명명

```
index.html                                        허브 (모듈 목록). 루트에 남는다

notes/                                            노트는 전부 여기 모은다
  glossary.html                                   약어·용어 사전 (아래 참조)
  L01-course-intro.html                           Lecture 1
  L02-design-and-verification-overview.html       Lecture 2
  L03-system-verilog-for-design.html              Lecture 3
  L04-clock-and-reset.html                        Lecture 4
  L{NN}-{kebab-case-영문주제}.html
  LAB{N}-{kebab-case-과제제목}.html               Lab 공략 (아래 참조)

slides/L01-course-intro.pdf                       Lecture 1 슬라이드 (노트와 같은 stem)
slides/L02-design-and-verification-overview.pdf

lab/lab0/README.md                                Lab 작업 기록
lab/lab0/report.md                                제출 리포트
lab/lab0/materials/                               공개 금지. gitignore 된다 (아래 참조)

reader.js  reader.css                             슬라이드 리더 (모든 노트가 공유)
vendor/pdf.js/                                    pdf.js 런타임
```

**노트는 `notes/` 안이고 `index.html`만 루트다.** GitHub Pages 진입점이라 옮길 수 없다.
30강이 다 차면 루트에 HTML 이 35 개 쌓이므로 미리 갈라놨다.

- `index.html` 에서 노트로 갈 때는 `href="notes/L01-....html"`.
- 노트에서 허브로 돌아갈 때는 `href="../index.html"`, 리더는 `src="../reader.js"`.
- **노트끼리의 링크와 glossary 링크는 같은 폴더라 그대로다.** `href="L02-....html#s7"`.
- `slides/` 와 `reader.js` 는 루트에 남는다. `reader.js` 가 슬라이드 경로를
  `new URL('./slides/...', import.meta.url)` 로 잡으므로 노트가 어디 있든 루트를 가리킨다.
  **이 한 줄이 EEE 554 에서 가져온 `reader.js` 를 이 저장소에서 고친 유일한 곳이다.**
  상대 경로로 되돌리면 `notes/slides/...` 를 찾아 404 가 난다.

`{NN}`은 **`docs/schedule.md` 의 강의 번호**를 따른다. **Lab overview 는 강의로 세지 않는다.**
그래서 강의가 23 개이고, 이 번호는 **강사가 PPTX 앞에 붙인 번호와 일치한다.**
`03_System Verilog for Design.pptx` 가 3 강이고 `04_Clock_Reset_Chetan.pptx` 가 4 강이다.

강의 사이트 Schedule 은 Lab 을 함께 세므로 번호가 다르다. `docs/schedule.md` 의 `site` 열이
그 번호이고 **사이트와 대조할 때만 쓴다.** 사이트 번호는 10 과 11 이 날짜순과 어긋나 있는데
여기서는 날짜순으로 정리되어 그 문제가 사라졌다.

**Lab 은 `LAB{N}` 으로 따로 센다.** Lab 0~6 이고 강의 번호를 달지 않는다.

**슬라이드 사본은 노트와 stem을 맞춰서 이름을 바꾼다.** `02_Design and Verification Overview.pptx`
→ `slides/L02-design-and-verification-overview.pdf`. 그러면 `reader.js`가 노트 파일명에서
슬라이드 경로를 바로 유도하므로 하드코딩된 매핑 표가 필요 없다.

### scripts/

| 스크립트 | 하는 일 |
|---|---|
| `crop.mjs` | 스크린샷 일부만 잘라 보기 |
| `serve.mjs` | 로컬 서버. `.mjs` MIME 을 제대로 내보낸다 (아래 [슬라이드 리더](#슬라이드-리더-데스크톱-전용) 참조) |

## 모바일 오버플로우가 났을 때

| 원인 | 방어 |
|---|---|
| 그리드 트랙이 `1fr`이라 넓은 자식이 레이아웃 전체를 밀어냄 | `grid-template-columns:minmax(0,1fr)` |
| 표의 min-content가 화면보다 넓음 | `@media(max-width:900px){table{display:block;overflow-x:auto}}` |
| **긴 코드 줄이 안 접힘** | `pre.code{overflow-x:auto}` |
| **`.jargon .parts` 첫 칸이 `nowrap`** | `@media(max-width:900px){.jargon .parts td:first-child{white-space:normal}}` |

세 번째와 네 번째가 이 과목에서 새로 생긴 것이다. EEE 554 스타일 블록에는 없다.

## 검증 루프

도해나 레이아웃을 고쳤으면 끝나기 전에 돌린다. 명령과 판정 기준은 `write-note` 스킬의
"검증 루프" 절이 단일 출처고, 여기는 그중 도해·레이아웃 수정에 필요한 것만 추린다.

```bash
node scripts/verify.mjs <노트 파일>
node scripts/langcheck.mjs <노트 파일>
```

`shots/` 에 생긴 도해별 스크린샷을 한 장씩 전부 눈으로 연다. 자동 검사가 통과해도 건너뛰지 않는다.
앵커(`data-slide`)를 건드렸으면 `node scripts/readercheck.mjs <노트 파일> s1,s3,...` 도 돌린다.
