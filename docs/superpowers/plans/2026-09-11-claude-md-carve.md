# CLAUDE.md 카브 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `CLAUDE.md` 의 절차 86% 를 온디맨드 스킬로 내려 세션당 컨텍스트 비용을 줄이되, 컨텍스트 없는 에이전트가 기존 활동을 끝까지 할 수 있게 유지한다.

**Architecture:** 스킬을 **먼저** 만들어 내용을 안착시킨 뒤 `CLAUDE.md` 를 마지막에 깎는다. 그래야 내용이 어디에도 없는 구간이 생기지 않는다. 검증은 자동 검사가 없으므로 **컨텍스트 없는 서브에이전트 3 문항** 으로 카브 전후를 대조한다.

**Tech Stack:** Markdown, git, Python 3 (섹션 추출), Agent 툴 (서브에이전트 프로브)

**Spec:** `docs/superpowers/specs/2026-09-11-claude-md-carve-design.md`

## Global Constraints

- **규약 내용을 바꾸지 않는다. 옮기기만 한다.** 압축은 중복 제거 수준까지만
- 노트 HTML, `reader.js`, `scripts/` 의 코드는 건드리지 않는다
- 스킬 frontmatter 는 `name` 과 `description` 두 필드. `description` 은 한국어, "~할 때 쓴다" + 호출 트리거 문구로 끝낸다 (기존 3 개 스킬과 동일한 형식)
- 모든 스킬 본문은 한국어 반말체. em dash 금지
- 스킬 파일 경로는 `.claude/skills/<name>/SKILL.md`
- 커밋 메시지는 한 줄 영어 + `Claude-Session:` 트레일러
- Python 을 셸에서 돌릴 때 `PYTHONIOENCODING=utf-8` 을 준다. 안 주면 한글 출력이 `UnicodeEncodeError` 로 죽는다
- 파일은 UTF-8 로 쓴다. `io.open(..., encoding='utf-8')`

---

### Task 1: 기준선 캡처

카브 전에 "지금 문서로 답할 수 있는 것" 을 기록한다. 이게 없으면 나중에
"원래도 못 답했던 것" 과 "카브가 깨뜨린 것" 을 구별할 수 없다.

**Files:**
- Create: `docs/superpowers/plans/baseline-2026-09-11.md`

- [ ] **Step 1: 현재 자수를 기록한다**

```bash
cd "D:/Engineering/asu-cen-598-addv-fa26-notes"
PYTHONIOENCODING=utf-8 python -c "import io; print(len(io.open('CLAUDE.md',encoding='utf-8').read()))"
```

기대값: `34719` (다르면 문서가 그새 바뀐 것이니 spec 의 수치를 갱신하고 진행)

- [ ] **Step 2: 서브에이전트 3 마리를 동시에 띄운다**

Agent 툴, `subagent_type: "general-purpose"`, 세 개를 **한 메시지에** 보낸다.
각 프롬프트는 아래 그대로. 대화 맥락을 주지 않는다.

프로브 A:
```
D:\Engineering\asu-cen-598-addv-fa26-notes 저장소에서 Lecture 5 강의 노트를 새로
만들려고 한다. 무엇을 어떤 순서로 해야 하는지 단계별로 답하라. 실제로 작업하지 말고
절차만 답하라. 근거로 삼은 파일 경로를 각 단계에 밝혀라.
```

프로브 B:
```
D:\Engineering\asu-cen-598-addv-fa26-notes 저장소에서 커밋하면 안 되는 파일은
무엇인가. 이유와 함께 답하라. 근거로 삼은 파일 경로를 밝혀라.
```

프로브 C:
```
D:\Engineering\asu-cen-598-addv-fa26-notes 저장소의 강의 노트에 새 도해(SVG)를
추가하려고 한다. 색을 어떻게 골라야 하는가. 근거로 삼은 파일 경로를 밝혀라.
```

- [ ] **Step 3: 답변을 기준선 파일에 그대로 저장한다**

`baseline-2026-09-11.md` 에 프로브별로 원문을 붙인다. 요약하지 않는다.
Task 7 에서 **문자 그대로 대조** 할 것이라 요약하면 쓸모가 없다.

다음 항목이 답에 들어 있는지 표시해 둔다. 이게 합격선이다.

| 프로브 | 들어 있어야 할 것 |
|---|---|
| A | PPTX→PDF 변환, 숨김 슬라이드 포함, 발표자 노트, `data-slide` 앵커, `verify.mjs`, `langcheck.mjs`, `glossary.html` 갱신, `index.html` 갱신 |
| B | Lab 코드, quiz/exam, `*.pptx`, `shots/`, `node_modules/` |
| C | 의미 고정 색상 (Design=blue, Verification=pink, 도구=violet 등), 하드코딩 금지 |

