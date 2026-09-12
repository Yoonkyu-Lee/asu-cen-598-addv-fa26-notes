---
name: write-note
description: 이 저장소에 강의 노트(notes/L{NN}-*.html)나 Lab 공략(notes/LAB{N}-*.html)을 새로 쓰거나 고칠 때 쓴다. 5단 구조, .jargon 규약, 이중 언어, 의미 고정 색상, 검증 루프를 컨텍스트 없이 바로 착수할 수 있게 정리했다. "노트 써줘 / 강의 정리 / 블로그화 / Lab 공략"에서 호출한다.
---

# 학습 노트 작성

`CLAUDE.md` 가 전체 계약이고 897 줄이다. **이 스킬은 그걸 통독하지 않고 착수하기 위한 실행 절차다.**
판단이 갈리면 `CLAUDE.md` 가 이긴다. 아래 각 절에 해당 원문 위치를 적어뒀다.

## 0. 이 저장소가 하는 일

ASU CEN 598 (Advanced Digital Design and Verification) 강의를 **업계 용어를 모르는 사람도 읽히는**
개인 학습 노트로 재구성한다. 독자(YK)는 **Verilog 는 쓸 줄 알지만 산업 워크플로우와 용어는 처음이다.**
그 간극이 이 노트의 존재 이유다. 수식이 아니라 **용어와 흐름**이 막히는 지점이다.

## 1. 먼저 정하라: 무엇을 쓰는가

| | 강의 노트 | Lab 공략 |
|---|---|---|
| 파일 | `notes/L{NN}-{kebab}.html` | `notes/LAB{N}-{kebab}.html` |
| 번호 | **강의 사이트 Schedule 의 Lecture 번호.** PPTX 앞 번호가 아니다 | 과제 번호 |
| 정렬 | 슬라이드 순서 | **요구사항 항목 순서** |
| `data-slide` | 붙인다 | **안 붙인다** |
| `reader.js` | 넣는다 | **안 넣는다** |

`{NN}` 이 PPTX 번호와 어긋나는 일이 실제로 있다. Schedule 이 기준이다.

## 2. 착수 전 확보할 것

**슬라이드 없이 노트를 쓰지 않는다.** 없으면 `index.html` 에서 `soon` 으로 두고 기다린다.

```bash
node scripts/pagecount.mjs                      # PPTX 장수 = PDF 쪽 수 확인
python scripts/pptx-text.py "<pptx>"            # 본문 + 발표자 노트
node scripts/pdftext.mjs slides/<stem>.pdf      # 쪽별 텍스트. 앵커 달기 전 대조용
node scripts/render-slides.mjs slides/<stem>.pdf 12-18   # 도해는 반드시 눈으로 본다
```

**텍스트만 보고 도해를 옮기면 반드시 틀린다.** 화살표가 어디를 가리키는지, 표의 열 순서가
어떤지는 렌더해서 봐야 안다. 실제로 이걸로 틀린 적이 있다.

**그 다음 오늘 나오는 새 용어부터 뽑는다.** 각각에 대해 풀네임 / 한 줄 / 언제 / 누가 /
헷갈리는 것을 채울 수 있는지 확인한다. **못 채우면 아직 이해 못 한 것이다.**

Synopsys 트레이닝 같은 로그인 자료가 필요하면 `synopsys-training` 스킬을 쓴다.

## 3. 뼈대 만들기

**스타일 블록을 손으로 복사하지 않는다.** 기존 노트에서 뽑아서 끼운다. 안 그러면 파일들이 갈라진다.

```bash
node -e "const fs=require('fs');const s=fs.readFileSync('notes/L01-course-intro.html','utf8');
const a=s.indexOf('<style>'),b=s.indexOf('</style>')+8;fs.writeFileSync('.build-style.html',s.slice(a,b));"
```

경로 규칙 (노트는 `notes/`, 허브만 루트):

- 허브로: `href="../index.html"` · 리더: `src="../reader.js"`
- **노트끼리와 glossary 는 같은 폴더라 그대로**: `href="L02-....html#s7"`

## 4. 섹션 5단 구조

각 개념 섹션이 이 순서를 반복한다.

1. **요약** 섹션 00. 이 강의가 하는 일 + **오늘 나오는 약어 표** + 뭐가 제일 중요한지
2. **정의** `.def` 로 슬라이드 정의를 그대로. **바로 뒤에 `.jargon`**
3. **비주얼** 흐름과 경계를 그린다. 무엇이 무엇으로 바뀌고 누가 누구에게 넘기는지. **이게 존재 이유다**
4. **현장 감각** `.ex` + `<details>`. 계산이 아니라 **분류와 판단** 문제
5. **함정** `.trap`. 헷갈리는 이웃 용어, 회사마다 다른 이름. **사용자가 제일 값있게 보는 부분**

마지막 섹션은 항상 **정리 & 다음 강의**: 한 장 요약 표 + Lab/Quiz 대응 + 다음 예고.

## 5. `.jargon` 이 핵심 장치다

**다섯 줄을 채운다.** 풀네임 / 한 줄 / **언제** / **누가** / 헷갈리는 것.
가운데 둘이 이 과목의 핵심이다. 사전적 정의만 적으면 만든 의미가 없다.

