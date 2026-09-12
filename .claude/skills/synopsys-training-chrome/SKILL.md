---
name: synopsys-training-chrome
description: gstack browse 없이 claude --chrome 의 Chrome 도구만으로 Synopsys Learning Center 강좌를 열고 슬라이드·나레이션을 수집할 때 쓴다. SCORM 프레임이 cross-origin 이라 DOM 경로가 전부 막히므로 스크린샷과 좌표 클릭으로만 움직인다. 어디까지 되고 어디서 막히는지, 장당 비용이 왜 gstack 보다 큰지까지. "크롬으로 트레이닝 열어봐 / gstack 없이 수집"에서 호출한다.
---

# Chrome 도구로 Synopsys 트레이닝 수집하기

`.claude/skills/synopsys-training/SKILL.md` 와 **결과물은 같고 수단이 다르다.**
저쪽은 DOM 을 긁고 이쪽은 화면을 본다. 아래 내용은 전부 VCS 강좌에서 실측한 것이다.

## 0. 먼저: 이걸 쓸 상황인가

**기본은 gstack 이다.** `CLAUDE.md` 의 "로그인이 필요한 자료는 gstack browse 로 연다" 가 계약이고,
수집량이 조금이라도 많으면 그쪽이 압도적으로 싸다 (3절의 비용 표 참조).

이 스킬은 **gstack 을 못 쓸 때의 경로**다.

- `browse` 서버가 죽었는데 되살릴 시간이 없다
- 이미 `claude --chrome` 으로 켜져 있고 슬라이드 몇 장만 확인하면 된다
- 화면에 실제로 어떻게 보이는지가 중요하다 (레이아웃, 도해, 판서)

**두 스킬을 한 세션에서 섞지 마라.** 같은 강좌를 두 브라우저로 동시에 열면 SCORM 세션이
어느 쪽 진도를 기록할지 알 수 없다.

## 1. 자료 취급 규칙

**gstack 스킬 1절과 완전히 동일하게 적용된다.** 덱 2번째 장이 배포 금지를 명시한다.
수집물은 `lab/**/materials/` 아래에만 두고 (gitignore 됨), 공개 노트에는 옮기지 않는다.

**이 경로에서는 위험이 하나 더 있다.** 수집물이 전부 **스크린샷 이미지**라서,
gstack 의 텍스트 추출물보다 "슬라이드 원본 복제"에 훨씬 가깝다.
**스크린샷은 읽고 나면 남기지 않는 것을 기본으로 한다.** 읽어서 이해한 내용을 텍스트로 적고,
이미지가 꼭 필요한 경우에만 `materials/` 에 남기고 왜 필요했는지 기록한다.

## 2. 무엇이 되고 무엇이 안 되는가 (실측)

SCORM 콘텐츠는 `cdn5.dcbstatic.com/dcd/scormapi_v60/launcher.html` 에 있다.
페이지는 `training.synopsys.com` 이다. **다른 origin 이다.** 여기서 전부 갈린다.

| 도구 | 프레임 안 | 실측 결과 |
|---|---|---|
| `javascript_tool` | ❌ | `contentDocument` 가 `null`, `frames[0].location` 은 `SecurityError` |
| `get_page_text` | ❌ | 상위 프레임 텍스트만 |
| `read_page` (`filter:all`) | ❌ | 상위 프레임만. 프레임 안 요소는 트리에 아예 없다 |
| `find` | ❌ | "no button elements present on this page" 라고 답한다 |
| `computer` 스크린샷 | ✅ | 프레임 안 글자가 그대로 찍힌다 |
| `computer` 좌표 클릭 | ✅ | 프레임 안 핸들러가 실제로 발화한다 |

**이건 Synopsys 가 친 벽이 아니라 브라우저의 same-origin policy 다.**
로그인해도 안 열린다. 로그인 없는 `example.com` 에 opaque-origin iframe 을 심어도 똑같이 막힌다.
**"로그인하면 되겠지" 로 시간 쓰지 마라.** 인증 문제와 origin 문제는 별개다.

### 막다른 길: launcher 로 직접 이동하기

프레임 문서를 최상위로 열면 경계가 사라진다는 발상은 맞다. **그런데 안 된다.**

launcher URL 에 `launch_type=lightbox` 와 `context=lms` 가 박혀 있고,
단독으로 열면 **14 초를 기다려도 백지다.** LMS 안에 끼워진 상태를 전제로 만들어진 페이지다.
게다가 `cdn5.dcbstatic.com` 은 확장에 권한이 없어서 `javascript_tool` 이
`Permission denied for JavaScript execution on this domain` 으로 거절한다.

**시도하면 원래 강좌 탭도 잃는다.** 돌아오려면 레슨 URL 로 다시 navigate 하고
플레이어를 처음부터 다시 띄워야 한다 (25 초+). 하지 마라.

### iframe src 는 읽히지 않는다

`f.src` 를 그대로 반환하면 확장이 `[BLOCKED: Cookie/query string data]` 로 가로챈다.
쿼리에 `auth_code` 와 `id_user` 가 들어 있기 때문이다. **우회해서 뽑아내려 하지 마라.**
origin 과 pathname 만 필요하면 `new URL(f.src)` 로 쪼개서 그 부분만 반환한다.

## 3. 비용: 이게 이 경로의 진짜 한계

| | gstack | Chrome (이 스킬) |
|---|---|---|
| 슬라이드 60 장 본문 | `eval` 한 번, `textContent` 로 통째로 | **스크린샷 60 장** |
| 나레이션 | `#transcript-content` 를 DOM 에서 | 탭 열고 장마다 화면으로 |
| 한 장당 | 왕복 없음 | 클릭 + 대기 + 스크린샷 |