- [ ] **Step 4: 커밋**

```bash
git add docs/superpowers/plans/baseline-2026-09-11.md
git commit -m "Capture the pre-carve baseline probe answers"
```

---

### Task 2: `docs/schedule.md` 추출

30 강 모듈 표를 데이터 파일로 뺀다. 두 스킬이 참조할 단일 출처다.

**Files:**
- Create: `docs/schedule.md`
- Modify: `CLAUDE.md` (모듈 목록 섹션 제거는 Task 6 에서. 여기서는 **복사만** 한다)

**Interfaces:**
- Produces: `docs/schedule.md` — Task 4 (`convert-slides`) 와 Task 5 (`write-note`) 가 경로로 참조한다

- [ ] **Step 1: 섹션을 그대로 뽑아낸다**

```bash
cd "D:/Engineering/asu-cen-598-addv-fa26-notes"
PYTHONIOENCODING=utf-8 python - <<'PY'
import io,re
s=io.open('CLAUDE.md',encoding='utf-8').read()
m=re.search(r'^## 모듈 목록 \(전체 30강\)\n(.*?)(?=^## )',s,flags=re.M|re.S)
body=m.group(1).strip()
head="""# 강의 일정 (전체 30강)

강의 사이트 Schedule 표 기준. **`index.html` 의 뼈대이고, `write-note` 와
`convert-slides` 가 함께 참조하는 단일 출처다.** 여기만 고친다.

"""
io.open('docs/schedule.md','w',encoding='utf-8').write(head+body+"\n")
print(len(body))
PY
```

- [ ] **Step 2: 표가 30 강 전부 살아 있는지 확인한다**

```bash
grep -c "^| [0-9]" docs/schedule.md
```

기대값: `29` (표에 Lecture 3 이 없고 10 과 11 이 순서가 바뀌어 있는 게 정상. 행 수만 센다)

행 수가 다르면 추출 정규식이 섹션을 잘못 잘랐다. 손으로 대조한다.

- [ ] **Step 3: 커밋**

```bash
git add docs/schedule.md
git commit -m "Extract the 30-lecture schedule into its own reference file"
```

---

### Task 3: `note-html` 스킬 신설

노트 HTML 을 **만드는** 규격. 기존 노트를 고칠 때는 이것만 있으면 된다.

**Files:**
- Create: `.claude/skills/note-html/SKILL.md`

**Interfaces:**
- Produces: 스킬 이름 `note-html` — Task 5 (`write-note`) 와 Task 6 (라우터) 이 이 이름으로 가리킨다

- [ ] **Step 1: frontmatter 와 자족성 블록을 쓴다**

```markdown
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
```

- [ ] **Step 2: `CLAUDE.md` 에서 해당 섹션들을 그대로 옮긴다**

옮길 섹션 (`## ` 를 `## ` 그대로 유지, 순서는 아래대로):

1. `HTML 기술 규격` 전체
2. `다크모드` 전체
3. `이중 언어 (한국어 / 영어)` 전체
4. `상단 미니 헤더` 전체
5. `슬라이드 리더 (데스크톱 전용)` 전체
6. `파일 명명` 중 **파일 트리와 명명 규칙 부분만** (`### scripts/` 하위 표는 제외)
7. `검증` 의 `### 모바일 오버플로우가 났을 때` 하위 표. 레이아웃 문제라 여기가 맞다.
   나머지 `검증` 본문은 Task 5 로 간다

추출 명령:

```bash
cd "D:/Engineering/asu-cen-598-addv-fa26-notes"
PYTHONIOENCODING=utf-8 python - <<'PY'
import io,re
s=io.open('CLAUDE.md',encoding='utf-8').read()
def sec(title):
    m=re.search(r'^## '+re.escape(title)+r'\n(.*?)(?=^## )',s,flags=re.M|re.S)
    return '## '+title+'\n'+m.group(1).rstrip()+'\n\n'
out=''
for t in ['HTML 기술 규격','다크모드','이중 언어 (한국어 / 영어)','상단 미니 헤더','슬라이드 리더 (데스크톱 전용)','파일 명명']:
    out+=sec(t)
io.open('/tmp/note-html-body.md','w',encoding='utf-8').write(out)
print(len(out))
PY
```

`/tmp/note-html-body.md` 를 열어 `파일 명명` 의 `### scripts/` 표에서
`serve.mjs` 와 `crop.mjs` 두 줄만 남기고 나머지 스크립트 행은 지운다.
지운 행은 Task 4 와 Task 5 로 간다.