**표를 두 벌 둔다.** 셀 단위로 언어를 섞지 않는다.

```html
<details class="jargon" open>
  <summary><span lang="ko">용어 뜯어보기 · ECO</span><span lang="en">Unpacking the jargon · ECO</span></summary>
  <div class="body">
    <table class="parts" lang="ko"> … 5행 … </table>
    <table class="parts" lang="en"> … 5행 … </table>
  </div>
</details>
```

같은 용어를 두 번 풀지 않는다. 처음 나온 곳에서 풀고 뒤에서는 그리로 링크한다.

## 6. 반드시 지켜야 할 규칙

문체 · 언어 (`CLAUDE.md` "언어와 문체")

- 본문은 **한국어 반말**. **em dash(—) 금지**, 콜론·쉼표·마침표로. 영어판에도 적용된다
- **업계 용어와 약어는 영어 유지.** netlist, tapeout, slack, testbench. 번역도 음차도 안 한다
- 일반 명사는 한국어. "이 단계에서 넘기는 산출물"
- **"업계에서는 ~한다"는 근거가 있을 때만.** 없으면 쓰지 않는다
- **용어를 지어내지 않는다.** 이 과목 최대 위험이고 자동 검사가 못 잡는다

이중 언어 (`CLAUDE.md` "이중 언어")

- `<p lang="ko">` / `<p lang="en">` 쌍. 영어는 **번역문이 아니라 처음부터 영어로 쓴 글**
- **`<details>` 하나에 `<summary>` 는 하나.** 두 벌 넣으면 숨는 언어에서 내용에 영원히 못 간다
- **SVG 텍스트도 같은 좌표로 두 벌.** `lang="ko"` / `lang="en"`
- **`pre.code` 안 주석도 번역 대상이다.** 여기서 제일 많이 샌다

색 (`CLAUDE.md` "의미 고정 색상")

| Design/RTL | Verification | 도구 | 통과 | 함정 | 물리 | 범위 밖 |
|---|---|---|---|---|---|---|
| `--blue` | `--pink` | `--violet` | `--green` | `--amber` | `--brown` | `--ink3` |

**색 하드코딩 금지.** 토큰만 쓴다. 농도는 `rgba(var(--blue-rgb),.13)`.
`<mask>` 안의 `#000`/`#fff` 만 예외다.

SVG (`CLAUDE.md` "SVG 규칙")

- `viewBox` 필수, `width`/`height` 금지, `role="img"` + `aria-label` 필수
- **크기·색은 인라인 `style` 로.** 프레젠테이션 속성은 클래스에 진다
- **라벨 없는 화살표는 그리지 않는다.** 이 과목 도해는 화살표가 주인공이다
- `<defs>` id 는 파일 내 유일해야 한다
- **라벨을 화살표 선 위에 놓지 마라.** 자동 검사가 못 잡고 렌더해야 보인다
- 원문자(①②③)는 mono 폰트에 없어서 깨진다. `1.` `2.` 로 쓴다

쓸 수 있는 클래스: `.def` `.jargon` `.trap` `.ex` `.callout` `pre.code` `figure` `.mini`
`.grid2` `.grid3` `.play` `.chip.hot` `.chip.dim` `.cD/.cV/.cT/.cP`
**`.grid4` 와 `.chip.warn` 은 없다.**

## 7. 검증 루프

```bash
node scripts/verify.mjs notes/L{NN}-{topic}.html      # exit 0 이어야 통과
node scripts/langcheck.mjs notes/L{NN}-{topic}.html   # 영어 모드 한글 잔류
node scripts/readercheck.mjs notes/L{NN}-{topic}.html s1,s3,s9   # 앵커 동기화
```

**`shots/*-fig01.png` 부터 한 장씩 전부 열어본다.** 자동 검사가 통과해도 건너뛰지 않는다.
테두리가 글자를 관통하는 것, 화살표가 라벨을 뚫는 것, 색 의미 위반은 **눈으로만 잡힌다.**

`readercheck` 가 한두 쪽 뒤지게 나오는 것은 정상이다. 리더 판정선이 화면 위가 아니라 조금 아래에 있다.
**몇 쪽씩 어긋나면 그때 앵커를 의심한다.**

**검사가 전혀 못 잡는 것**: 설명의 질, 용어 풀이가 실제로 이해되는지, **용어를 지어냈는지.**
그래서 **완성했다고 단정하지 말고 사용자에게 확인을 요청한다.**

## 8. 끝내기 전 체크리스트

- [ ] `glossary.html` 에 이번에 푼 용어를 **전부** 넣었다. 알파벳 자리도 맞췄다. 미루면 반드시 빠뜨린다
- [ ] `index.html` 카드를 `soon` 에서 링크로 바꾸고 태그와 `N / 30강` chip 을 갱신했다
- [ ] 이전 강의와의 연결을 `.callout` 으로 최소 한 번 짚었다
- [ ] `verify.mjs` · `langcheck.mjs` 둘 다 exit 0
- [ ] 도해 스크린샷을 전부 눈으로 봤다
- [ ] 커밋 메시지는 영어. 슬라이드 PDF 가 노트보다 늦게 들어가지 않게 같이 커밋한다