**덱 전체를 훑을 일이면 gstack 을 되살리는 게 거의 항상 싸다.**
이 경로는 **레슨 하나, 목차 몇 항목** 규모에서 쓴다.
"전부 뽑아줘" 를 이 스킬로 받았으면 **먼저 분량을 세어보고 사용자에게 비용을 알린다.**

## 4. 로그인 확인

**카탈로그를 뒤지기 전에 `My Courses` 를 먼저 본다.** gstack 스킬과 같은 함정이다.

```
navigate  https://training.synopsys.com/learn/mycourses
wait 3            ← SPA 라 즉시 읽으면 "No text content found" 가 난다
get_page_text
```

- `N Items` 와 강좌 카드가 보이면 로그인 상태
- `/learn/signin` 으로 리다이렉트되고 **$760 가격표가 붙은 카탈로그**가 나오면 세션 만료다.
  **이걸 "수강 등록이 안 됐다" 로 오해하지 마라.**

만료면 **사용자에게 그 Chrome 창에서 직접 로그인해 달라고 요청한다.** 대신 로그인하지 않는다.

**Chrome 이 여러 개 붙어 있으면 `tabs_context_mcp` 가 거부한다.** 그때는 임의로 고르지 말고
`AskUserQuestion` 으로 물어야 한다. `switch_browser` 는 모든 창에 확인 버튼을 띄우고
2 분 기다리는데, **사용자가 못 보고 넘기면 그냥 timeout 으로 죽는다.** 다시 보내면서 눌러 달라고 말한다.

## 5. 강좌 열기

강좌 URL 은 상위 프레임이라 JS 로 뽑을 수 있다.

```js
[...document.querySelectorAll('a')].map(a=>a.href).filter(h=>/\/learn\/course/.test(h))
// → https://training.synopsys.com/learn/course/290/vcs-rtl-and-gate-level-simulation
```

레슨 목록은 `course` → `courses` 로 바꾸고 `/lessons` 를 붙인다.

```
https://training.synopsys.com/learn/courses/290/vcs-rtl-and-gate-level-simulation/lessons
```

투어 팝업과 시작 버튼은 **둘 다 상위 프레임이라 JS 로 눌러도 된다.** 좌표를 쓸 필요 없다.

```js
[...document.querySelectorAll('button')].find(e=>/Explore on my own/i.test(e.innerText||''))?.click();
[...document.querySelectorAll('button,a')].find(e=>/Resume training|Start learning now/i.test(e.innerText||''))?.click();
```

**여기까지가 JS 가 닿는 마지막 지점이다.** 이 뒤로는 전부 눈과 좌표다.

## 6. 플레이어가 뜨기를 기다린다

**느리다. 실측 25~30 초.** 먼저 헤더(`Introduction to VCS`)와 스피너만 있는 화면이 나오고,
한참 뒤에야 내용이 들어온다. `wait` 는 한 번에 최대 10 초라 **여러 번 이어 붙인다.**

```
wait 10 → wait 10 → wait 8 → screenshot
```

**스피너 화면을 보고 "실패했다" 고 판단하지 마라.** 실제로 18 초 시점에도 스피너였다.

### 이어보기 모달

`Would you like to resume where you left off?` 가 뜬다.
처음부터 훑을 거면 `No`, 이어서 볼 거면 `Yes`. **좌표 클릭이다.**

## 7. 화면에서 읽어내기

Articulate 클래식 기준 화면 구성 (gstack 스킬 5a 절의 그 플레이어다):

| 위치 | 내용 |
|---|---|
| 왼쪽 위 | `Menu` / `Transcript` 탭 |
| 왼쪽 | 목차. 현재 항목이 반전 표시된다 |
| 가운데 | 슬라이드 |
| 아래 | 재생/일시정지, seek bar, `PREV` / `NEXT` |

- **본문**: `Menu` 탭 상태로 스크린샷. 슬라이드 글자가 그대로 읽힌다.
- **나레이션**: `Transcript` 탭을 누르면 왼쪽 패널이 대본으로 바뀐다.
  gstack 이 `#transcript-content` 에서 긁던 것을 여기서는 화면으로 읽는다.
- **진행**: 목차 항목을 좌표로 클릭하거나 `NEXT` 를 누른다.

### 좌표는 직전 스크린샷 것만 믿어라

**페이지 렌더링 배율이 호출 사이에 바뀐다.** 실측으로 한 번 당했다.
같은 버튼이 한 스크린샷에서 `(352,258)` 이었다가 다음에 `(376,349)` 가 됐고,
앞의 좌표로 누르니 빈 공간을 쳤다.

**클릭 직전에 찍은 스크린샷의 좌표만 쓴다.** `browser_batch` 안에서 여러 번 클릭할 때
특히 위험하다. 배치 안의 좌표는 **배치 시작 전** 화면 기준이다.

### 클릭이 먹었는지는 화면으로만 확인된다

반환값이 없다. **누르고 나서 스크린샷을 한 장 더 찍어 확인한다.**
목차 반전 위치가 바뀌었는지, 슬라이드가 넘어갔는지로 판정한다.

## 8. 끝내기 전에

- 스크린샷을 `materials/` 에 남겼다면 `git status` 로 gitignore 가 먹었는지 확인한다
- 플레이어 lightbox 를 `X` 로 닫는다. 열어둔 채로 두면 다음 세션이 이어보기 모달부터 만난다
- 무엇을 어떻게 뽑았는지 `lab/lab0/README.md` 에 남긴다
- **이 경로로 수집했다는 걸 기록에 명시한다.** 스크린샷 판독이라 gstack 의 텍스트 추출보다
  오타와 누락 가능성이 높다. 나중에 노트를 쓸 때 근거의 신뢰도가 다르다는 걸 알아야 한다