- [ ] **Step 3: 합쳐서 저장한다**

Step 1 의 머리말 + Step 2 의 본문을 이어 `.claude/skills/note-html/SKILL.md` 로 쓴다.

- [ ] **Step 4: 내용이 유실되지 않았는지 확인한다**

```bash
cd "D:/Engineering/asu-cen-598-addv-fa26-notes"
for k in "--blue-rgb" "prefers-color-scheme" "lang=\"en\"" "data-slide" "viewBox" "minmax(0,1fr)" "sec-head"; do
  printf "%-24s %s\n" "$k" "$(grep -c -- "$k" .claude/skills/note-html/SKILL.md)"
done
```

전부 1 이상이어야 한다. 0 이 있으면 그 섹션이 통째로 빠진 것이다.

- [ ] **Step 5: 커밋**

```bash
git add .claude/skills/note-html/
git commit -m "Add the note-html skill holding the HTML authoring spec"
```

---

### Task 4: `convert-slides` 스킬 신설

슬라이드를 저장소에 **넣는** 절차. 노트를 쓰기 전에 반드시 선행한다.

**Files:**
- Create: `.claude/skills/convert-slides/SKILL.md`

**Interfaces:**
- Consumes: `docs/schedule.md` (Task 2)
- Produces: 스킬 이름 `convert-slides` — Task 5 와 Task 6 이 가리킨다

- [ ] **Step 1: frontmatter 와 자족성 블록을 쓴다**

```markdown
---
name: convert-slides
description: 강의 PPTX 를 slides/*.pdf 로 변환해 저장소에 넣을 때 쓴다. 숨김 슬라이드를 되살려 쪽 번호를 맞추는 것, 발표자 노트 추출, Drive 원본 갱신 확인, 강의 사이트 Schedule 대조까지. 노트를 쓰기 전에 먼저 끝나 있어야 한다. "슬라이드 변환 / PPTX / 새 강의 올라왔나 / Schedule 대조"에서 호출한다.
---

# 슬라이드를 저장소에 넣기

**같이 필요한 스킬**
- 변환이 끝나면 노트 작성은 `write-note`
- 강의 사이트가 로그인을 요구하면 `synopsys-training` 또는 `synopsys-training-chrome`

**참조**: 강의 번호·날짜·강사는 `docs/schedule.md` 가 단일 출처다. 여기에 옮겨 적지 않는다

**이 스킬만으로 끝나는 것**: 슬라이드 변환, 쪽 수 대조, 발표자 노트 추출
```

- [ ] **Step 2: `CLAUDE.md` 에서 해당 섹션들을 옮긴다**

1. `슬라이드 변환 (PPTX → PDF)` 전체
2. `강의 사이트가 원천이다` 중 **Notion 긁기와 Schedule 대조 부분** (`### 로그인이 필요한 자료` 이하 브라우저 절은 제외 — 그건 `CLAUDE.md` 결정표와 synopsys 스킬로 간다)
3. `경로` 의 Drive 원본 경로와 "학기 중에 갱신된다" 문단
4. `파일 명명` 의 `scripts/` 표에서 `pptx2pdf.ps1`, `pptx-text.py`, `hidden-slides.py`, `pagecount.mjs`, `pdftext.mjs`, `render-slides.mjs` 여섯 행
5. `워크플로우` 의 1~3 단계

- [ ] **Step 3: 유실 확인**

```bash
cd "D:/Engineering/asu-cen-598-addv-fa26-notes"
for k in "ppSaveAsPDF" "PrintHiddenSlides" "hidden-slides.py" "pagecount.mjs" "notion-collection-item" "BOM"; do
  printf "%-26s %s\n" "$k" "$(grep -c -- "$k" .claude/skills/convert-slides/SKILL.md)"
done
```

전부 1 이상.

- [ ] **Step 4: 커밋**

```bash
git add .claude/skills/convert-slides/
git commit -m "Add the convert-slides skill for getting decks into the repo"
```

---

### Task 5: `write-note` 확장

노트에 **무엇을** 쓸지를 정하는 규약 전부를 흡수한다. 지금 156 줄에서 크게 늘어난다.

**Files:**
- Modify: `.claude/skills/write-note/SKILL.md`

**Interfaces:**
- Consumes: `note-html` (Task 3), `convert-slides` (Task 4), `docs/schedule.md` (Task 2)

- [ ] **Step 1: 자족성 블록을 맨 위에 넣는다**

