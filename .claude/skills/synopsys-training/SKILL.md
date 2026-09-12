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

## 4. SCORM 프레임 진입

콘텐츠는 **cross-origin iframe 안**에 있다. 최소 두 겹, TechSmith 는 세 겹이다.

```bash
"$B" frame --url "scormapi_v60"   # 런처
"$B" frame --name sco             # 실제 콘텐츠
"$B" frame main                   # 빠져나오기
```

`browse click` 은 **프레임 안으로 안 닿는다** (page 기준이라). 프레임 안에서는 `browse js` 로 `el.click()` 한다.

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
`#seek input` 이 `type=range`(단위 ms)이니 값을 max 근처로 밀고 이벤트를 쏜다.

```js
const inp=document.querySelector('#seek input');
const setV=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
setV.call(inp, String(Number(inp.max)-100));
['input','change'].forEach(t=>inp.dispatchEvent(new Event(t,{bubbles:true})));
```

`#transcript-content` 는 **Transcript 탭을 안 눌러도 이미 DOM 에 있다.**

### 5b. Articulate HTML5 (React)

`DS` 전역도 `#play-pause` 도 `#seek input` 도 없다. seekbar 가 div(`.cs-seek`)라
값을 못 주고 **합성 마우스 이벤트도 무시한다.** 진짜 클릭은 프레임 안으로 안 닿는다.

**그런데 seek 이 아예 필요 없다.** 슬라이드 전체가 처음부터 DOM 에 있고 렌더만 안 된 상태다.

- `innerText` 는 지금까지 그려진 것만 준다
- **`textContent` 는 전부 준다** (실측 853 자 vs 2416 자)
- 화면도 처음부터 완성돼 렌더된다. 스크린샷도 기다릴 필요 없다

목차를 클릭하고 1~2 초 뒤 TreeWalker 로 텍스트 노드를 순서대로 읽으면 끝이다.
끝에 나오는 `Notes` 마커 뒤쪽이 **강사 해설**이고, 이 플레이어에서는 설명의 대부분이 거기 있다.

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

- 수집물이 `lab/**/materials/` 안에 있는지 `git status` 로 확인한다
- 폴더와 문서 제목은 **플레이어 목차에 나온 문자열 그대로** 쓴다. 임의로 바꾸지 않는다
- 무엇을 어떻게 뽑았는지 `lab/lab0/README.md` 같은 작업 기록에 남긴다. 다음 사람이 또 헤매지 않게
