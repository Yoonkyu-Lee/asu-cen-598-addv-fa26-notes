---
name: synopsys-training
description: Synopsys Learning Center(training.synopsys.com)의 강좌를 헤드 브라우저로 열고 슬라이드·나레이션·화면 텍스트를 뽑아낼 때 쓴다. 로그인 유지, SCORM 프레임 진입, 플레이어 3종 판별, 완료 판정, 수집물 보관 규칙까지. "Synopsys 트레이닝 보자 / 강좌 수집 / VCS·Verdi·DC 트레이닝"에서 호출한다.
---

# Synopsys 트레이닝 탐방과 수집

Synopsys Learning Center 강좌를 읽고 자료를 뽑는 절차. **시행착오로 알아낸 것만 적었다.**
여기 적힌 함정은 전부 실제로 한 번씩 밟은 것이다.

## 0. 먼저 정하라: 무엇을 위한 수집인가

- **개인 정독**이면 목차를 훑고 관심 레슨만 본다. 아래 3~5절만 필요하다.
- **노트 작성용 원문 확보**면 레슨 전체를 기계적으로 훑는다. 6절의 루프를 쓴다.
- **과제 제출용 완료 증거**면 7절의 완료 판정이 핵심이다. 수집과 완료는 별개다.

## 1. 자료 취급 규칙 (먼저 읽어라)

덱 안에 **배포 금지가 명시돼 있다.** VCS 덱의 `II. Confidential information` 슬라이드 원문:

> You are not permitted to disseminate or use any of the information provided to you in this
> presentation outside of Synopsys without prior written authorization.

**수집물은 전부 `lab/**/materials/` 아래에 둔다.** 그 경로는 `.gitignore` 로 막혀 있다.
공개 노트(`notes/*.html`)에는 슬라이드 이미지도 나레이션 문장도 옮기지 않는다.
배운 개념을 직접 다시 쓰고 근거는 공개 자료(User Guide, IEEE 표준, Synopsys 공개 YouTube)로 단다.

Verdi 강좌의 Demo 구간은 영상 안에 데모가 없고 **공개 YouTube 채널("Synopsys Unified Debug")로 보낸다.**
공개 노트에 걸 수 있는 몇 안 되는 출처다.

## 2. 브라우저 띄우기

**`claude --chrome` 으로 들어왔고 `browse` 를 못 살리겠으면 `synopsys-training-chrome` 으로 간다.**
다만 Chrome 도구는 cross-origin iframe 안에 못 들어가서 4~6 절이 통째로 안 먹고,
장당 스크린샷이라 비용이 크다. **덱 전체를 훑을 일이면 여기서 `browse` 를 되살리는 게 거의 항상 싸다.**

```bash
B="$HOME/.claude/skills/gstack/browse/dist/browse.exe"   # Windows. 확장자 없는 이름은 v1.84 에 없다
"$B" status          # Mode: headed 여야 정상
"$B" connect         # 아니면 이걸로 띄운다
```

로그인은 `~/.gstack/chromium-profile` 에 남아서 **재기동해도 유지된다.** ASU SSO 의 Duo 2FA 쿠키까지 산다.
사용자의 실제 Chrome 은 건드리지 않는다.