```markdown
**같이 필요한 스킬**
- HTML 을 실제로 만드는 규격은 `note-html`. **이 스킬만 읽고 노트를 쓰면 안 된다**
- 슬라이드 PDF 가 아직 `slides/` 에 없으면 `convert-slides` 를 먼저

**참조**: 강의 번호·날짜·강사는 `docs/schedule.md`

**이 스킬만으로 끝나는 것**: 무엇을 쓸지 정하는 것. 5 단 구조 설계, 용어 선별, 함정 발굴
```

- [ ] **Step 2: `CLAUDE.md` 에서 해당 섹션들을 흡수한다**

1. `EEE 554 노트와 무엇이 다른가` 전체
2. `내용의 근거` 중 불변식 3 줄을 뺀 나머지 (근거 3 종의 설명, 슬라이드 밖 내용 표기법)
3. `언어와 문체` 중 불변식 3 줄을 뺀 나머지 (발표자 노트를 읽는다 포함)
4. `강의 노트의 5단 구조` 전체
5. `.jargon — 용어 뜯어보기` 전체
6. `약어 사전 (glossary.html)` 전체
7. `함정 섹션 작성 원칙` 전체
8. `강의 간 연결` 전체
9. `Lab과 Quiz 처리 원칙` 전체
10. `워크플로우` 의 4~12 단계
11. `검증` 에서 **모바일 오버플로우 표를 뺀 나머지 전체.** 그 표는 레이아웃 문제라
    Task 3 에서 `note-html` 로 갔다. 여기서는 한 줄로 가리키기만 한다
12. `파일 명명` 의 `scripts/` 표에서 `verify.mjs`, `langcheck.mjs`, `readercheck.mjs` 세 행

기존 `write-note` 본문과 겹치는 대목은 **CLAUDE.md 쪽 서술을 남긴다.** 그쪽이 원본이고 더 상세하다.

- [ ] **Step 3: 유실 확인**

```bash
cd "D:/Engineering/asu-cen-598-addv-fa26-notes"
for k in "풀네임" "언제" "누가" "헷갈리는 것" "Lockdown" "24시간당 15%" "glossary.html" "readercheck" "langcheck" "발표자 노트"; do
  printf "%-20s %s\n" "$k" "$(grep -c -- "$k" .claude/skills/write-note/SKILL.md)"
done
```

전부 1 이상.

- [ ] **Step 4: 커밋**

```bash
git add .claude/skills/write-note/
git commit -m "Fold the note-writing conventions into the write-note skill"
```

---

### Task 6: `CLAUDE.md` 재작성

여기서 처음으로 **지운다.** 앞의 네 태스크가 끝나 있어야 안전하다.

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: 앞선 태스크가 전부 커밋됐는지 확인한다**

```bash
cd "D:/Engineering/asu-cen-598-addv-fa26-notes"
git status --short
ls .claude/skills/
```

`git status` 가 깨끗하고 스킬이 5 개(`write-note`, `note-html`, `convert-slides`, `synopsys-training`, `synopsys-training-chrome`) 보여야 한다. 아니면 멈춘다.

- [ ] **Step 2: 새 `CLAUDE.md` 를 쓴다**

이 골격만 남긴다.

```
# CEN 598 ADDV 학습 노트 프로젝트
## 이 저장소가 하는 일          기존 그대로
## 착수 — 스킬 라우터            아래 Step 3
## 경로                          기존에서 Drive 갱신 문단 제거 (convert-slides 로 갔음)
## 브라우저 고르기               기존 결정표 8 줄만. 운용 상세 제거
## 절대 어기지 않는 것            아래 Step 4
## 커밋하는 것과 안 하는 것       기존에서 rationale 압축
```

- [ ] **Step 3: 라우터를 작업 단위로 쓴다**

```markdown
## 착수 — 스킬 라우터

**절차는 전부 `.claude/skills/` 에 있다. 이 문서는 어겼을 때 되돌리기 비싼 것만 담는다.**

| 하려는 일 | 읽을 스킬 |
|---|---|
| 새 강의 노트를 쓴다 | `convert-slides` → `write-note` → `note-html` **셋 다** |
| 기존 노트의 문구·도해를 고친다 | `note-html` |
| Lab 공략 페이지를 쓴다 | `write-note` → `note-html` |
| 슬라이드만 저장소에 넣는다 | `convert-slides` |
| Synopsys 트레이닝을 수집한다 | `synopsys-training` (또는 `-chrome`) |

강의 번호·날짜·강사는 `docs/schedule.md` 가 단일 출처다.

**불변식은 이 문서가 이긴다. 각 절차의 단일 출처는 해당 스킬이다.**
```

