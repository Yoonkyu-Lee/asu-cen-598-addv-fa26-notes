# Apporto 에서 돌리고 캡처하기

`SKILL.md` 의 보조 문서다. 시뮬레이션, 합성, 파형 캡처, 터미널 캡처를 Apporto 에서 할 때 읽는다.

## 흐름

```
로컬에서 고침 ──(git push)──▶ labs 저장소 (private) ──(git pull)──▶ Apporto ~/labs
Apporto 에서 나온 보고서 ──(git push)──▶ labs ──(pull)──▶ 로컬
```

- Apporto 홈은 NFS 다. `~/labs` clone 과 SSH 키가 노드가 바뀌어도 남는다
- 도구 환경: `cd ~/labs && source lab1/part1/env.sh` (VCS, Verdi, DC, `PDK_DIR`)
- **로그인은 사용자가 한다.** 비밀번호, Duo, keyring 암호를 치지 않는다.
  keyring 잠금 대화상자("Default keyring")가 뜨면 타이핑이 그 칸으로 들어간다. **`$B press Escape`** 로 닫는다
  (Cancel 좌표 클릭은 안 먹을 때가 있다). 닫히면서 터미널 창도 사라질 수 있으니 스크린샷으로 확인하고 다시 연다.
  **타이핑 전에는 항상 스크린샷으로 터미널 프롬프트가 보이는지 확인한다**

## browse

바이너리는 `~/.claude/skills/gstack/browse/dist/browse.exe` 다 (`$B`).

- **`browse` 는 현재 디렉토리의 `.gstack/browse.json` 을 상태 파일로 쓴다.** 디렉토리를 옮겨서 부르면
  다른 데몬이 about:blank, 1280x720 으로 새 브라우저를 띄운다. "세션이 끊겼다" 가 아니다.
  **browse 는 항상 labs 저장소 루트에서 부른다.** 다른 곳의 스크립트는 `( cd 거기 && ... )` 서브셸로 감싼다
- `Meta`/`Super` 키는 브라우저가 가로챈다. 창 조작은 원격 앱의 메뉴로 한다
- **Guacamole 캔버스는 `$B click <sel>` 이 안 먹는다.** labs `.tmp/guac.sh` 를 `source` 해서 쓴다 (git 에 없는 로컬 파일)
  - `gclick X Y`: client 좌표 클릭. 스크린샷 좌표 × 1.28 이 client 좌표다
  - `gdrag X1 Y1 X2 Y2`: 스크린샷 좌표로 드래그
  - `gcap OUT.png X Y W H`: 캔버스를 원래 해상도로 잘라 저장
  - `wavecap OUT.png START END HEIGHT`: nWave 창에서 시간 범위를 줌해서 캡처
- **`$B type` 과 `$B press Enter` 를 붙여 치지 않는다.** 앞 명령이 출력 중이면 글자가 끼어든다.
  사이에 `$B js 1` 을 한 번 넣는다
- 글자 크기는 `Ctrl+Plus` 가 아니라 **View 메뉴의 Zoom In/Out** 으로 바꾼다. `Ctrl+Plus` 는 빈 Enter 로 들어간다
- 터미널 열기: Activities → `terminal` 입력 → Enter. 최대화는 `Alt+F10`
- **캡처 전에 gstack 자국 둘을 지운다** (`#gstack-ctrl`, `#gstack-status-pill`). 화면 내용을 건드리는 게 아니다:

  ```
  $B js "(()=>{const s=document.createElement('style');s.id='nogstack';s.textContent='#gstack-ctrl,#gstack-status-pill{display:none!important}';document.documentElement.appendChild(s);return 'ok';})()"
  ```

  인라인 style 이 아니라 `!important` 스타일시트로 넣는다. 확장이 알약을 인라인 `display:flex` 로 다시 띄우기 때문이다

## 터미널 스크린샷

터미널 출력 캡처는 설명서 Deliverable 이다. 증거이므로 아래를 지킨다.

- **실제로 칠 명령만 친다.** `echo "=== BEFORE ==="` 같은 배너를 만들어 넣지 않는다
- **프롬프트가 프레임 안에 있다.** 프롬프트가 "어느 디렉토리에서 쳤는가" 를 증명한다
- **친 명령과 그 출력이 같은 프레임에 있다.** 출력만 잘라 넣지 않는다
- **자르지 않는다.** 창 테두리, 메뉴바, 여백까지 있는 그대로 넣는다
- 도구 리포트(`area.rep` 등)는 **머리말째** 담는다. `Design` / `Version` / `Date` / `Library(s) Used` 가 출처다
- 한 화면에 안 들어가면 터미널을 키운다(View > Full Screen). 그래도 넘치면 `clear` 하고 다시 친다
- before/after 대조는 배너 대신 `ls` → `make ...` → `ls` 를 그냥 이어서 친다

**왜:** Lab 0 에서 `=== area.rep ===` 배너를 넣었다가 채점자가 그걸 DC 출력으로 오해했다.
배너 자리를 만드느라 DC 리포트 머리말을 잘라서 출처를 증명하는 증거를 스스로 버렸다.
