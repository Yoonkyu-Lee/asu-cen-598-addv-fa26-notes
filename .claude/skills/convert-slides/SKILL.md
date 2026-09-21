---
name: convert-slides
description: 강의 PPTX 를 slides/*.pdf 로 변환해 저장소에 넣을 때 쓴다. 숨김 슬라이드를 되살려 쪽 번호를 맞추는 것, 발표자 노트 추출, 원본 갱신 확인, 강의 사이트 Schedule 대조까지. 노트를 쓰기 전에 먼저 끝나 있어야 한다. "슬라이드 변환 / PPTX / 새 강의 올라왔나 / Schedule 대조"에서 호출한다.
---

# 슬라이드를 저장소에 넣기

**같이 필요한 스킬**
- 변환이 끝나면 노트 작성은 `write-note`
- 강의 사이트가 로그인을 요구하면 `synopsys-training` 또는 `synopsys-training-chrome`

**참조**: 강의 번호·날짜·강사는 `docs/schedule.md` 가 단일 출처다. 여기에 옮겨 적지 않는다

**이 스킬만으로 끝나는 것**: 슬라이드 변환, 쪽 수 대조, 발표자 노트 추출

## 경로

| 용도 | 경로 |
|---|---|
| 강의 자료 원본 (스테이징) | `lecture/` (저장소 안, `.gitignore` 로 통째로 제외) |

**예전에는 Drive 미러가 원본이었으나 머신 초기화로 사라졌다.** 이제 강의 사이트에서
`lecture/` 로 직접 받는다. 파일명은 강사가 올린 그대로 둔다 (`07_Pipelined CPU Design.pptx`).

`lecture/` 는 **하나도 커밋되지 않는다.** PDF로 변환할 때도 원본을 건드리지 않고
스크래치패드로 복사해서 사본에서만 작업한다.

**원본은 학기 중에 갱신된다.** 강사가 슬라이드를 고치거나 끼워 넣는다.
**노트를 쓰거나 고치기 전에 반드시 다시 받고 쪽수를 대조한다.**
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

이렇게 얻은 Schedule 표가 `docs/schedule.md` 의 근거다.

## 슬라이드 변환 (PPTX → PDF)

EEE 554는 슬라이드가 PDF로 배포됐다. **여기는 PPTX다.** 리더가 PDF만 다루므로 변환이 필요하다.

**PowerPoint COM 자동화를 쓴다.** LibreOffice 로도 시도해봤으나 텍스트 상자를 넘친 글자를
잘라버리고 수식(OMML)을 외곽선으로 내보내서, 변환본이 강사 화면과 달라진다.
Office 가 없는 머신이라면 그 손실을 감수하고 쓸 수는 있다.

변환에 쓴 **스크래치패드의 PPTX 사본도 repo 안에 두지 않는다.** 발표자 노트가 딸려 들어간다.

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

## 슬라이드를 눈으로 봐야 한다

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

## scripts/

| 스크립트 | 하는 일 |
|---|---|
| `pptx2pdf.ps1` | PPTX → `slides/*.pdf`. 숨김 슬라이드를 되살려서 변환한다 |
| `pptx-text.py` | 슬라이드 본문 + **발표자 노트** 추출 |
| `hidden-slides.py` | 숨김 슬라이드 번호 목록 |
| `clipcheck.py` | PPTX 원문과 PDF 를 대조해 **잘린 글자**를 찾는다. 변환 뒤 필수 |
| `pagecount.mjs` | `slides/*.pdf`의 쪽 수. PPTX 장수와 대조용 |
| `pdftext.mjs` | PDF **쪽별** 텍스트. `data-slide` 앵커를 달기 전 대조용 |
| `render-slides.mjs` | PDF 쪽을 PNG로 렌더 → `shots/slides/` |

## 워크플로우

새 강의 노트를 쓰기 전에, 슬라이드를 저장소에 넣는 순서:

1. **강의 사이트에서 `lecture/` 로 받는다.** 이미 있는 것도 갱신됐을 수 있다.
   **강사가 파일 앞에 붙인 번호는 강의 번호가 아니다.** 6번부터 Lab 자료 때문에 밀렸다.
   `docs/schedule.md` 의 주제와 날짜로 대조해서 `L{NN}` 을 정한다.
2. **PPTX를 PDF로 변환한다.** `powershell -File scripts/pptx2pdf.ps1`
   `$map` 에 한 줄 추가하고, 파일명은 노트와 stem 을 맞춘다 (`slides/L{NN}-{topic}.pdf`).
   이미 있는 PDF 는 건너뛴다. 다시 만들려면 `-Force`.
3. **두 가지를 확인한다. 둘 다 통과해야 한다.**
   - `node scripts/pagecount.mjs` : PPTX 장수 = PDF 쪽 수. 다르면 숨김 슬라이드가 빠진 것이다
   - `python scripts/clipcheck.py "<pptx>" "<pdf>"` : 잘린 글자. 걸린 쪽은 렌더해서 눈으로 본다
4. **슬라이드 본문과 발표자 노트를 뽑아 읽는다.**
   `python scripts/pptx-text.py "<pptx>"`. 필요하면 강의 사이트의 Material 링크도 확인한다.
   **노트에 옮길 문구는 PDF 가 아니라 이 XML 추출을 원본으로 삼는다.** 변환기가 무엇이든
   PDF 텍스트 층은 렌더 결과물이라 믿을 것이 못 된다.
   **읽으면서 어느 개념이 몇 쪽인지 기록해둔다.**

여기서부터는 `write-note` 스킬의 몫이다.