- [ ] **Step 4: 불변식 블록을 쓴다**

```markdown
## 절대 어기지 않는 것

스킬을 안 읽고 들어와도 이것만은 어기면 안 된다. **판단 기준은 "어겼을 때 되돌리기가 비싼가" 다.**

- **교재가 없다.** 강의계획서가 "There is no textbook for this course" 라고 명시한다.
  비슷한 책을 교재로 적지 않는다. footer 에 교재 줄을 넣지 않는다
- **용어를 지어내지 않는다.** 이 과목의 최대 위험이다. 업계에서 안 쓰는 말을 그럴듯하게
  만들어내는 것. 확신이 없으면 슬라이드 표현을 쓰고 "강의에서는 이렇게 부른다" 로 범위를 좁힌다.
  **자동 검사가 못 잡는다**
- **em dash(—) 금지.** 콜론, 쉼표, 마침표를 쓴다 (SVG 안과 구분선은 예외)
- **업계 용어는 영어 유지, 서술은 한국어.** netlist, tapeout, DUT, RTL 을 번역하거나 음차하지 않는다
- **Drive 원본은 읽기 전용.** `D:\Library\...\CEN 598  ADDV` 를 수정하지 않는다
- **색을 하드코딩하지 않는다.** 그리고 의미가 고정돼 있다

| 대상 | 색 |
|---|---|
| Design (RTL, 설계자, front-end) | `--blue` |
| Verification (testbench, 검증 엔지니어) | `--pink` |
| 도구와 자동화 (synthesis, STA, simulator) | `--violet` |
| 통과·정답·sign-off | `--green` |
| 버그, 함정, 실패 | `--amber` |
| 물리·back-end (P&R, fab, silicon) | `--brown` |
| 이 강의 범위 밖 | `--ink3` |
```

- [ ] **Step 5: 목표 자수에 들어왔는지 확인한다**

```bash
cd "D:/Engineering/asu-cen-598-addv-fa26-notes"
PYTHONIOENCODING=utf-8 python -c "import io; n=len(io.open('CLAUDE.md',encoding='utf-8').read()); print(n, 'target <= 7000')"
```

7,000 자를 넘으면 아직 절차가 남아 있다. 어느 섹션인지 찾아 해당 스킬로 마저 내린다.

- [ ] **Step 6: 커밋**

```bash
git add CLAUDE.md
git commit -m "Cut CLAUDE.md down to the invariants and the skill router"
```

---

### Task 7: 검증과 보정

**Files:**
- Modify: `.claude/skills/*/SKILL.md` (프로브가 실패한 경우에만)
- Modify: `CLAUDE.md` (라우터가 실패한 경우에만)

- [ ] **Step 1: Task 1 과 똑같은 프로브 3 개를 다시 띄운다**

프롬프트를 **한 글자도 바꾸지 않는다.** 바꾸면 대조가 성립하지 않는다.

- [ ] **Step 2: 기준선과 대조한다**

`baseline-2026-09-11.md` 의 합격선 표를 항목별로 체크한다.
**카브 전에 나왔던 항목이 카브 후에 빠졌으면 실패다.**

- [ ] **Step 3: 실패하면 라우터를 고친다. 내용을 되돌리지 않는다**

내용은 이미 스킬에 있다. 못 찾은 것이므로 고칠 곳은 둘 중 하나다.

- 스킬 `description` 에 그 작업의 트리거 문구가 없다 → `description` 보강
- `CLAUDE.md` 라우터 표에 그 작업 행이 없거나 스킬 조합이 빠졌다 → 표 보강

고친 뒤 Step 1 로 돌아간다.

- [ ] **Step 4: 최종 수치를 기록하고 커밋**

```bash
cd "D:/Engineering/asu-cen-598-addv-fa26-notes"
PYTHONIOENCODING=utf-8 python -c "
import io,glob
c=len(io.open('CLAUDE.md',encoding='utf-8').read())
s=sum(len(io.open(f,encoding='utf-8').read()) for f in glob.glob('.claude/skills/*/SKILL.md'))
print(f'CLAUDE.md {c:,} (before 34,719)  skills {s:,}')
"
git add -A
git commit -m "Verify the carve with context-free probes"
```

---

## 완료 조건

- `CLAUDE.md` 가 7,000 자 이하
- 프로브 3 문항이 기준선과 같거나 나은 답을 낸다
- `git status` 가 깨끗하다
- `node scripts/verify.mjs` 가 여전히 통과한다 (노트를 안 건드렸으니 통과해야 정상)
