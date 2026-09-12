# 카브 결과 (2026-09-11)

기준선 `docs/superpowers/plans/baseline-2026-09-11.md` 와 대조한 결과다.

## 수치

| | 전 | 후 |
|---|---|---|
| `CLAUDE.md` (매 세션 로드) | 34,719 자 | **3,967 자** |
| 감축률 | | **89%** |

온디맨드로 내려간 것:

| 파일 | 자 |
|---|---|
| `.claude/skills/convert-slides/SKILL.md` | 4,683 |
| `.claude/skills/note-html/SKILL.md` | 13,481 |
| `.claude/skills/synopsys-training-chrome/SKILL.md` | 5,638 |
| `.claude/skills/synopsys-training/SKILL.md` | 6,801 |
| `.claude/skills/write-note/SKILL.md` | 15,381 |
| `docs/schedule.md` | 2,266 |

## 프로브 대조

카브 전과 **한 글자도 다르지 않은 프롬프트**로 다시 던졌다.

| 프로브 | 합격선 | 카브 전 | 카브 후 |
|---|---|---|---|
| A 새 강의 노트 절차 | 8 항목 | 8/8 | **8/8** |
| B 커밋 금지 대상 | 5 항목 | 5/5 | **5/5** |
| C 도해 색 고르기 | 2 항목 | 2/2 | **2/2** |

**회귀 없음.** 프로브 A 는 오히려 나아졌다. 카브 전에는 원본을 PDF 로 오인해 변환 단계를
건너뛰었는데, 카브 후에는 `convert-slides` 를 먼저 읽고 PPTX 변환, 숨김 슬라이드 판서 확인
(L04 s25 선례), `pptx2pdf.ps1` 의 BOM 함정까지 짚었다.

**라우터가 실제로 작동했다.** 프로브 A 가 첫 줄에서
`convert-slides` -> `write-note` -> `note-html` 순서를 스스로 정하고 시작했다.

## 남은 문제

`CLAUDE.md` 의 `.gitignore` 스니펫이 실제 파일과 다르다. **카브 이전부터 있던 드리프트이고
카브가 만든 것이 아니다.** 문서에는 5 줄만 있는데 실제로는 `*.pptx`, `lab/**/materials/`,
`lab/**/*.png`, `.build-*.html`, `.gstack/` 등이 더 있다. 공개 금지의 핵심 두 개가 문서에 없다.
문서에 사본을 두는 한 또 갈라지므로 스니펫을 지우고 파일을 가리키는 것이 맞다.