**`Mode: launched` 로 나오면 headed 세션의 인증 토큰이 날아간 상태다.**
상태가 `.gstack/browse.json` 한 파일에만 있어서, 다른 명령이 새 headless 서버를 띄우며 덮어쓴다.
**이 버그는 gstack `v1.55.0.0` (#1781) 에서 고쳐졌고 설치본은 `v1.84.1.0` 이라 해당 없다.**
그래도 증상이 보이면 유령 서버를 정리하고 다시 띄운다.

```bash
netstat -ano | grep ":34567 " | grep LISTENING      # 잡고 있는 PID
taskkill //PID <pid> //T //F
rm -f .gstack/browse.json
"$B" connect
```

### 세션 만료를 강좌 미등록으로 오해하지 마라

세션이 끊기면 조용히 `/learn/signin` 으로 리다이렉트된다. 그 상태로 강좌를 열면
플레이어 대신 **구매 화면(`Purchase options $760.00 / ADD TO CART`)** 이 뜬다.
실제로 이걸 "수강 등록 안 됨"으로 오해해서 카탈로그를 한참 뒤진 적이 있다.

**카탈로그를 뒤지기 전에 `My Courses` 를 먼저 본다.**

```bash
"$B" goto "https://training.synopsys.com/learn/mycourses"
# N Items 가 보이면 로그인 상태, /learn/signin 이면 만료
```

만료면 **사용자에게 그 창에서 로그인해 달라고 요청한다.** 대신 로그인하지 않는다.

## 3. 강좌와 레슨 열기

```
https://training.synopsys.com/learn/courses/<id>/<slug>/lessons
```

페이지마다 **투어 팝업이 뜬다.** 먼저 닫지 않으면 클릭이 가로막힌다.

```js
const b=[...document.querySelectorAll("button")].find(e=>/Explore on my own/i.test(e.innerText)); if(b)b.click();
```

레슨은 제목 `<span>` 을 찾아 조상으로 올라가며 list-item 을 클릭한다.

```js
const s=[...document.querySelectorAll("span")].find(e=>e.innerText.trim()==="<레슨 제목>");
let n=s,h=0; while(n&&h<8){ if(/list-item|lesson/i.test(n.className||"")||/LESSON/i.test(n.tagName)){ n.click(); break; } n=n.parentElement; h++; }
```

그 다음 `Resume training` 또는 `Start learning now` 버튼을 누른다. 없으면 이미 열린 것이다.
**이미 완료한 레슨은 그 자리에 `Retake the lesson` 만 있다.** 다시 보려면 그걸 눌러야 하고,
완료 기록에 손이 갈 수 있으니 **누르기 전에 사용자에게 확인을 받는다.**
(Articulate 레슨은 목차를 전부 방문하면 다시 완료로 잡히므로 위험은 낮다. 그래도 사용자 계정이다.)

`goto` 는 Angular 렌더보다 먼저 돌아온다. **레슨 목록이 그려질 때까지 기다렸다 클릭한다.**
안 기다리면 조용히 `lesson not found` 로 끝난다.

## 4. SCORM 프레임 진입

콘텐츠는 **cross-origin iframe 안**에 있다. 최소 두 겹, TechSmith 는 세 겹이다.

```bash
"$B" frame --name sco             # 이것만 쓰면 된다. 프레임 트리 전체를 뒤져서 중첩된 것도 찾는다
"$B" frame main                   # 빠져나오기
```

**`frame <CSS 선택자>` 는 main 페이지에서만 찾는다.** 중첩 프레임에는 안 닿으니 `--name` 을 쓴다.
`Frame not found` 는 문법 문제가 아니라 **아직 그 프레임이 안 생긴 것**인 경우가 대부분이다.
`sco` 는 launcher 가 SCORM 패키지를 받아온 뒤에 생기므로 붙을 때까지 다시 시도한다.

**`browse click` 은 지금 들어가 있는 프레임 안에 닿는다** (gstack v1.84 기준 확인).
예전에 안 닿는다고 적혀 있었는데 사실이 아니다. 오히려 **React 컨트롤은 `el.click()` 을 무시하고
`browse click` 만 먹는다.** 레슨 시작 때 뜨는 `Resume where you left off?` 프롬프트가 그렇다.

```bash
"$B" click 'button:has-text("No")'     # el.click() 으로는 안 닫힌다
```

## 5. 플레이어 3종 판별

`sco` 프레임에 들어가서 판별한다. **셋이 전부 다르다.**

| 판별 | 플레이어 | 슬라이드 | 나레이션 |
|---|---|---|---|
| `#preso` 있고 URL 이 `index_lms.html` | Articulate 클래식 | `#slide` | `#transcript-content` |
| `#preso` 있고 URL 이 `index_lms_html5.html` | Articulate HTML5 (React) | `.slide` | 없음. 슬라이드 안 **Notes** 블록 |
| `.tsc-smartplayer` | TechSmith Smart Player | 영상이다 | 자막 트랙 |

목차는 셋 중 앞의 둘이 같다: `.cs-outline .cs-listitem`, 현재 항목은 `.cs-selected`, 열람 완료는 `.cs-viewed`.

### 5a. Articulate 클래식

컨트롤 ID 가 있다: `#play-pause` `#prev` `#next` `#seek`.
**슬라이드가 타임라인 따라 쌓이므로 끝으로 보내야 전부 나온다.**
seek input 은 `input[aria-label="slide progress"]` 이고 **단위가 ms** 다 (max 가 예를 들어 26000).
볼륨 슬라이더도 range 라서 `input[type=range]` 만으로 고르면 그걸 집는다.

```js
const inp=[...document.querySelectorAll('input[type=range]')]
  .find(i=>/slide progress/i.test(i.getAttribute('aria-label')||''));
const setV=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
setV.call(inp, String(Math.round(Number(inp.max)*0.95)));
['input','change'].forEach(t=>inp.dispatchEvent(new Event(t,{bubbles:true})));
```

`#transcript-content` 는 **Transcript 탭을 안 눌러도 이미 DOM 에 있다.**

#### 클래식은 끝에 닿으면 무조건 다음 장으로 넘어간다

HTML5 는 끝에서 멈추지만 **클래식은 자동 진행이다.** 그래서 여기서 하면 안 되는 것이 둘이다.

- **`max - 100` 으로 밀지 마라.** 그 장이 끝나면서 다음 장으로 넘어간다. **0.95 배가 실측 안전선**이다
- **끝 신호(`#play-pause` 아이콘이 `icon-play`)를 기다리지 마라.** 기다리면 덱을 계속 걸어간다.
  실측으로 3 번 슬라이드에서 11 초 만에 12 번까지 갔다. 한 번만 밀고 바로 찍는다

**목차 클릭 직후에는 아직 이전 슬라이드의 seek input 이다.** 거기 밀면 그 장이 끝나 버린다.
0.7 초쯤 기다렸다 민다. 이걸 빼면 섹션의 첫 장이 매번 실패한다.

**다 그려졌는지는 시계가 아니라 그리기 진행도로 본다.** 클래식은 본문 텍스트가 시각용과
접근성용 두 벌이라 `renderedLen / bodyLen` 을 못 쓴다. `.slide-object.shown` 개수가
자라기를 멈췄고 그 사이에 다음 장으로 안 넘어갔으면 끝난 것이다.
시계 비율(`seek/max >= 0.95`)을 기준으로 삼으면 **목표를 낮췄을 때 영영 통과 못 하는 모순**이 생긴다.
실제로 그 모순 때문에 두 장이 사다리를 끝까지 내려갔다.

#### 목차가 아코디언이다

클래식의 목차는 섹션이 접혀 있고 **한 번에 하나만 펼쳐진다.** 접힌 섹션의 하위 항목은
`offsetParent` 가 `null` 이라 클릭이 아예 안 된다 (`Element not found or not interactable`).
찍기 전에 그 항목을 감싸는 `is-scene` 행을 눌러 펼치고, **펼침 애니메이션을 기다린다** (2~3 초).
기다리지 않고 바로 읽으면 아직 안 보인다고 나온다.

### 5b. Articulate HTML5 (React)

`DS` 전역도 `#play-pause` 도 없다. 겉보기에 컨트롤이 전부 div 라 손댈 데가 없어 보인다.
**그렇지 않다. seekbar 는 진짜 `input[type=range]` 다.** 클래식과 똑같이 밀 수 있다.

**텍스트는 seek 없이 다 나온다. 스크린샷은 아니다. 이 둘을 절대 같이 묶지 마라.**

슬라이드 전체가 처음부터 DOM 에 있지만 **그려지는 것은 나레이션 타임라인을 따라 하나씩 쌓인다.**

- `innerText` 는 **지금 화면에 그려진 것만** 준다
- **`textContent` 는 전부 준다** (실측 853 자 vs 2416 자)
- 그래서 **텍스트 수집**은 목차를 클릭하고 1~2 초 뒤 TreeWalker 로 읽으면 끝난다
- **스크린샷을 그 시점에 찍으면 백지이거나 bullet 한 줄짜리다.** 위의 "853 자" 가 바로 그 순간이고,
  그 슬라이드는 내용의 4% 만 그려져 있었다. 2026-09-08 수집에서 DC 3 개 강좌 80 장 중 52 장을
  그렇게 날렸다

끝에 나오는 `Notes` 마커 뒤쪽이 **강사 해설**이고, 이 플레이어에서는 설명의 대부분이 거기 있다.
Notes 는 슬라이드 위에 그려지지 않으므로 **렌더 완료 판정의 분모에서 빼야 한다.**
`.slide-layer` 중 `hidden` 이 붙지 않은 것들의 `textContent` 합이 진짜 분모다.

#### 타임라인을 기다리지 말고 끝으로 민다

```js
// aria-label 로 고른다. 볼륨 슬라이더도 range 라 type 만으로 고르면 그걸 집는다.
const inp = [...document.querySelectorAll('input[type=range]')]
  .find(i => /seek/i.test(i.getAttribute('aria-label') || ''));
const setV = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
setV.call(inp, '0.999');                                  // max 가 1 이다. ms 가 아니다
['input','change'].forEach(t => inp.dispatchEvent(new Event(t, {bubbles:true})));
```

밀고 나면 `.cs-seekcontrol` 의 첫 버튼 텍스트가 `pause` 에서 **`play` 로 바뀐다. 이게 끝 신호다.**
한 장에 0.4~1.2 초면 끝난다. 재생을 기다리면 레슨 하나에 10 분 넘게 든다.

**함정 둘.**

- **끝까지 밀면 자동 진행이 켜진 슬라이드는 그대로 다음 장으로 넘어간다.** 짧은 타이틀/Agenda
  슬라이드가 그렇다. 찍기 전에 `.cs-outline .cs-selected` 가 **몇 번째 항목인지** 확인하고,
  어긋났으면 목표를 0.95 → 0.85 → 아예 밀지 않음 순으로 낮춰 다시 잡는다
- 퀴즈 슬라이드에는 seekbar 가 없다. 밀 게 없으니 `innerText` 길이가 자라기를 멈출 때까지
  기다렸다가 찍는다 (0.4 초 간격으로 6 회 같으면 끝)

#### 화면이 얼어붙어 있으면 창이 가려진 것이다

**Chromium 은 창이 다른 창에 가려지면(occluded) `requestAnimationFrame` 과 `setTimeout` 을
초당 1 회로 조인다.** `document.hidden` 은 `false`, `document.hasFocus()` 는 `true` 라서
증상만 보면 원인을 못 찾는다. 이 플레이어의 애니메이션은 GSAP 이고 rAF 로 도니까
그 상태에서는 슬라이드가 사실상 안 그려진다. 재보면 바로 나온다.

```js
let f=0; const t=()=>{f++;requestAnimationFrame(t);}; requestAnimationFrame(t);
await sleep(2000); return f/2;     // 60 이상이면 정상, 1 이면 창이 가려져 있다
```

gstack 은 Chromium 실행 인자를 하드코딩해서 `--disable-backgrounding-occluded-windows` 를
끼워 넣을 훅이 없다. **수집하는 동안 창을 최상위로 올려두고 끝나면 되돌린다.**
`browse focus` 는 macOS 전용이라 Windows 에서는 PowerShell 로 `SetWindowPos(HWND_TOPMOST)` 를 쓴다.

**seek 으로 미는 방식은 타임라인이 도는지에 의존하지 않는다.** 그래서 창 문제를 만나도
덜 깨진다. 이것이 재생을 기다리는 것보다 나은 두 번째 이유다.

#### 판정 근거를 shot 마다 남긴다

```
{"idx":11,"stable":true,"ended":true,"seeks":1,"seekTo":0.999,
 "renderedLen":734,"bodyLen":705,"notesLen":149,"selectedIdx":11,"selected":"How is ..."}
```

`renderedLen / bodyLen` 이 0.95 미만이거나 `selectedIdx` 가 원한 index 와 다르면 그 shot 은 실패다.
**다음 슬라이드로 넘어가기 전에 판정한다.** 퀴즈 슬라이드는 정답/오답 피드백 글자 때문에
1.0 이 안 나오니 임계를 0.95 로 둔다.

#### 프로그레스바 모양에 속지 마라

이 스킨은 **지나간 구간이 밝은 회색, 남은 구간이 어두운 회색**이다. 채워지는 색 막대가 없다.
그래서 **끝까지 간 바는 "텅 빈 것처럼" 균일한 밝은 회색**이고, 처음에 멈춘 바는 어두운 트랙에
왼쪽 끝 작은 밝은 블록(플레이헤드)이 보인다. 버튼도 같이 본다. ⏸ 면 재생 중, ▶ 면 끝난 것이다.
눈으로 헷갈리면 DOM 을 본다: `input[aria-label=Seekbar]` 의 `value` 가 1 이면 끝이다.

### 5c. TechSmith Smart Player

슬라이드가 아니라 mp4 화면 녹화다. 프레임이 세 겹이다:
`scormapi_v60` → `<name>.html` → `<name>_player.html`.

**설정 XML 하나에 모든 게 들어 있다.**

```js
TSC.playerConfiguration.getXMPSrc()   // 예: coredebug_config.xml
```

그 XML 의 `xmpDM:markers` 트랙 셋:

- `Caption` 나레이션. 시작시각과 길이가 붙어 있고 본문이 `{\rtf1 ...}` 로 감싸여 있어 RTF 를 풀어야 한다
- `ScreenText` 화면에 뜬 글자
- `TableOfContents` 목차와 각 항목 시작 시각

프레임 캡처는 `video.currentTime` 을 목차 구간 끝 직전으로 옮기고 `pause()` 한 뒤 `seeked` 를 기다린다.
영상 영역만 남기려면 `browse screenshot --clip x,y,w,h`.

## 6. 여러 슬라이드를 훑을 때

**CLI 왕복으로 루프를 돌리지 마라.** 한 슬라이드마다 `browse js` + `browse eval` 을 부르면
느리기도 하고, 플레이어가 막 로드된 직후에는 목차가 아직 없어서 **전부 조용히 빈손으로 끝난다.**
실제로 17 번을 20 초 만에 헛돌린 적이 있다.

**브라우저 안에서 한 번에 순회하는 eval 하나를 쓴다.** 그 안에서 목차가 나타날 때까지 먼저 기다린다.

```js
let items = [...document.querySelectorAll('.cs-outline .cs-listitem')];
for (let t=0; t<40 && items.length===0; t++) { await sleep(250); items = [...document.querySelectorAll('.cs-outline .cs-listitem')]; }
```

**스크린샷까지 찍을 거면 CLI 왕복이 불가피하다.** `browse screenshot` 은 eval 안에서 못 부른다.
대신 **목차 클릭과 렌더 판정은 프레임 안 eval 하나로 묶고, 스크린샷만 바깥에서 찍는다.**
이 저장소는 그걸 두 파일로 굳혀놨다.

| 파일 | 하는 일 |
|---|---|
| `scripts/articulate-step.js` | 프레임 안. 슬라이드를 끝으로 밀고 판정해서 JSON 을 돌려준다 |
| `scripts/collect-articulate.sh` | 목차 클릭 → step → 스크린샷 루프. 어긋나면 seek 목표를 낮춰 재시도 |
| `scripts/open-lesson.sh` | 레슨 열기. 투어/쿠키/Retake/Resume 프롬프트를 순서대로 치운다 |
| `scripts/shotcheck.py` | 다 찍은 뒤 검사. 로그와 픽셀 양쪽으로 본다 |
| `scripts/rename-shots.py` | 파일 이름을 목차 번호/이름으로 바꾸고 문서 참조까지 고친다 |

### 한 장씩 판정하고 넘어간다

순회 루프는 **찍고 끝내는 게 아니라 찍을 자격이 됐는지 확인하고 찍는다.** 판정을 통과한
슬라이드만 남기고, 통과 못 한 것은 로그에 그대로 남겨 **그 자리에서 눈에 띄게 한다.**
로그에 실패를 적어놓고 아무도 안 읽는 것이 가장 흔한 실패다. 실제로 DC 3 개 강좌 80 장 중 52 장을
그렇게 날렸다. `renderedLen` 과 `fullLen` 을 나란히 찍어놓고도 둘을 비교하지 않았다.

**한 번의 eval 로 34 장을 다 돌리면 CLI 타임아웃에 걸려 통째로 날아간다.** 90 초짜리 루프 하나도
`The operation timed out` 으로 끝난다. 로그는 append 하고, 끊긴 지점부터 다시 시작할 수 있게 짠다.

### 스크린샷은 `--viewport` 를 붙인다

`browse screenshot` 의 기본은 **전체 페이지**다. 이 사이트는 플레이어가 lightbox 라서
전체 페이지로 찍으면 **플레이어 영역이 통째로 하얗게 비어 나온다.** 크기도 1600x1582 같은 게 나온다.

```bash
"$B" viewport 1600x1000
"$B" screenshot --viewport shots/s11.png
```

뷰포트는 CDP 가 페이지에 강제하는 값이라 **사용자가 창 크기를 바꾸거나 확대해도 결과가 같다.**

### browse eval 의 함정 둘

1. **파일 경로가 `/tmp` 나 cwd 아래여야 한다.** 아니면 **조용히 아무것도 안 하고 성공한다.**
2. 코드에 `await` 가 있으면 `(async()=>{...})()` 로 한 번 더 감싸므로 **`return` 이 필요하다.**
   `await` 가 없으면 그대로 실행되므로 **top-level `return` 이 문법 오류**다. 둘 중 하나로 맞춘다.

## 7. 완료 판정 (제출 증거가 필요할 때)

**수집과 완료는 다르다.** 슬라이드를 다 읽어도 완료로 안 잡힐 수 있다.

- **Articulate**: 목차 항목을 전부 방문하면 레슨이 `Completed` 로 바뀐다.
  일부만 요구하는 과제라면 `.cs-viewed` 가 붙은 메뉴 자체가 증거다.
- **TechSmith**: 끝으로 seek 해서 `ended` 를 띄워도 **안 된다.** 실제로 재생된 구간 비율을 본다.
  처음부터 끝까지 재생해야 하고, **`playbackRate` 는 플레이어가 2 로 강제**한다. 34 분짜리면 17 분이 든다.
  `v.playbackRate=16` 을 줘도 조용히 2 로 되돌아가니 그 시간을 감수하고 계획을 잡는다.

**영상이 도는 동안 그 탭을 다른 데로 옮기지 마라.** 플레이어가 통째로 사라지고
그때까지 재생한 구간도 같이 날아간다. 실제로 33% 에서 다른 강좌 스크린샷을 찍으려다
처음부터 다시 돌린 적이 있다. 중간에 다른 페이지가 필요하면 `browse newtab` 으로 새 탭을 쓴다.
진행률 확인은 탭을 건드리지 않는 `browse js` 폴링으로 한다.

증거 스크린샷은 **메뉴 패널만 잘라서** 찍는다. 슬라이드 본문이 같이 찍히면 confidential 자료를 복제하는 셈이다.
프레임 안 좌표에 iframe 의 페이지 좌표를 더해서 `--clip` 을 만든다.

## 8. 끝내기 전에

**수집물이 쓸 만한지부터 기계로 본다.** 이걸 안 해서 52 장을 날린 것을 반년 뒤에 알았다.

```bash
python scripts/shotcheck.py lab/lab0/materials
```

- `PARTIAL` 은 `renderedLen / bodyLen` 이 0.95 미만. 덜 그려진 채 찍혔다
- `WRONG_SLIDE` 는 자동 진행으로 다음 장이 찍혔다
- `BLANK` / `SPARSE` 는 픽셀로 본 것. 로그가 없거나 못 믿을 때의 독립 증거다
- 전부 0 이어야 끝난 것이다. FLAG 는 눈으로 확인하고 그 슬라이드만 다시 찍는다

**그 다음 파일 이름을 목차에 맞춘다.** `s00.png` 로는 나중에 어느 장인지 알 수 없다.

```bash
python scripts/rename-shots.py lab/lab0/materials
```

`<인덱스>_<목차번호>_<이름>.png` 가 된다 (`09_1.3_pure-verilog-flow-2-step.png`).
인덱스를 맨 앞에 둬야 정렬이 목차 순서와 맞는다. 목차 번호만 쓰면 `1.10` 이 `1.2` 앞에 온다.
**transcript.md 의 `shots/...` 참조도 같이 고친다.** 안 그러면 링크가 전부 깨진다.
다시 돌려도 안전하다. 재수집으로 `s00.png` 가 다시 생기면 그것만 바꾼다.

그리고:

- 창을 최상위로 올려뒀으면 **되돌린다.** 사용자 화면을 계속 덮는다
- 수집물이 `lab/**/materials/` 안에 있는지 `git status` 로 확인한다
- 폴더와 문서 제목은 **플레이어 목차에 나온 문자열 그대로** 쓴다. 임의로 바꾸지 않는다
- 무엇을 어떻게 뽑았는지 `lab/lab0/README.md` 같은 작업 기록에 남긴다. 다음 사람이 또 헤매지 않게
