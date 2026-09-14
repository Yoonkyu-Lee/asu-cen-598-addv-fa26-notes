# 실습 입문 페이지 (P03 · P04) 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 코드 · 회로 · 파형을 한 시크바에 묶어 반 클럭 단위로 밟아보는 시뮬레이션 엔진(`sim.js`)과 트레이스 검사기(`scripts/simcheck.mjs`)를 만들고, 그 위에 3 강과 4 강을 읽기 전에 손에 익힐 동작을 다루는 페이지 둘(`P03`, `P04`)을 낸다.

**Architecture:** 시나리오는 페이지 안 `<script type="application/json" id="sim-data">` 에 데이터로만 둔다. 루트의 `sim.js` 가 `.sim[data-sim]` 카드마다 그 데이터를 읽어 코드 · 회로 · 파형 세 렌더러와 시크바를 붙이고, 프레임 번호 하나(`go(i)`)로 셋을 같이 다시 칠한다. `scripts/simcheck.mjs` 는 같은 JSON 을 꺼내 노드 종류(ff · latch · 게이트)의 의미대로 트레이스를 재계산해 손으로 쓴 값과 대조한다.

**Tech Stack:** 바닐라 JS (ES module, 외부 의존성 없음), SVG, 기존 `scripts/verify.mjs` · `langcheck.mjs` (playwright), 파이썬 빌더 (`.gstack/tmp/`).

**Spec:** `docs/superpowers/specs/2026-09-13-hands-on-primer-design.md`

## Global Constraints

- 파일명 `notes/P{NN}-{kebab}.html`. 이번은 `notes/P03-before-lecture-3.html`, `notes/P04-before-lecture-4.html`.
- `data-slide` 없음. `reader.js` 없음. 대신 `<script src="../sim.js" type="module"></script>` 한 줄.
- `sim.js` 는 루트(`reader.js` 옆). 인라인 규칙의 두 번째 예외이고 `note-html` 스킬에 그렇게 적는다.
- 프레임 단위는 반 클럭. 프레임 `2k` = posedge 직후 (`clk=1`), `2k+1` = 정착 (`clk=0`). `frames` 길이는 짝수, 첫 프레임은 엣지.
- 값은 `0` / `1` / 정수 (`signals[].bits`) / `"X"` / `"M"`. 파형은 프레임에서 자동 생성. 손으로 그리는 파형 없음.
- 색은 토큰만. 논리 · 배선 `--blue`, 클럭선 `--brown`, `X` · `M` · latch 투명 `--amber`, 잡힘 `--green`. 리터럴 색 금지.
- 이중 언어 `lang="ko"` / `lang="en"` 쌍. em dash 금지. 업계 용어는 영어 유지.
- 브라우저 저장소 금지. 상태는 JS 변수.
- 단원 형식: **코드 → 회로 → 밟아본다 → 한 줄 정리.** 퀴즈가 아니다. "~라고 생각하기 쉽다" 는 제목 한 줄에만.
- 검증: `simcheck.mjs` → `verify.mjs` → `langcheck.mjs` → `.gstack/tmp/simstep.mjs`. 전부 exit 0.
- 커밋 메시지는 영어. 페이지와 `sim.js` 는 같은 커밋에 넣는다 (페이지가 먼저 올라가면 스크립트 404).

## 파일 구조

| 파일 | 책임 |
|---|---|
| `scripts/simcheck.mjs` (새) | HTML 에서 `#sim-data` 를 꺼내 트레이스를 노드 의미대로 대조. `--selftest` 내장 |
| `sim.js` (새, 루트) | 카드 마운트, CSS 주입, 코드 · 회로 · 파형 렌더러, 시크바 · 재생 · 키보드, `langchange` |
| `scripts/verify.mjs` (수정 287 · 393 · 579줄) | `.sim` 을 도해 스크린샷과 SVG 겹침 검사 대상에 포함 |
| `.gstack/tmp/simfix.html` (새) | 엔진 개발용 고정 페이지. 시나리오 하나 |
| `.gstack/tmp/simstep.mjs` (새) | playwright 로 페이지의 모든 `.sim` 을 끝 프레임까지 밟고 DOM 상태와 콘솔 에러를 확인 |
| `.gstack/tmp/p03.py`, `p04.py` (새) | 페이지 빌더. 스타일 블록은 `notes/L01-course-intro.html` 에서 뽑는다 |
| `notes/P03-before-lecture-3.html`, `notes/P04-before-lecture-4.html` (새) | 페이지 |
| `index.html`, `notes/L03-*.html`, `notes/L04-*.html`, `.claude/skills/note-html/SKILL.md` (수정) | 허브 카드, 콜아웃, 명명 표 |

---

### Task 1: `scripts/simcheck.mjs` 트레이스 검사기

**Files:**
- Create: `scripts/simcheck.mjs`

**Interfaces:**
- Produces: `checkScenario(sc) → string[]` (에러 목록, 비면 통과). CLI: `node scripts/simcheck.mjs <html…>` 는 파일마다 `#sim-data` 를 꺼내 검사하고 하나라도 에러면 exit 1. `node scripts/simcheck.mjs --selftest` 는 내장 사례를 돌린다.
- 노드 의미 (Task 6 · 8 의 시나리오가 이 규칙에 맞아야 한다):
  - `ff` `in:{d, clk, rst_n?, arst_n?}` `out:{q}` `late?:true`. `arst_n=0` 인 프레임은 항상 `q=0`. 엣지 프레임 `i`: `rst_n[i-1]=0` 이면 `q=0`, 아니면 `q[i] = d[i-1]` (`late` 면 `d[i]`). 정착 프레임: `q[i] = q[i-1]`. 프레임 0 은 초기값이라 검사 안 함.
  - `latch` `in:{d, en}` `out:{q}`. `en=1` 이면 `q[i]=d[i]`, 아니면 `q[i]=q[i-1]`.
  - `and` `or` `xor` `in:{a,b}` `out:{y}`. `not` `buf` `delay` `in:{a}` `out:{y}`. `mux` `in:{a,b,sel}` `out:{y}` (`sel=1` 이면 `b`). `add` `in:{a,b}` `out:{y}` (`bits(y)` 로 mask). `const` `val` `out:{y}`.
  - 기대값이나 실제값에 `"X"` / `"M"` 이 끼면 그 칸은 건너뛴다.

- [ ] **Step 1: 자체 시험 사례를 먼저 적는다**

`scripts/simcheck.mjs` 를 아래 내용으로 만든다. 검사 함수는 아직 없고 selftest 만 있어서 실행하면 실패해야 한다.

```js
#!/usr/bin/env node
// scripts/simcheck.mjs
// P 페이지의 시뮬레이션 트레이스는 손으로 쓴다. 그래서 틀릴 수 있다.
// #sim-data 의 시나리오를 꺼내 노드 종류(ff · latch · 게이트)의 의미대로
// 값을 다시 계산하고 손으로 쓴 값과 대조한다. 어긋나면 exit 1.
import fs from 'node:fs';

// ── 자체 시험 사례 ──────────────────────────────────────────────
const GOOD = {
  id: 'self-ff',
  code: [{ t: 'always_ff @(posedge clk)' }, { t: '  q <= d;', drives: ['q'] }],
  circuit: { w: 320, h: 120,
    nodes: [{ id: 'f1', kind: 'ff', x: 140, y: 40, in: { d: 'd', clk: 'clk' }, out: { q: 'q' } }],
    ports: [], wires: [{ sig: 'd', pts: [[20, 60], [140, 60]] }] },
  signals: [{ n: 'clk', kind: 'clk' }, { n: 'd' }, { n: 'q' }],
  frames: [
    { v: { clk: 1, d: 0, q: 0 } }, { v: { clk: 0, d: 1, q: 0 } },
    { v: { clk: 1, d: 1, q: 1 } }, { v: { clk: 0, d: 0, q: 1 } },
    { v: { clk: 1, d: 0, q: 0 } }, { v: { clk: 0, d: 0, q: 0 } },
  ],
};
const clone = o => JSON.parse(JSON.stringify(o));
const CASES = [
  ['정상', GOOD, 0],
  ['엣지에서 d 를 안 잡음', (() => { const s = clone(GOOD); s.frames[2].v.q = 0; return s; })(), 1],
  ['정착 프레임에서 q 가 바뀜', (() => { const s = clone(GOOD); s.frames[3].v.q = 0; return s; })(), 1],
  ['프레임 수 홀수', (() => { const s = clone(GOOD); s.frames.pop(); return s; })(), 1],
  ['clk 가 엣지 프레임에서 0', (() => { const s = clone(GOOD); s.frames[2].v.clk = 0; return s; })(), 1],
  ['drives 에 없는 신호', (() => { const s = clone(GOOD); s.code[1].drives = ['zz']; return s; })(), 1],
  ['X 는 건너뜀', (() => { const s = clone(GOOD); s.frames[2].v.q = 'X'; s.frames[3].v.q = 'X'; return s; })(), 0],
];

function selftest() {
  let bad = 0;
  for (const [name, sc, want] of CASES) {
    const errs = checkScenario(sc);
    const ok = want === 0 ? errs.length === 0 : errs.length >= want;
    console.log(`${ok ? '[OK]' : '[FAIL]'} ${name}${ok ? '' : ' → ' + errs.join(' | ')}`);
    if (!ok) bad++;
  }
  process.exit(bad ? 1 : 0);
}

if (process.argv.includes('--selftest')) selftest();
```

- [ ] **Step 2: 실행해서 실패를 확인한다**

Run: `node scripts/simcheck.mjs --selftest`
Expected: `ReferenceError: checkScenario is not defined`

- [ ] **Step 3: 검사 함수와 CLI 를 넣는다**

`// ── 자체 시험 사례` 줄 **위에** 아래를 넣고, 파일 맨 아래 `if (process.argv.includes('--selftest')) selftest();` 를 CLI 블록으로 바꾼다.

```js
// ── 검사 ────────────────────────────────────────────────────────
const isXM = v => v === 'X' || v === 'M';
const mask = bits => (1 << bits) - 1;
const gate = (a, b, f) => (isXM(a) || isXM(b)) ? 'X' : f(a, b);

export function checkScenario(sc) {
  const errs = [];
  const F = sc.frames || [], N = F.length;
  const sigs = Object.fromEntries((sc.signals || []).map(s => [s.n, s]));
  const bits = n => (sigs[n] && sigs[n].bits) || 1;

  if (N === 0 || N % 2) errs.push(`${sc.id}: frames 길이가 짝수가 아니다 (${N})`);
  for (let i = 0; i < N; i++)
    for (const s of Object.keys(sigs))
      if (!F[i].v || !(s in F[i].v)) errs.push(`${sc.id} frame ${i}: 신호 ${s} 값이 없다`);

  const clk = (sc.signals || []).find(s => s.kind === 'clk');
  if (!clk) errs.push(`${sc.id}: kind:"clk" 신호가 없다`);
  else for (let i = 0; i < N; i++) {
    const want = i % 2 ? 0 : 1;
    if (F[i].v && F[i].v[clk.n] !== want) errs.push(`${sc.id} frame ${i}: ${clk.n} 는 ${want} 이어야 한다`);
  }

  for (const l of sc.code || []) for (const d of l.drives || [])
    if (!sigs[d]) errs.push(`${sc.id}: code drives 에 없는 신호 ${d}`);
  for (const w of (sc.circuit && sc.circuit.wires) || [])
    if (!sigs[w.sig]) errs.push(`${sc.id}: wire 에 없는 신호 ${w.sig}`);

  if (errs.length) return errs;                    // 구조가 깨졌으면 의미 검사는 무의미하다
  for (const n of (sc.circuit && sc.circuit.nodes) || []) checkNode(n, F, bits, errs, sc.id);
  return errs;
}

function checkNode(n, F, bits, errs, id) {
  const N = F.length;
  const v = (i, s) => F[i].v[s];
  const IN = n.in || {}, OUT = n.out || {};
  const expect = (i, s, want) => {
    const got = v(i, s);
    if (want === undefined || isXM(got) || isXM(want)) return;
    if (got !== want) errs.push(`${id} frame ${i} ${n.id}.${s}: 기대 ${want}, 실제 ${got}`);
  };
  for (let i = 0; i < N; i++) {
    switch (n.kind) {
      case 'ff': {
        if (IN.arst_n && v(i, IN.arst_n) === 0) { expect(i, OUT.q, 0); break; }
        if (i === 0) break;
        if (i % 2 === 0) {
          if (IN.rst_n && v(i - 1, IN.rst_n) === 0) expect(i, OUT.q, 0);
          else expect(i, OUT.q, v(n.late ? i : i - 1, IN.d));
        } else expect(i, OUT.q, v(i - 1, OUT.q));
        break;
      }
      case 'latch':
        if (v(i, IN.en) === 1) expect(i, OUT.q, v(i, IN.d));
        else if (i > 0) expect(i, OUT.q, v(i - 1, OUT.q));
        break;
      case 'and': expect(i, OUT.y, gate(v(i, IN.a), v(i, IN.b), (a, b) => a & b)); break;
      case 'or':  expect(i, OUT.y, gate(v(i, IN.a), v(i, IN.b), (a, b) => a | b)); break;
      case 'xor': expect(i, OUT.y, gate(v(i, IN.a), v(i, IN.b), (a, b) => a ^ b)); break;
      case 'not': expect(i, OUT.y, gate(v(i, IN.a), 0, a => (a ? 0 : 1))); break;
      case 'buf': case 'delay': expect(i, OUT.y, v(i, IN.a)); break;
      case 'mux': { const s = v(i, IN.sel); if (!isXM(s)) expect(i, OUT.y, v(i, s ? IN.b : IN.a)); break; }
      case 'add': expect(i, OUT.y, gate(v(i, IN.a), v(i, IN.b), (a, b) => (a + b) & mask(bits(OUT.y)))); break;
      case 'const': expect(i, OUT.y, n.val); break;
      default: errs.push(`${id}: 모르는 노드 종류 ${n.kind}`); return;
    }
  }
}

// ── CLI ─────────────────────────────────────────────────────────
export function extractData(html) {
  const m = html.match(/<script type="application\/json" id="sim-data">([\s\S]*?)<\/script>/);
  if (!m) throw new Error('#sim-data 를 못 찾았다');
  return JSON.parse(m[1]);
}
```

파일 맨 아래는 이렇게:

```js
const argv = process.argv.slice(2);
if (argv.includes('--selftest')) selftest();
else if (argv.length === 0) { console.error('usage: node scripts/simcheck.mjs <html…> | --selftest'); process.exit(2); }
else {
  let bad = 0;
  for (const f of argv) {
    const data = extractData(fs.readFileSync(f, 'utf8'));
    for (const sc of data) {
      const errs = checkScenario(sc);
      console.log(`${errs.length ? '[FAIL]' : '[OK]'} ${f} · ${sc.id} · frames ${sc.frames.length}`);
      errs.forEach(e => console.log('   · ' + e));
      if (errs.length) bad++;
    }
  }
  process.exit(bad ? 1 : 0);
}
```

- [ ] **Step 4: 자체 시험을 통과시킨다**

Run: `node scripts/simcheck.mjs --selftest`
Expected: 7 줄 전부 `[OK]`, exit 0. (`'정착 프레임에서 q 가 바뀜'` 이 `[OK]` 인 것은 에러가 1 개 이상 잡혔다는 뜻이다.)

- [ ] **Step 5: 커밋**

```bash
git add scripts/simcheck.mjs
git commit -m "Add simcheck, a trace checker for the hands-on primer scenarios"
```

---

### Task 2: `sim.js` 골격 · 시크바 · 파형 렌더러

**Files:**
- Create: `sim.js` (루트)
- Create: `.gstack/tmp/simfix.html` (개발용 고정 페이지)
- Create: `.gstack/tmp/simstep.mjs` (playwright 확인)

**Interfaces:**
- Consumes: 시나리오 JSON 형식 (Task 1 의 `GOOD` 과 같은 모양) + `note:{ko,en}` 프레임 해설 + `title:{ko,en}`.
- Produces: 카드 DOM. `.sim` 안에 `.sim-grid > .sim-code, .sim-circ`, `.sim-wave > svg`, `.sim-bar > button[data-act=first|prev|next|last|play], input[type=range], .sim-label`, `.sim-note`. 카드 요소에 `el.simGo(i)` 와 `el.simFrame` (현재 프레임)을 붙인다 (Task 3 · 4 와 simstep 이 쓴다). 내부 `go(i)` 는 `renderers.forEach(r => r(i))` 를 부른다. Task 3 · 4 는 `renderers` 배열에 함수를 하나씩 더한다.

- [ ] **Step 1: 고정 페이지를 만든다**

`.gstack/tmp/simfix.html`. 스타일은 L01 에서 뽑아 넣는다.

```bash
node -e "const fs=require('fs');const s=fs.readFileSync('notes/L01-course-intro.html','utf8');const a=s.indexOf('<style>'),b=s.indexOf('</style>')+8;fs.writeFileSync('.gstack/tmp/.style.html',s.slice(a,b));"
```

그 다음 파이썬으로 조립한다 (`.gstack/tmp/mkfix.py`):

```python
# -*- coding: utf-8 -*-
import io, json
style = io.open(".gstack/tmp/.style.html", encoding="utf-8").read()
data = [{
  "id": "fix-ff",
  "title": {"ko": "flip-flop", "en": "flip-flop"},
  "code": [{"t": "always_ff @(posedge clk)"}, {"t": "  q <= d;", "drives": ["q"]}],
  "circuit": {"w": 320, "h": 120,
    "nodes": [{"id": "f1", "kind": "ff", "x": 140, "y": 40, "in": {"d": "d", "clk": "clk"}, "out": {"q": "q"}}],
    "ports": [{"sig": "d", "side": "in", "y": 56}, {"sig": "q", "side": "out", "y": 56}, {"sig": "clk", "side": "in", "y": 96}],
    "wires": [{"sig": "d", "pts": [[36, 56], [140, 56]]},
              {"sig": "q", "pts": [[196, 56], [284, 56]]},
              {"sig": "clk", "pts": [[36, 96], [120, 96], [120, 74], [140, 74]]}]},
  "signals": [{"n": "clk", "kind": "clk"}, {"n": "d"}, {"n": "q"}],
  "frames": [
    {"v": {"clk": 1, "d": 0, "q": 0}, "note": {"ko": "리셋 직후. 둘 다 0.", "en": "Just after reset. Both 0."}},
    {"v": {"clk": 0, "d": 1, "q": 0}, "note": {"ko": "d 가 1 로 올라갔다. q 는 아직.", "en": "d went to 1. q has not."}},
    {"v": {"clk": 1, "d": 1, "q": 1}, "note": {"ko": "엣지. q 가 d 를 잡았다.", "en": "Edge. q captured d."}},
    {"v": {"clk": 0, "d": 0, "q": 1}, "note": {"ko": "d 가 내려갔다. q 는 유지.", "en": "d fell. q holds."}},
    {"v": {"clk": 1, "d": 0, "q": 0}, "note": {"ko": "엣지. q 가 0 을 잡았다.", "en": "Edge. q captured 0."}},
    {"v": {"clk": 0, "d": 0, "q": 0}, "note": {"ko": "정착.", "en": "Settled."}}
  ]
}]
html = f'''<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>simfix</title>
{style}
</head><body><div class="wrap"><main>
<section id="s1"><div class="sec-head"><span class="sec-num">01</span><h2 lang="ko">고정</h2><h2 lang="en">Fixture</h2></div>
<div class="sim" data-sim="fix-ff"></div>
</section>
</main></div>
<script type="application/json" id="sim-data">{json.dumps(data, ensure_ascii=False)}</script>
<script src="../../sim.js" type="module"></script>
<button class="lang-btn" type="button">English</button>
<script>
(function () {{ var root = document.documentElement; var btn = document.querySelector('.lang-btn');
  btn.addEventListener('click', function () {{ root.dataset.lang = root.dataset.lang === 'en' ? 'ko' : 'en';
    root.lang = root.dataset.lang; window.dispatchEvent(new Event('langchange')); }}); }})();
</script>
</body></html>'''
io.open(".gstack/tmp/simfix.html", "w", encoding="utf-8").write(html)
print("wrote .gstack/tmp/simfix.html")
```

Run: `python .gstack/tmp/mkfix.py`

- [ ] **Step 2: 확인 스크립트를 먼저 쓴다**

`.gstack/tmp/simstep.mjs`. 저장소 루트를 서버로 띄우고 (verify.mjs 와 같은 이유: `file://` 에서는 모듈 로드가 막힌다) 페이지의 모든 `.sim` 을 끝까지 밟는다. 인자로 HTML 경로를 받는다.

```js
// .gstack/tmp/simstep.mjs — 페이지의 모든 .sim 을 끝 프레임까지 밟고 DOM 과 콘솔을 확인한다.
import { chromium } from 'playwright';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = process.cwd();
const FILE = process.argv[2];
if (!FILE) { console.error('usage: node .gstack/tmp/simstep.mjs <html>'); process.exit(2); }
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css', '.pdf': 'application/pdf' };
const srv = http.createServer((req, res) => {
  const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  if (!fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); res.end(); return; }
  res.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
});
await new Promise(r => srv.listen(4612, r));

const b = await chromium.launch();
const pg = await b.newPage();
const errs = [];
pg.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
pg.on('pageerror', e => errs.push(String(e)));
await pg.goto('http://127.0.0.1:4612/' + FILE.replace(/\\/g, '/'), { waitUntil: 'networkidle' });

const cards = await pg.$$('.sim[data-sim]');
let bad = 0;
for (const c of cards) {
  const id = await c.getAttribute('data-sim');
  const r = await c.$('input[type=range]');
  if (!r) { console.log(`[FAIL] ${id}: 시크바가 없다`); bad++; continue; }
  const n = Number(await r.getAttribute('max')) + 1;
  const seen = [];
  for (let i = 0; i < n; i++) {
    await c.evaluate((el, i) => el.simGo(i), i);
    seen.push(await c.evaluate(el => ({
      frame: el.simFrame,
      label: el.querySelector('.sim-label').textContent,
      note: el.querySelector('.sim-note').textContent.slice(0, 24),
      hotLines: el.querySelectorAll('.sim-code .ln.hot').length,
      edgeNodes: el.querySelectorAll('.sim-circ .node.edge').length,
      cursor: el.querySelector('.sim-wave .cur') ? Number(el.querySelector('.sim-wave .cur').getAttribute('data-i')) : -1,
    })));
  }
  const okFrames = seen.every((s, i) => s.frame === i && s.cursor === i);
  const okNotes = seen.every(s => s.note.length > 0);
  console.log(`${okFrames && okNotes ? '[OK]' : '[FAIL]'} ${id}: ${n} 프레임` +
    ` · 코드 강조 ${seen.map(s => s.hotLines).join('')} · 엣지 표시 ${seen.map(s => s.edgeNodes).join('')}`);
  if (!(okFrames && okNotes)) bad++;
}
// 언어 토글 뒤에도 해설이 바뀌는지
await pg.click('.lang-btn');
const enNote = await pg.$eval('.sim[data-sim] .sim-note', e => e.textContent);
console.log(`${/[가-힣]/.test(enNote) ? '[FAIL]' : '[OK]'} 영어 모드 해설: ${enNote.slice(0, 40)}`);
if (/[가-힣]/.test(enNote)) bad++;
console.log(errs.length ? `[FAIL] 콘솔 에러 ${errs.length}건\n  ` + errs.join('\n  ') : '[OK] 콘솔 에러 없음');
if (errs.length) bad++;
await b.close(); srv.close();
process.exit(bad ? 1 : 0);
```

- [ ] **Step 3: 실행해서 실패를 확인한다**

Run: `node .gstack/tmp/simstep.mjs .gstack/tmp/simfix.html`
Expected: `[FAIL] fix-ff: 시크바가 없다` 와 `[FAIL] 콘솔 에러` (sim.js 404). exit 1.

- [ ] **Step 4: `sim.js` 골격을 쓴다**

루트에 `sim.js`. 이 단계에서는 마운트 · CSS · 시크바 · 재생 · 키보드 · 해설 · 파형까지. 회로와 코드 패널은 빈 상자만 만든다.

```js
// sim.js — 반 클럭 프레임 시뮬레이션 뷰어.
// 페이지 안 #sim-data 의 시나리오를 .sim[data-sim] 카드에 붙인다.
// 프레임 2k 는 posedge 직후(clk=1), 2k+1 은 정착(clk=0)이다.
// 외부 의존성 없음. 이 파일이 없어도 본문은 그대로 읽힌다.

const CSS = `
.sim{margin:22px 0;padding:16px 18px;background:var(--card);border:1px solid var(--rule);border-radius:12px;outline:none}
.sim:focus-visible{border-color:var(--blue)}
.sim-title{font-family:var(--mono);font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink3);margin:0 0 10px}
.sim-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:14px;align-items:stretch}
@media(max-width:900px){.sim-grid{grid-template-columns:minmax(0,1fr)}}
.sim-code pre.code{margin:0;min-height:100%;box-sizing:border-box}
.sim-code .ln{display:block;padding-left:8px;margin-left:-8px;border-left:3px solid transparent;transition:background .15s}
.sim-code .ln.hot{border-left-color:var(--blue);background:rgba(var(--blue-rgb),.09)}
.sim-circ{background:var(--paper);border:1px solid var(--rule);border-radius:8px;padding:6px}
.sim-circ svg{width:100%;height:auto;display:block}
.sim-wave{margin-top:14px;overflow-x:auto;border:1px solid var(--rule);border-radius:8px;background:var(--paper)}
.sim-wave svg{display:block}
.sim-bar{display:flex;align-items:center;gap:8px;margin-top:12px;flex-wrap:wrap}
.sim-bar button{font-family:var(--mono);font-size:11.5px;padding:5px 9px;border:1px solid var(--rule);border-radius:7px;background:var(--card);color:var(--ink2);cursor:pointer}
.sim-bar button:hover{border-color:var(--blue);color:var(--blue)}
.sim-bar input[type=range]{flex:1;min-width:120px;accent-color:var(--blue)}
.sim-label{font-family:var(--mono);font-size:11px;letter-spacing:.05em;color:var(--ink2);white-space:nowrap}
.sim-note{margin:10px 0 0;font-size:14px;line-height:1.6;color:var(--ink);min-height:1.6em}
.sim-fail{font-family:var(--mono);font-size:12px;color:var(--ink3)}
.sim .wv{fill:none;stroke-linejoin:round}
.sim .wv.sig{stroke:var(--blue);stroke-width:2}
.sim .wv.clk{stroke:var(--brown);stroke-width:1.8}
.sim .wv.bus{stroke:var(--blue);stroke-width:1.6}
.sim .xm{fill:rgba(var(--amber-rgb),.22);stroke:var(--amber);stroke-width:1.2}
.sim .xm text,.sim .bust{font-family:var(--mono);font-size:10px;fill:var(--ink)}
.sim .xm text{fill:var(--amber)}
.sim .chgbar{fill:var(--blue);opacity:.55}
.sim .cur{fill:none;stroke:var(--blue);stroke-width:2;rx:3}
.sim .lab{font-family:var(--mono);font-size:10.5px;fill:var(--ink2)}
.sim .lab.clk{fill:var(--brown)}
.sim .cyc{font-family:var(--mono);font-size:9.5px;fill:var(--ink3)}
.sim .grid{stroke:var(--rule);stroke-width:1}
`;

function injectCSS() {
  if (document.getElementById('sim-css')) return;
  const s = document.createElement('style');
  s.id = 'sim-css';
  s.textContent = CSS;
  document.head.appendChild(s);
}

const L = (ko, en) => (document.documentElement.dataset.lang === 'en' ? en : ko);
const isXM = v => v === 'X' || v === 'M';
const changed = (sc, i, sig) => i > 0 && sc.frames[i].v[sig] !== sc.frames[i - 1].v[sig];

function el(tag, attrs = {}, txt) {
  const n = document.createElement(tag);
  for (const k in attrs) n.setAttribute(k, attrs[k]);
  if (txt !== undefined) n.textContent = txt;
  return n;
}
function svgEl(tag, attrs = {}, txt) {
  const n = document.createElementNS('http://www.w3.org/2000/svg', tag);
  for (const k in attrs) n.setAttribute(k, attrs[k]);
  if (txt !== undefined) n.textContent = txt;
  return n;
}

// ── 파형 ─────────────────────────────────────────────────────────
// 프레임 하나가 한 칸이다. 값이 바뀐 칸은 행 아래 얇은 바로 표시하고
// 커서는 테두리만 그린다. 칠한 사각형이 글자 위에 오면 verify 가 잡는다.
const CW = 30, RH = 28, LG = 68, TOP = 10;

function renderWave(sc, host) {
  const N = sc.frames.length, S = sc.signals;
  const W = LG + N * CW + 10, H = TOP + S.length * RH + 20;
  const svg = svgEl('svg', { viewBox: `0 0 ${W} ${H}`, width: W, height: H, role: 'img',
    'aria-label': L('프레임별 신호 파형', 'signal waveform per frame') });
  host.replaceChildren(svg);

  // 사이클 눈금. 엣지 프레임마다 세로선과 번호.
  for (let i = 0; i < N; i += 2) {
    const x = LG + i * CW;
    svg.appendChild(svgEl('line', { x1: x, y1: TOP, x2: x, y2: TOP + S.length * RH, class: 'grid' }));
    svg.appendChild(svgEl('text', { x: x + CW, y: H - 6, 'text-anchor': 'middle', class: 'cyc' }, String(i / 2)));
  }

  S.forEach((s, r) => {
    const y0 = TOP + r * RH, hi = y0 + 5, lo = y0 + RH - 7;
    const bits = s.bits || 1;
    svg.appendChild(svgEl('text', { x: LG - 8, y: y0 + RH / 2 + 4, 'text-anchor': 'end',
      class: 'lab' + (s.kind === 'clk' ? ' clk' : '') }, s.n));
    const val = i => sc.frames[i].v[s.n];

    if (bits === 1) {
      let d = '', pen = false;
      for (let i = 0; i < N; i++) {
        const x = LG + i * CW, v = val(i);
        if (isXM(v)) { pen = false; xmCell(svg, x, y0, v); continue; }
        const y = v ? hi : lo;
        if (!pen) { d += `M${x} ${y}`; pen = true; }
        else if (val(i - 1) !== v) d += `L${x} ${y}`;
        d += `L${x + CW} ${y}`;
      }
      svg.appendChild(svgEl('path', { d, class: 'wv ' + (s.kind === 'clk' ? 'clk' : 'sig') }));
    } else {
      // 버스: 같은 값이 이어지는 구간마다 육각 띠와 값 글자
      let i = 0;
      while (i < N) {
        let j = i; while (j + 1 < N && val(j + 1) === val(i)) j++;
        const x0 = LG + i * CW, x1 = LG + (j + 1) * CW, v = val(i);
        if (isXM(v)) { for (let k = i; k <= j; k++) xmCell(svg, LG + k * CW, y0, v); i = j + 1; continue; }
        const g = svgEl('g');
        g.appendChild(svgEl('path', { class: 'wv bus',
          d: `M${x0} ${(hi + lo) / 2} L${x0 + 4} ${hi} L${x1 - 4} ${hi} L${x1} ${(hi + lo) / 2} L${x1 - 4} ${lo} L${x0 + 4} ${lo} Z` }));
        g.appendChild(svgEl('text', { x: (x0 + x1) / 2, y: (hi + lo) / 2 + 3.5, 'text-anchor': 'middle', class: 'bust' }, String(v)));
        svg.appendChild(g);
        i = j + 1;
      }
    }
    // 값이 바뀐 칸 표시 (프레임에 따라 다시 그린다)
    for (let i = 1; i < N; i++) if (changed(sc, i, s.n))
      svg.appendChild(svgEl('rect', { x: LG + i * CW + 2, y: y0 + RH - 4, width: CW - 4, height: 3, class: 'chgbar', 'data-sig': s.n, 'data-i': i }));
  });

  const cur = svgEl('rect', { x: LG, y: TOP - 2, width: CW, height: S.length * RH + 4, class: 'cur', 'data-i': 0 });
  svg.appendChild(cur);
  return i => {
    cur.setAttribute('x', LG + i * CW);
    cur.setAttribute('data-i', i);
    // 현재 칸까지의 변화만 진하게. 앞으로 올 변화는 흐리게 남겨 예고한다.
    svg.querySelectorAll('.chgbar').forEach(b => b.setAttribute('opacity', Number(b.dataset.i) <= i ? '.55' : '.15'));
    const box = host.getBoundingClientRect();
    const cx = LG + i * CW;
    if (cx < host.scrollLeft + LG || cx + CW > host.scrollLeft + box.width) host.scrollLeft = Math.max(0, cx - box.width / 2);
  };
}

function xmCell(svg, x, y0, v) {
  const g = svgEl('g', { class: 'xm' });
  g.appendChild(svgEl('rect', { x: x + 1, y: y0 + 4, width: CW - 2, height: RH - 10, rx: 2 }));
  g.appendChild(svgEl('text', { x: x + CW / 2, y: y0 + RH / 2 + 3, 'text-anchor': 'middle' }, v));
  svg.appendChild(g);
}

// ── 카드 ─────────────────────────────────────────────────────────
function mount(card, sc) {
  card.tabIndex = 0;
  card.replaceChildren();
  if (!sc) { card.appendChild(el('p', { class: 'sim-fail' }, L('시뮬레이션을 못 불러왔다', 'simulation failed to load'))); return; }

  const title = el('p', { class: 'sim-title' });
  const grid = el('div', { class: 'sim-grid' });
  const codeHost = el('div', { class: 'sim-code' });
  const circHost = el('div', { class: 'sim-circ' });
  grid.append(codeHost, circHost);
  const waveHost = el('div', { class: 'sim-wave' });
  const bar = el('div', { class: 'sim-bar' });
  const btn = (act, t) => { const b = el('button', { type: 'button', 'data-act': act }, t); bar.appendChild(b); return b; };
  const bFirst = btn('first', '|◀'), bPrev = btn('prev', '◀');
  const range = el('input', { type: 'range', min: 0, max: sc.frames.length - 1, value: 0 });
  bar.appendChild(range);
  const bNext = btn('next', '▶'), bLast = btn('last', '▶|'), bPlay = btn('play', '');
  const label = el('span', { class: 'sim-label' });
  bar.appendChild(label);
  const note = el('p', { class: 'sim-note' });
  card.append(title, grid, waveHost, bar, note);

  const renderers = [];
  renderers.push(renderWave(sc, waveHost));
  if (typeof renderCircuit === 'function') renderers.push(renderCircuit(sc, circHost));
  if (typeof renderCode === 'function') renderers.push(renderCode(sc, codeHost));

  let i = 0, timer = null;
  const N = sc.frames.length;
  function paintText() {
    title.textContent = sc.title ? L(sc.title.ko, sc.title.en) : '';
    bPlay.textContent = timer ? L('❚❚ 멈춤', '❚❚ pause') : L('▶ 재생', '▶ play');
    const k = Math.floor(i / 2), phase = i % 2 === 0 ? L('엣지 직후', 'after edge') : L('정착', 'settled');
    label.textContent = `cycle ${k} · ${phase}`;
    const n = sc.frames[i].note;
    note.textContent = n ? L(n.ko, n.en) : '';
  }
  function go(j) {
    i = Math.max(0, Math.min(N - 1, j));
    range.value = i;
    card.simFrame = i;
    renderers.forEach(r => r(i));
    paintText();
  }
  function stop() { if (timer) { clearInterval(timer); timer = null; } paintText(); }
  function play() {
    if (timer) { stop(); return; }
    if (i >= N - 1) go(0);
    timer = setInterval(() => { if (i >= N - 1) stop(); else go(i + 1); }, 700);
    paintText();
  }
  bFirst.onclick = () => { stop(); go(0); };
  bPrev.onclick = () => { stop(); go(i - 1); };
  bNext.onclick = () => { stop(); go(i + 1); };
  bLast.onclick = () => { stop(); go(N - 1); };
  bPlay.onclick = play;
  range.oninput = () => { stop(); go(Number(range.value)); };
  card.addEventListener('keydown', e => {
    if (e.key === 'ArrowRight') { e.preventDefault(); stop(); go(i + 1); }
    else if (e.key === 'ArrowLeft') { e.preventDefault(); stop(); go(i - 1); }
    else if (e.key === 'Home') { e.preventDefault(); stop(); go(0); }
    else if (e.key === 'End') { e.preventDefault(); stop(); go(N - 1); }
    else if (e.key === ' ') { e.preventDefault(); play(); }
  });
  window.addEventListener('langchange', () => { paintText(); renderers.forEach(r => r(i)); });
  card.simGo = go;
  go(0);
}

// ── 시작 ─────────────────────────────────────────────────────────
(function main() {
  injectCSS();
  let data = [];
  try { data = JSON.parse(document.getElementById('sim-data').textContent); } catch { data = []; }
  const byId = Object.fromEntries(data.map(s => [s.id, s]));
  document.querySelectorAll('.sim[data-sim]').forEach(card => mount(card, byId[card.dataset.sim]));
})();
```

- [ ] **Step 5: 확인 스크립트를 돌린다**

Run: `node .gstack/tmp/simstep.mjs .gstack/tmp/simfix.html`
Expected: `[OK] fix-ff: 6 프레임 · 코드 강조 000000 · 엣지 표시 000000`, `[OK] 영어 모드 해설`, `[OK] 콘솔 에러 없음`, exit 0. (코드 강조와 엣지 표시가 전부 0 인 것은 아직 그 렌더러가 없어서다.)

- [ ] **Step 6: 눈으로 본다**

Run: `node scripts/verify.mjs .gstack/tmp/simfix.html` 는 아직 `.sim` 을 모른다 (Task 5). 대신 `node scripts/serve.mjs` 로 띄우고 `http://127.0.0.1:4599/.gstack/tmp/simfix.html` 을 브라우저로 열어 시크바 · 재생 · ← → · 언어 토글이 도는지, 파형 커서가 따라오는지 본다. (`.gstack/` 이 서버에서 안 보이면 페이지를 `notes/` 에 잠깐 복사해서 본다.)

- [ ] **Step 7: 커밋**

```bash
git add sim.js .gstack/tmp/simfix.html .gstack/tmp/mkfix.py .gstack/tmp/simstep.mjs
git commit -m "Add sim.js: half-clock frame viewer with seekbar and generated waveform"
```

`.gstack/` 이 gitignore 대상이면 `sim.js` 만 커밋된다. 그래도 된다. 고정 페이지와 확인 스크립트는 로컬 도구다.

---

### Task 3: `sim.js` 회로 렌더러

**Files:**
- Modify: `sim.js` (파형 렌더러 아래에 `renderCircuit` 추가)
- Modify: `.gstack/tmp/simstep.mjs` (엣지 표시와 배선 클래스 확인 추가)

**Interfaces:**
- Consumes: `sc.circuit = { w, h, nodes[], ports[], wires[] }`. 노드 `{ id, kind, x, y, in:{핀:신호}, out:{핀:신호}, val?, late? }`. 포트 `{ sig, side:'in'|'out', y }`. 배선 `{ sig, pts:[[x,y],…] }`.
- Produces: `renderCircuit(sc, host) → (i) => void`. DOM: `.sim-circ svg` 안에 `g.node[data-id]` (kind 별 클래스 `node ff`, `node latch`, …), `path.wire[data-sig]` (값에 따라 클래스 `w0` `w1` `wx`, 클럭이면 `wc0` `wc1`, 이번 프레임에 바뀌었으면 `chg`), `g.badge[data-sig]` (값 글자). 엣지 프레임(짝수, 0 제외)에 `ff` 노드는 클래스 `edge`, `en=1` 인 `latch` 는 `open`, 출력이 `X`/`M` 이면 `bad`.
- 핀 좌표 (배선을 적을 때 이 자리에 맞춘다):

| kind | 크기 | 입력 핀 | 출력 핀 |
|---|---|---|---|
| `ff` | 56×44 | `d` (x, y+16) · `clk` (x, y+34) · `rst_n`/`arst_n` (x+28, y+44) | `q` (x+56, y+16) |
| `latch` | 56×44 | `d` (x, y+16) · `en` (x, y+34) | `q` (x+56, y+16) |
| `and` `or` `xor` `add` | 48×40 | `a` (x, y+12) · `b` (x, y+28) | `y` (x+48, y+20) |
| `mux` | 48×40 | `a` (x, y+12) · `b` (x, y+28) · `sel` (x+24, y+40) | `y` (x+48, y+20) |
| `not` `buf` `delay` | 40×28 | `a` (x, y+14) | `y` (x+40, y+14) |
| `const` | 32×24 | 없음 | `y` (x+32, y+12) |

포트는 `side:'in'` 이면 x=8 에 이름, 배선은 x=36 에서 시작. `side:'out'` 이면 배선이 x=w-36 에서 끝나고 이름은 x=w-8.

- [ ] **Step 1: 확인 스크립트에 검사를 더한다**

`.gstack/tmp/simstep.mjs` 의 `okNotes` 줄 아래에 추가:

```js
  // 회로: 엣지 프레임(2, 4, …)에 ff 가 edge 표시를 받고, q 배선이 값 1 일 때 w1 클래스를 갖는다
  const hasFF = await c.evaluate(el => !!el.querySelector('.sim-circ .node.ff'));
  const okEdge = !hasFF || seen.every((s, i) => (i > 0 && i % 2 === 0) ? s.edgeNodes > 0 : s.edgeNodes === 0);
  const wireCls = await c.evaluate(el => { el.simGo(2); const w = el.querySelector('.sim-circ .wire[data-sig="q"]'); return w ? w.getAttribute('class') : ''; });
  const okWire = !hasFF || /\bw1\b/.test(wireCls);
  if (!okEdge) console.log(`   · 엣지 표시가 프레임과 안 맞는다: ${seen.map(s => s.edgeNodes).join('')}`);
  if (!okWire) console.log(`   · q 배선 클래스: "${wireCls}" (w1 이어야 한다)`);
```

그리고 `const okFrames` 판정을 `okFrames && okNotes && okEdge && okWire` 로 바꾼다 (두 군데).

- [ ] **Step 2: 실행해서 실패를 확인한다**

Run: `node .gstack/tmp/simstep.mjs .gstack/tmp/simfix.html`
Expected: `[FAIL] fix-ff` 와 `· 엣지 표시가 프레임과 안 맞는다: 000000` 아니면 `q 배선 클래스: ""`. (hasFF 가 false 라 통과할 수도 있다. 그러면 Step 3 뒤 다시 돌렸을 때 `edgeNodes` 가 `001010` 로 나오는지로 확인한다.)

- [ ] **Step 3: 렌더러를 쓴다**

`sim.js` 의 `// ── 카드` 블록 **위에** 추가. CSS 도 `CSS` 문자열 끝에 더한다.

```js
// ── 회로 ─────────────────────────────────────────────────────────
// 초보자용이라 IEEE 기호 대신 이름 붙은 상자를 쓴다. 배선은 값에 따라
// 굵기가 달라지고, 이번 프레임에 바뀐 배선은 빛난다.
const GEOM = {
  ff:    { w: 56, h: 44, pins: { d: [0, 16], clk: [0, 34], rst_n: [28, 44], arst_n: [28, 44], q: [56, 16] } },
  latch: { w: 56, h: 44, pins: { d: [0, 16], en: [0, 34], q: [56, 16] } },
  and:   { w: 48, h: 40, pins: { a: [0, 12], b: [0, 28], y: [48, 20] }, label: 'AND' },
  or:    { w: 48, h: 40, pins: { a: [0, 12], b: [0, 28], y: [48, 20] }, label: 'OR' },
  xor:   { w: 48, h: 40, pins: { a: [0, 12], b: [0, 28], y: [48, 20] }, label: 'XOR' },
  add:   { w: 48, h: 40, pins: { a: [0, 12], b: [0, 28], y: [48, 20] }, label: '+' },
  mux:   { w: 48, h: 40, pins: { a: [0, 12], b: [0, 28], sel: [24, 40], y: [48, 20] }, label: 'MUX' },
  not:   { w: 40, h: 28, pins: { a: [0, 14], y: [40, 14] }, label: 'NOT' },
  buf:   { w: 40, h: 28, pins: { a: [0, 14], y: [40, 14] }, label: '' },
  delay: { w: 40, h: 28, pins: { a: [0, 14], y: [40, 14] }, label: 'delay' },
  const: { w: 32, h: 24, pins: { y: [32, 12] } },
};

function renderCircuit(sc, host) {
  const C = sc.circuit;
  const svg = svgEl('svg', { viewBox: `0 0 ${C.w} ${C.h}`, role: 'img',
    'aria-label': L('회로도. 프레임에 따라 배선 값이 바뀐다', 'circuit diagram; wire values follow the frame') });
  host.replaceChildren(svg);
  const clkSigs = new Set(sc.signals.filter(s => s.kind === 'clk').map(s => s.n));

  // 배선을 먼저 깔고 상자를 그 위에 올린다
  const wires = (C.wires || []).map(w => {
    const p = svgEl('path', { class: 'wire', 'data-sig': w.sig, d: w.pts.map((q, k) => (k ? 'L' : 'M') + q[0] + ' ' + q[1]).join(' ') });
    svg.appendChild(p);
    return { el: p, sig: w.sig };
  });

  const nodes = (C.nodes || []).map(n => {
    const g = GEOM[n.kind];
    const grp = svgEl('g', { class: 'node ' + n.kind, 'data-id': n.id, transform: `translate(${n.x} ${n.y})` });
    grp.appendChild(svgEl('rect', { width: g.w, height: g.h, rx: 6 }));
    if (n.kind === 'ff' || n.kind === 'latch') {
      grp.appendChild(svgEl('text', { x: 7, y: 20 }, 'D'));
      grp.appendChild(svgEl('text', { x: g.w - 7, y: 20, 'text-anchor': 'end' }, 'Q'));
      if (n.kind === 'ff') grp.appendChild(svgEl('path', { d: 'M0 28 L8 34 L0 40', class: 'clkmark' }));
      else grp.appendChild(svgEl('text', { x: 7, y: 38, class: 'small' }, 'EN'));
      if (n.in && (n.in.rst_n || n.in.arst_n)) grp.appendChild(svgEl('text', { x: g.w / 2, y: g.h - 4, 'text-anchor': 'middle', class: 'small' }, n.in.arst_n ? 'ARST' : 'RST'));
    } else if (n.kind === 'const') {
      grp.appendChild(svgEl('text', { x: g.w / 2, y: g.h / 2 + 4, 'text-anchor': 'middle' }, String(n.val)));
    } else if (g.label) {
      grp.appendChild(svgEl('text', { x: g.w / 2, y: g.h / 2 + 4, 'text-anchor': 'middle' }, g.label));
    }
    if (n.kind === 'buf') grp.appendChild(svgEl('path', { d: `M4 4 L${g.w - 4} ${g.h / 2} L4 ${g.h - 4} Z`, class: 'bufmark' }));
    svg.appendChild(grp);
    return { el: grp, n };
  });

  // 포트 이름
  (C.ports || []).forEach(p => {
    const x = p.side === 'in' ? 8 : C.w - 8;
    svg.appendChild(svgEl('text', { x, y: p.y + 4, 'text-anchor': p.side === 'in' ? 'start' : 'end',
      class: 'port' + (clkSigs.has(p.sig) ? ' clk' : '') }, p.sig));
  });

  // 값 배지: 신호마다 첫 배선의 시작점 위
  const badges = {};
  wires.forEach(w => {
    if (badges[w.sig]) return;
    const pts = (C.wires.find(x => x.sig === w.sig) || {}).pts;
    const [x, y] = pts[0];
    const g = svgEl('g', { class: 'badge', 'data-sig': w.sig, transform: `translate(${x + 4} ${y - 14})` });
    g.appendChild(svgEl('rect', { width: 18, height: 12, rx: 3 }));
    g.appendChild(svgEl('text', { x: 9, y: 9, 'text-anchor': 'middle' }));
    svg.appendChild(g);
    badges[w.sig] = g;
  });

  return i => {
    const v = sc.frames[i].v;
    wires.forEach(w => {
      const val = v[w.sig], clk = clkSigs.has(w.sig);
      let cls = 'wire';
      if (isXM(val)) cls += ' wx';
      else if (clk) cls += val ? ' wc1' : ' wc0';
      else cls += val ? ' w1' : ' w0';
      if (changed(sc, i, w.sig)) cls += ' chg';
      w.el.setAttribute('class', cls);
    });
    for (const sig in badges) {
      const val = v[sig];
      badges[sig].querySelector('text').textContent = String(val);
      badges[sig].setAttribute('class', 'badge' + (isXM(val) ? ' bad' : ''));
    }
    nodes.forEach(({ el, n }) => {
      let cls = 'node ' + n.kind;
      const out = n.out && (n.out.q || n.out.y);
      if (n.kind === 'ff' && i > 0 && i % 2 === 0) cls += ' edge';
      if (n.kind === 'latch' && n.in && v[n.in.en] === 1) cls += ' open';
      if (out && isXM(v[out])) cls += ' bad';
      el.setAttribute('class', cls);
    });
  };
}
```

`CSS` 문자열 끝에 붙일 규칙:

```css
.sim .wire{fill:none;stroke-linejoin:round;transition:stroke-width .15s}
.sim .wire.w0{stroke:var(--blue);stroke-width:1.4;opacity:.45}
.sim .wire.w1{stroke:var(--blue);stroke-width:2.6}
.sim .wire.wx{stroke:var(--amber);stroke-width:2.4;stroke-dasharray:4 3}
.sim .wire.wc0{stroke:var(--brown);stroke-width:1.3;opacity:.5}
.sim .wire.wc1{stroke:var(--brown);stroke-width:2.2}
.sim .wire.chg{filter:drop-shadow(0 0 3px rgba(var(--blue-rgb),.7))}
.sim .wire.wx.chg{filter:drop-shadow(0 0 3px rgba(var(--amber-rgb),.8))}
.sim .node rect{fill:rgba(var(--blue-rgb),.12);stroke:var(--blue);stroke-width:1.6}
.sim .node.edge rect{fill:rgba(var(--green-rgb),.3);stroke:var(--green)}
.sim .node.open rect{fill:rgba(var(--amber-rgb),.22);stroke:var(--amber)}
.sim .node.bad rect{stroke:var(--amber);stroke-dasharray:4 3}
.sim .node text{font-family:var(--mono);font-size:10.5px;font-weight:700;fill:var(--ink)}
.sim .node text.small{font-size:8px;font-weight:400;fill:var(--ink2)}
.sim .node .clkmark{fill:none;stroke:var(--brown);stroke-width:1.6}
.sim .node .bufmark{fill:none;stroke:var(--blue);stroke-width:1.4}
.sim .port{font-family:var(--mono);font-size:10.5px;fill:var(--blue)}
.sim .port.clk{fill:var(--brown)}
.sim .badge rect{fill:var(--card);stroke:var(--rule);stroke-width:1}
.sim .badge text{font-family:var(--mono);font-size:9.5px;font-weight:700;fill:var(--ink)}
.sim .badge.bad text{fill:var(--amber)}
```

- [ ] **Step 4: 확인**

Run: `node .gstack/tmp/simstep.mjs .gstack/tmp/simfix.html`
Expected: `[OK] fix-ff: 6 프레임 · 코드 강조 000000 · 엣지 표시 001010`, 콘솔 에러 없음, exit 0.

- [ ] **Step 5: 눈으로 본다**

`node scripts/serve.mjs` 로 열어 flop 상자가 엣지 프레임에 초록으로 바뀌고, d 배선이 값 1 일 때 굵어지고, clk 배선이 갈색인지 본다. 배지 글자가 상자나 배선 위에 겹치면 시나리오의 `pts[0]` 를 옮긴다 (배지는 첫 점의 왼쪽 위에 붙는다).

- [ ] **Step 6: 커밋**

```bash
git add sim.js
git commit -m "sim.js: circuit renderer with value-driven wires and edge/open node states"
```

---

### Task 4: `sim.js` 코드 렌더러

**Files:**
- Modify: `sim.js` (`renderCode` 추가)

**Interfaces:**
- Consumes: `sc.code = [{ t, drives?: string[] }]`.
- Produces: `renderCode(sc, host) → (i) => void`. DOM: `.sim-code pre.code > span.ln[data-drives]`. 이번 프레임에 값이 바뀐 신호를 모는 줄은 클래스 `hot`. 키워드는 `span.k`, `//` 주석은 `span.c`, 숫자 리터럴은 `span.n`.

- [ ] **Step 1: 확인 스크립트에 검사를 더한다**

`.gstack/tmp/simstep.mjs` 의 `okWire` 아래:

```js
  // 코드: q 를 모는 줄은 q 가 바뀐 프레임(2, 4)에만 hot 이다
  const okCode = !hasFF || (seen[2].hotLines > 0 && seen[1].hotLines === 0);
  if (!okCode) console.log(`   · 코드 강조: ${seen.map(s => s.hotLines).join('')} (프레임 2 에 있고 1 에 없어야 한다)`);
```

판정에 `&& okCode` 를 더한다.

- [ ] **Step 2: 실행해서 실패를 확인한다**

Run: `node .gstack/tmp/simstep.mjs .gstack/tmp/simfix.html`
Expected: `[FAIL] fix-ff` 와 `· 코드 강조: 000000`.

- [ ] **Step 3: 렌더러를 쓴다**

`renderCircuit` 아래에 추가.

```js
// ── 코드 ─────────────────────────────────────────────────────────
// 하이라이팅은 손으로 하는 게 규칙이지만 여기는 줄이 데이터로 오므로
// 키워드 · 주석 · 숫자 세 가지만 정규식으로 칠한다. 색은 pre.code 의 .k .c .n 이 맡는다.
const KW = /\b(always_ff|always_comb|always_latch|always|posedge|negedge|if|else|begin|end|module|endmodule|input|output|logic|assign|case|endcase|default)\b/g;
const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

function hl(t) {
  const c = t.indexOf('//');
  let code = c >= 0 ? t.slice(0, c) : t, cm = c >= 0 ? t.slice(c) : '';
  code = esc(code).replace(KW, '<span class="k">$1</span>').replace(/\b(\d+'[bdh][0-9a-fA-F_]+|\d+)\b/g, '<span class="n">$1</span>');
  return code + (cm ? '<span class="c">' + esc(cm) + '</span>' : '');
}

function renderCode(sc, host) {
  const pre = el('pre', { class: 'code' });
  host.replaceChildren(pre);
  const lines = (sc.code || []).map(l => {
    const s = el('span', { class: 'ln', 'data-drives': (l.drives || []).join(',') });
    s.innerHTML = hl(l.t) || ' ';
    pre.appendChild(s);
    return { el: s, drives: l.drives || [] };
  });
  return i => lines.forEach(l => {
    const hot = l.drives.some(sig => changed(sc, i, sig));
    l.el.setAttribute('class', 'ln' + (hot ? ' hot' : ''));
  });
}
```

- [ ] **Step 4: 확인**

Run: `node .gstack/tmp/simstep.mjs .gstack/tmp/simfix.html`
Expected: `[OK] fix-ff: 6 프레임 · 코드 강조 001010 · 엣지 표시 001010`, exit 0.

- [ ] **Step 5: 커밋**

```bash
git add sim.js
git commit -m "sim.js: code panel that lights the line driving whichever signal just changed"
```

---

### Task 5: `verify.mjs` 가 `.sim` 을 보게 한다

**Files:**
- Modify: `scripts/verify.mjs:287`, `scripts/verify.mjs:393`, `scripts/verify.mjs:579`

- [ ] **Step 1: 세 줄을 고친다**

287줄: `const figs = await page.$$('figure, .play');` → `const figs = await page.$$('figure, .play, .sim');`
393줄: `document.querySelectorAll('figure svg, .play svg, .nota svg')` → `document.querySelectorAll('figure svg, .play svg, .nota svg, .sim svg')`
579줄: `'도해 스크린샷: 없음 (figure / .play 요소가 없는 파일)\n'` → `'도해 스크린샷: 없음 (figure / .play / .sim 요소가 없는 파일)\n'`

- [ ] **Step 2: 고정 페이지로 확인한다**

고정 페이지를 `notes/` 아래로 잠깐 복사해서 돌린다 (`verify.mjs` 가 `notes/` 기준으로 경로를 잡는다면). `sim.js` 경로가 `../../sim.js` 라 `notes/` 에서는 `../sim.js` 로 바꿔야 한다.

```bash
sed 's#\.\./\.\./sim\.js#../sim.js#' .gstack/tmp/simfix.html > notes/_simfix.html
node scripts/verify.mjs notes/_simfix.html
```

Expected: `도해 스크린샷: shots/_simfix-fig01.png … (1장)`, `[OK] 도해 글자끼리 겹치지 않음`, `[OK] 하드코딩된 색 없음`. `shots/_simfix-fig01.png` 를 열어 카드 전체가 찍혔는지 본다.

```bash
rm notes/_simfix.html
```

- [ ] **Step 3: 커밋**

```bash
git add scripts/verify.mjs
git commit -m "verify: screenshot and overlap-check .sim cards like figures"
```

---

### Task 6: P03 시나리오 일곱 개와 페이지 빌더 골격

**Files:**
- Create: `.gstack/tmp/pbuild.py` (P 페이지 공용 빌더)
- Create: `.gstack/tmp/p03_scen.py` (시나리오 데이터)
- Create: `.gstack/tmp/p03.py` (본문. 이 Task 에서는 골격만)
- Output: `notes/P03-before-lecture-3.html`

**Interfaces:**
- Produces: `pbuild.build(dst, lec, title, sub_ko, sub_en, chips_ko, chips_en, toc, sections, scenarios)` 가 페이지를 쓴다. `toc = [(id, ko, en)]`, `sections = {id: html}`, `scenarios = [dict]`. 페이지에는 `<script type="application/json" id="sim-data">` 와 `<script src="../sim.js" type="module">` 이 들어가고 `reader.js` 는 없다.
- 시나리오 id (Task 7 본문이 `<div class="sim" data-sim="…">` 로 부른다): `p03-xor`, `p03-ff`, `p03-three`, `p03-counter`, `p03-swap-nb`, `p03-swap-b`, `p03-latch-noelse`, `p03-latch-else`.

- [ ] **Step 1: 공용 빌더**

`.gstack/tmp/pbuild.py`:

```python
# -*- coding: utf-8 -*-
"""P 페이지 빌더. 스타일과 꼬리는 L01 에서 빌리고, reader.js 대신 sim.js 를 넣는다."""
import io, json, re, sys
sys.path.insert(0, ".gstack/tmp")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from mk import load, strip_tool_js

SRC = "notes/L01-course-intro.html"


def build(dst, lec, title, sub_ko, sub_en, chips_ko, chips_en, toc, sections, scenarios, foot_lec):
    head, tail, _ = load(SRC)
    head = re.sub(r"<title>[^<]*</title>", f"<title>{lec} · {title} · CEN 598 ADDV</title>", head, count=1)
    tail = strip_tool_js(tail)
    tail = tail.replace('<script src="../reader.js" type="module"></script>\n', "")
    tail = tail.replace("Lecture 1 개인 학습 노트", f"{foot_lec} 개인 학습 노트")
    tail = tail.replace("Lecture 1 personal study notes", f"{foot_lec} personal study notes")
    for old in ("Lecture 1 개인", "Lecture 1 personal"):
        assert old not in tail, old

    data = ('<script type="application/json" id="sim-data">'
            + json.dumps(scenarios, ensure_ascii=False) + "</script>\n"
            + '<script src="../sim.js" type="module"></script>\n')
    mark = '<button class="lang-btn"'
    assert mark in tail
    tail = tail.replace(mark, data + mark, 1)

    chips = lambda cs: "\n".join(f'    <span class="chip{" " + c[1] if len(c) > 1 else ""}">{c[0]}</span>' for c in cs)
    header = f'''<header class="top">
  <div class="eyebrow">CEN 598 &middot; Advanced Digital Design and Verification &middot; 실습 입문</div>
  <h1 class="title">{lec}<br>{title}</h1>
  <p class="subtitle" lang="ko">{sub_ko}</p>
  <p class="subtitle" lang="en">{sub_en}</p>
  <div class="meta" lang="ko">
{chips(chips_ko)}
  </div>
  <div class="meta" lang="en">
{chips(chips_en)}
  </div>
  <a class="backlink" href="../index.html" lang="ko">&larr; 강의 목록으로</a>
  <a class="backlink" href="../index.html" lang="en">&larr; All lectures</a>
</header>
'''
    rows = "\n".join(f'  <a href="#{i}"><span class="n">{k:02d}</span><span lang="ko">{ko}</span><span lang="en">{en}</span></a>'
                     for k, (i, ko, en) in enumerate(toc, 1))
    nav = f'''<nav class="toc">
  <div class="mini-head">
    <a class="back" href="../index.html" lang="ko">&larr; 강의 목록</a>
    <a class="back" href="../index.html" lang="en">&larr; All lectures</a>
    <div class="mod">{lec}</div>
    <div class="name">{title}</div>
    <div class="rule"></div>
  </div>
  <div class="lab" lang="ko">목차</div>
  <div class="lab" lang="en">Contents</div>
{rows}
</nav>
'''
    body = []
    for k, (i, ko, en) in enumerate(toc, 1):
        body.append(f'<section id="{i}">\n  <div class="sec-head"><span class="sec-num">{k:02d}</span>'
                    f'<h2 lang="ko">{ko}</h2><h2 lang="en">{en}</h2></div>\n{sections[i]}\n</section>\n')
    out = head + header + nav + "\n<main>\n" + "\n".join(body) + "\n" + tail
    io.open(dst, "w", encoding="utf-8").write(out)
    print(f"wrote {dst}  {len(out)} chars  (시뮬레이션 {len(scenarios)})")
```

`mk.load` 가 주는 `head` 는 `<div class="wrap">` 까지이고 `tail` 은 `<footer>` 부터다. 그래서 `<main>` 을 여기서 열고 `tail` 이 닫는다. (Task 2 의 고정 페이지와 달리 `footer` 가 `main` 안에 있는 원본 구조를 그대로 따른다.)

- [ ] **Step 2: 시나리오 데이터**

`.gstack/tmp/p03_scen.py`. 프레임 해설은 여기서 같이 쓴다. 값과 좌표는 Task 1 의 노드 의미와 Task 3 의 핀 표에 맞춘다.

```python
# -*- coding: utf-8 -*-
"""P03 시나리오. 프레임 2k 는 엣지 직후(clk=1), 2k+1 은 정착(clk=0). 입력은 정착 프레임에서만 바뀐다."""


def F(v, ko, en):
    return {"v": v, "note": {"ko": ko, "en": en}}


XOR = {
    "id": "p03-xor",
    "title": {"ko": "조합 논리 하나. y = a ^ b", "en": "One piece of combinational logic: y = a ^ b"},
    "code": [{"t": "assign y = a ^ b;", "drives": ["y"]}],
    "circuit": {"w": 320, "h": 120,
        "nodes": [{"id": "x1", "kind": "xor", "x": 140, "y": 36, "in": {"a": "a", "b": "b"}, "out": {"y": "y"}}],
        "ports": [{"sig": "a", "side": "in", "y": 40}, {"sig": "b", "side": "in", "y": 72}, {"sig": "y", "side": "out", "y": 56}],
        "wires": [{"sig": "a", "pts": [[36, 40], [100, 40], [100, 48], [140, 48]]},
                  {"sig": "b", "pts": [[36, 72], [100, 72], [100, 64], [140, 64]]},
                  {"sig": "y", "pts": [[188, 56], [284, 56]]}]},
    "signals": [{"n": "clk", "kind": "clk"}, {"n": "a"}, {"n": "b"}, {"n": "y"}],
    "frames": [
        F({"clk": 1, "a": 0, "b": 0, "y": 0}, "a 도 b 도 0. y 는 0. 여기서 a 와 b 를 '동시에' 1 로 바꿀 참이다.", "Both a and b are 0, so y is 0. We are about to set a and b to 1 'at the same time'."),
        F({"clk": 0, "a": 1, "b": 0, "y": 1}, "a 가 먼저 도착했다. b 는 아직이다. 그 사이 y 는 1 이다. 우리가 원한 값이 아니다.", "a arrived first; b has not yet. In between, y is 1, which nobody wanted."),
        F({"clk": 1, "a": 1, "b": 0, "y": 1}, "여전히 y 는 1. 이 틀린 값이 한 클럭 가까이 살아 있다.", "y is still 1. The wrong value has lived nearly a whole clock."),
        F({"clk": 0, "a": 1, "b": 1, "y": 0}, "b 가 도착했다. 이제야 y 가 0 으로 돌아온다.", "b arrives. Only now does y return to 0."),
        F({"clk": 1, "a": 1, "b": 1, "y": 0}, "둘 다 1, y 는 0. 원하던 상태다. 그런데 도중에 1 이 한 번 지나갔다.", "Both 1, y is 0: what we wanted. But a 1 passed through on the way."),
        F({"clk": 0, "a": 0, "b": 1, "y": 1}, "내릴 때도 같은 일이 난다. a 가 먼저 내려가서 y 가 또 1 이다.", "The same thing happens on the way down. a drops first and y is 1 again."),
        F({"clk": 1, "a": 0, "b": 1, "y": 1}, "회로에는 '동시' 가 없다. 배선 길이가 다르면 도착 시각이 다르다.", "There is no 'simultaneous' in a circuit. Different wire lengths mean different arrival times."),
        F({"clk": 0, "a": 0, "b": 0, "y": 0}, "그래서 '언제 읽을지' 를 정하는 신호가 필요하다. 그게 clk 이고, 다음 단원부터 쓴다.", "So we need a signal that says when to read. That is clk, and the next unit starts using it."),
    ],
}

FF = {
    "id": "p03-ff",
    "title": {"ko": "flip-flop. q <= d", "en": "A flip-flop: q <= d"},
    "code": [{"t": "always_ff @(posedge clk)"}, {"t": "  q <= d;", "drives": ["q"]}],
    "circuit": {"w": 320, "h": 120,
        "nodes": [{"id": "f1", "kind": "ff", "x": 140, "y": 40, "in": {"d": "d", "clk": "clk"}, "out": {"q": "q"}}],
        "ports": [{"sig": "d", "side": "in", "y": 56}, {"sig": "q", "side": "out", "y": 56}, {"sig": "clk", "side": "in", "y": 96}],
        "wires": [{"sig": "d", "pts": [[36, 56], [140, 56]]},
                  {"sig": "q", "pts": [[196, 56], [284, 56]]},
                  {"sig": "clk", "pts": [[36, 96], [120, 96], [120, 74], [140, 74]]}]},
    "signals": [{"n": "clk", "kind": "clk"}, {"n": "d"}, {"n": "q"}],
    "frames": [
        F({"clk": 1, "d": 0, "q": 0}, "리셋 직후. d 도 q 도 0.", "Just after reset. d and q are both 0."),
        F({"clk": 0, "d": 1, "q": 0}, "d 가 1 로 올라갔다. q 는 아직 0 이다. flop 은 엣지가 아니면 안 듣는다.", "d rises to 1. q is still 0. A flop does not listen except at an edge."),
        F({"clk": 1, "d": 1, "q": 1}, "엣지. 이 순간 flop 이 d 를 본다. 1 이었으니 q 가 1 이 된다. 상자가 초록으로 깜빡인 것이 '잡았다' 는 표시다.", "Edge. This instant the flop looks at d. It was 1, so q becomes 1. The green flash means 'captured'."),
        F({"clk": 0, "d": 0, "q": 1}, "d 가 0 으로 내려갔다. q 는 1 그대로다. 다음 엣지까지 아무 일도 없다.", "d falls to 0. q stays 1. Nothing happens until the next edge."),
        F({"clk": 1, "d": 0, "q": 0}, "엣지. d 가 0 이었으니 q 도 0.", "Edge. d was 0, so q is 0."),
        F({"clk": 0, "d": 1, "q": 0}, "d 가 다시 1. q 는 기다린다.", "d is 1 again. q waits."),
        F({"clk": 1, "d": 1, "q": 1}, "엣지. q 가 1.", "Edge. q is 1."),
        F({"clk": 0, "d": 1, "q": 1}, "d 가 안 바뀌었다. 엣지가 와도 q 는 같은 값을 다시 잡을 뿐이다.", "d did not change. The next edge will just capture the same value."),
        F({"clk": 1, "d": 1, "q": 1}, "엣지. 값은 그대로 1.", "Edge. Still 1."),
        F({"clk": 0, "d": 0, "q": 1}, "q 는 항상 d 보다 반 클럭에서 한 클럭 늦다. 그게 버그가 아니라 flop 의 정의다.", "q always trails d by half a clock to one clock. That is not a bug; it is what a flop is."),
    ],
}

THREE = {
    "id": "p03-three",
    "title": {"ko": "같은 d, 세 가지 출력", "en": "One d, three outputs"},
    "code": [{"t": "assign y = d;                    // 조합 논리", "drives": ["y"]},
             {"t": "always_ff @(posedge clk)"},
             {"t": "  q_ff <= d;                     // flip-flop", "drives": ["q_ff"]},
             {"t": "always_latch"},
             {"t": "  if (en) q_lat <= d;            // latch", "drives": ["q_lat"]}],
    "circuit": {"w": 360, "h": 200,
        "nodes": [{"id": "b1", "kind": "buf", "x": 150, "y": 26, "in": {"a": "d"}, "out": {"y": "y"}},
                  {"id": "f1", "kind": "ff", "x": 150, "y": 84, "in": {"d": "d", "clk": "clk"}, "out": {"q": "q_ff"}},
                  {"id": "l1", "kind": "latch", "x": 150, "y": 144, "in": {"d": "d", "en": "en"}, "out": {"q": "q_lat"}}],
        "ports": [{"sig": "d", "side": "in", "y": 40}, {"sig": "clk", "side": "in", "y": 118}, {"sig": "en", "side": "in", "y": 178},
                  {"sig": "y", "side": "out", "y": 40}, {"sig": "q_ff", "side": "out", "y": 100}, {"sig": "q_lat", "side": "out", "y": 160}],
        "wires": [{"sig": "d", "pts": [[36, 40], [150, 40]]},
                  {"sig": "d", "pts": [[100, 40], [100, 100], [150, 100]]},
                  {"sig": "d", "pts": [[100, 100], [100, 160], [150, 160]]},
                  {"sig": "clk", "pts": [[36, 118], [150, 118]]},
                  {"sig": "en", "pts": [[36, 178], [150, 178]]},
                  {"sig": "y", "pts": [[190, 40], [324, 40]]},
                  {"sig": "q_ff", "pts": [[206, 100], [324, 100]]},
                  {"sig": "q_lat", "pts": [[206, 160], [324, 160]]}]},
    "signals": [{"n": "clk", "kind": "clk"}, {"n": "en"}, {"n": "d"}, {"n": "y"}, {"n": "q_ff"}, {"n": "q_lat"}],
    "frames": [
        F({"clk": 1, "en": 0, "d": 0, "y": 0, "q_ff": 0, "q_lat": 0}, "전부 0. latch 의 en 은 닫혀 있다.", "All 0. The latch's en is closed."),
        F({"clk": 0, "en": 1, "d": 1, "y": 1, "q_ff": 0, "q_lat": 1}, "en 이 열리고 d 가 1 이 됐다. y 는 즉시 1. q_lat 도 즉시 1 (문이 열려 있으니 그대로 흘린다). q_ff 만 기다린다.", "en opens and d goes to 1. y is 1 at once. q_lat is 1 at once too, the door is open and it passes d through. Only q_ff waits."),
        F({"clk": 1, "en": 1, "d": 1, "y": 1, "q_ff": 1, "q_lat": 1}, "엣지. 이제 q_ff 도 1. 셋이 같아 보이지만 도달한 시점이 달랐다.", "Edge. Now q_ff is 1 too. All three look equal, but they got there at different times."),
        F({"clk": 0, "en": 1, "d": 0, "y": 0, "q_ff": 1, "q_lat": 0}, "d 가 0 으로. y 즉시 0. q_lat 도 즉시 0 (문이 아직 열려 있다). q_ff 는 1 을 붙들고 있다.", "d drops. y is 0 at once. q_lat is 0 at once (the door is still open). q_ff holds its 1."),
        F({"clk": 1, "en": 1, "d": 0, "y": 0, "q_ff": 0, "q_lat": 0}, "엣지. q_ff 가 0 을 잡는다.", "Edge. q_ff captures 0."),
        F({"clk": 0, "en": 0, "d": 1, "y": 1, "q_ff": 0, "q_lat": 0}, "en 이 닫히고 d 가 1 로. y 는 1. q_lat 은 0 에 멈춘다. 문이 닫혔으니 마지막 값을 기억한다. 이게 latch 다.", "en closes and d rises. y is 1. q_lat stays at 0: the door is shut, so it remembers the last value. That is a latch."),
        F({"clk": 1, "en": 0, "d": 1, "y": 1, "q_ff": 1, "q_lat": 0}, "엣지. q_ff 는 1 을 잡았다. q_lat 은 여전히 0. flop 은 엣지를 듣고 latch 는 en 을 듣는다.", "Edge. q_ff captures 1. q_lat is still 0. A flop listens to the edge; a latch listens to en."),
        F({"clk": 0, "en": 0, "d": 0, "y": 0, "q_ff": 1, "q_lat": 0}, "d 가 0. y 즉시 0. 나머지 둘은 기억한 값을 지킨다.", "d is 0. y is 0 at once. The other two keep what they remember."),
        F({"clk": 1, "en": 0, "d": 0, "y": 0, "q_ff": 0, "q_lat": 0}, "엣지. q_ff 가 0.", "Edge. q_ff is 0."),
        F({"clk": 0, "en": 1, "d": 0, "y": 0, "q_ff": 0, "q_lat": 0}, "en 이 다시 열린다. d 가 0 이라 q_lat 도 0. 세 줄이 같은 회로였던 적은 한 번도 없다.", "en opens again. d is 0, so q_lat is 0. At no point were the three lines the same circuit."),
    ],
}

COUNTER = {
    "id": "p03-counter",
    "title": {"ko": "2 비트 카운터", "en": "A 2-bit counter"},
    "code": [{"t": "logic [1:0] q;"},
             {"t": "always_ff @(posedge clk)"},
             {"t": "  if (!rst_n) q <= 2'd0;", "drives": ["q"]},
             {"t": "  else        q <= q + 2'd1;", "drives": ["q"]}],
    "circuit": {"w": 360, "h": 150,
        "nodes": [{"id": "c1", "kind": "const", "x": 60, "y": 96, "val": 1, "out": {"y": "one"}},
                  {"id": "a1", "kind": "add", "x": 130, "y": 56, "in": {"a": "q", "b": "one"}, "out": {"y": "q_next"}},
                  {"id": "f1", "kind": "ff", "x": 230, "y": 60, "in": {"d": "q_next", "clk": "clk", "rst_n": "rst_n"}, "out": {"q": "q"}}],
        "ports": [{"sig": "clk", "side": "in", "y": 94}, {"sig": "rst_n", "side": "in", "y": 130}, {"sig": "q", "side": "out", "y": 76}],
        "wires": [{"sig": "q", "pts": [[286, 76], [324, 76]]},
                  {"sig": "q", "pts": [[300, 76], [300, 20], [110, 20], [110, 68], [130, 68]]},
                  {"sig": "one", "pts": [[92, 108], [110, 108], [110, 84], [130, 84]]},
                  {"sig": "q_next", "pts": [[178, 76], [230, 76]]},
                  {"sig": "clk", "pts": [[36, 94], [230, 94]]},
                  {"sig": "rst_n", "pts": [[36, 130], [258, 130], [258, 104]]}]},
    "signals": [{"n": "clk", "kind": "clk"}, {"n": "rst_n"}, {"n": "q", "bits": 2}, {"n": "q_next", "bits": 2}, {"n": "one", "bits": 2}],
    "frames": [
        F({"clk": 1, "rst_n": 0, "q": 0, "q_next": 1, "one": 1}, "reset 이 걸려 있다. q 는 0. 덧셈기는 벌써 q+1 = 1 을 내놓고 있지만 flop 이 안 받는다.", "Reset is asserted. q is 0. The adder already offers q+1 = 1, but the flop ignores it."),
        F({"clk": 0, "rst_n": 1, "q": 0, "q_next": 1, "one": 1}, "reset 을 풀었다. 아직 엣지 전이라 q 는 0.", "Reset released. No edge yet, so q is 0."),
        F({"clk": 1, "rst_n": 1, "q": 1, "q_next": 2, "one": 1}, "엣지. q 가 1. 덧셈기는 바로 2 를 준비한다. 되먹임 배선이 q 를 다시 덧셈기로 나른다.", "Edge. q is 1. The adder immediately prepares 2. The feedback wire carries q back into the adder."),
        F({"clk": 0, "rst_n": 1, "q": 1, "q_next": 2, "one": 1}, "정착. 아무것도 안 바뀐다. 카운터에는 입력이 없다. 시간이 곧 입력이다.", "Settled. Nothing changes. A counter has no input; time is the input."),
        F({"clk": 1, "rst_n": 1, "q": 2, "q_next": 3, "one": 1}, "엣지. q 가 2.", "Edge. q is 2."),
        F({"clk": 0, "rst_n": 1, "q": 2, "q_next": 3, "one": 1}, "정착.", "Settled."),
        F({"clk": 1, "rst_n": 1, "q": 3, "q_next": 0, "one": 1}, "엣지. q 가 3. 2 비트의 끝이다. 덧셈기가 내놓는 다음 값은 0 이다. 4 가 아니다.", "Edge. q is 3, the top of two bits. The adder's next value is 0, not 4."),
        F({"clk": 0, "rst_n": 1, "q": 3, "q_next": 0, "one": 1}, "정착.", "Settled."),
        F({"clk": 1, "rst_n": 1, "q": 0, "q_next": 1, "one": 1}, "엣지. q 가 0 으로 돌아왔다. 무한히 커지지 않는다. 비트 수만큼 세고 되감긴다.", "Edge. q is back to 0. It does not grow forever; it counts as far as its bits allow and wraps."),
        F({"clk": 0, "rst_n": 0, "q": 0, "q_next": 1, "one": 1}, "reset 을 다시 걸었다. 그런데 q 는 아직 안 바뀐다. 이 reset 은 엣지에서 듣는다.", "Reset asserted again, and yet q does not change yet. This reset is heard at the edge."),
        F({"clk": 1, "rst_n": 0, "q": 0, "q_next": 1, "one": 1}, "엣지. reset 이 이겨서 q 는 0. (원래 0 이었으니 안 보이지만, 3 이었어도 0 이 됐다.)", "Edge. Reset wins and q is 0. (It was 0 already, but it would have gone to 0 from 3 as well.)"),
        F({"clk": 0, "rst_n": 1, "q": 0, "q_next": 1, "one": 1}, "reset 을 풀면 다음 엣지부터 다시 센다.", "Release reset and counting resumes at the next edge."),
    ],
}

SWAP_NB = {
    "id": "p03-swap-nb",
    "title": {"ko": "<= 로 교환", "en": "Swapping with <="},
    "code": [{"t": "always_ff @(posedge clk) begin"},
             {"t": "  a <= b;", "drives": ["a"]},
             {"t": "  b <= a;", "drives": ["b"]},
             {"t": "end"}],
    "circuit": {"w": 320, "h": 180,
        "nodes": [{"id": "fa", "kind": "ff", "x": 120, "y": 20, "in": {"d": "b", "clk": "clk"}, "out": {"q": "a"}},
                  {"id": "fb", "kind": "ff", "x": 120, "y": 110, "in": {"d": "a", "clk": "clk"}, "out": {"q": "b"}}],
        "ports": [{"sig": "clk", "side": "in", "y": 144}, {"sig": "a", "side": "out", "y": 36}, {"sig": "b", "side": "out", "y": 126}],
        "wires": [{"sig": "a", "pts": [[176, 36], [284, 36]]},
                  {"sig": "a", "pts": [[240, 36], [240, 80], [96, 80], [96, 126], [120, 126]]},
                  {"sig": "b", "pts": [[176, 126], [284, 126]]},
                  {"sig": "b", "pts": [[250, 126], [250, 92], [86, 92], [86, 36], [120, 36]]},
                  {"sig": "clk", "pts": [[36, 144], [120, 144]]},
                  {"sig": "clk", "pts": [[60, 144], [60, 54], [120, 54]]}]},
    "signals": [{"n": "clk", "kind": "clk"}, {"n": "a"}, {"n": "b"}],
    "frames": [
        F({"clk": 1, "a": 1, "b": 0}, "a 는 1, b 는 0 으로 시작한다.", "Start with a = 1 and b = 0."),
        F({"clk": 0, "a": 1, "b": 0}, "두 flop 의 D 를 보라. fa 의 D 에는 b (0) 가, fb 의 D 에는 a (1) 가 걸려 있다. 둘 다 '옛 값' 이다.", "Look at both D inputs. fa's D carries b (0); fb's D carries a (1). Both are old values."),
        F({"clk": 1, "a": 0, "b": 1}, "엣지. 둘이 동시에 잡는다. a 는 0, b 는 1. 교환됐다.", "Edge. Both capture at once. a is 0, b is 1. Swapped."),
        F({"clk": 0, "a": 0, "b": 1}, "<= 는 '오른쪽을 지금 읽어두고, 엣지에 한꺼번에 쓴다' 이다. 그래서 순서가 없다.", "<= means 'read the right-hand side now, write them all at the edge'. So there is no order."),
        F({"clk": 1, "a": 1, "b": 0}, "엣지. 다시 교환.", "Edge. Swapped again."),
        F({"clk": 0, "a": 1, "b": 0}, "매 엣지마다 두 값이 자리를 바꾼다. 회로에서는 교차 배선 두 가닥이 그 일을 한다.", "Every edge the two values trade places. In the circuit, the two crossing wires do that."),
        F({"clk": 1, "a": 0, "b": 1}, "엣지.", "Edge."),
        F({"clk": 0, "a": 0, "b": 1}, "flop 두 개, 교차 배선 두 가닥. 코드 두 줄이 정확히 이 회로다.", "Two flops, two crossing wires. The two lines of code are exactly this circuit."),
    ],
}

SWAP_B = {
    "id": "p03-swap-b",
    "title": {"ko": "= 로 교환하려 하면", "en": "Trying to swap with ="},
    "code": [{"t": "always_ff @(posedge clk) begin"},
             {"t": "  a = b;", "drives": ["a"]},
             {"t": "  b = a;   // 이 a 는 방금 바뀐 a 다", "drives": ["b"]},
             {"t": "end"}],
    "circuit": {"w": 320, "h": 180,
        "nodes": [{"id": "fa", "kind": "ff", "x": 120, "y": 20, "in": {"d": "b", "clk": "clk"}, "out": {"q": "a"}},
                  {"id": "fb", "kind": "ff", "x": 120, "y": 110, "in": {"d": "b", "clk": "clk"}, "out": {"q": "b"}}],
        "ports": [{"sig": "clk", "side": "in", "y": 144}, {"sig": "a", "side": "out", "y": 36}, {"sig": "b", "side": "out", "y": 126}],
        "wires": [{"sig": "a", "pts": [[176, 36], [284, 36]]},
                  {"sig": "b", "pts": [[176, 126], [284, 126]]},
                  {"sig": "b", "pts": [[250, 126], [250, 92], [86, 92], [86, 36], [120, 36]]},
                  {"sig": "b", "pts": [[250, 92], [96, 92], [96, 126], [120, 126]]},
                  {"sig": "clk", "pts": [[36, 144], [120, 144]]},
                  {"sig": "clk", "pts": [[60, 144], [60, 54], [120, 54]]}]},
    "signals": [{"n": "clk", "kind": "clk"}, {"n": "a"}, {"n": "b"}],
    "frames": [
        F({"clk": 1, "a": 1, "b": 0}, "같은 출발. a 는 1, b 는 0.", "Same start: a = 1, b = 0."),
        F({"clk": 0, "a": 1, "b": 0}, "회로를 보라. 교차 배선이 없다. fb 의 D 에 자기 출력 b 가 되돌아와 있다. = 는 '위에서 아래로 차례로' 라서 둘째 줄의 a 는 첫째 줄이 방금 만든 a, 즉 b 다.", "Look at the circuit: no crossing wires. fb's D is fed by its own output b. = runs top to bottom, so the a in line two is the a line one just made, which is b."),
        F({"clk": 1, "a": 0, "b": 0}, "엣지. a 는 b 를 받아 0. b 는 자기 자신을 받아 0 그대로. 교환이 아니라 복사다.", "Edge. a takes b and becomes 0. b takes itself and stays 0. Not a swap; a copy."),
        F({"clk": 0, "a": 0, "b": 0}, "이제 둘 다 0 이다. 1 은 사라졌다.", "Both are 0 now. The 1 is gone."),
        F({"clk": 1, "a": 0, "b": 0}, "엣지. 영영 0 이다. b 의 flop 은 값이 안 바뀌니 합성기가 상수로 치워버릴 수도 있다.", "Edge. Zero forever. b's flop never changes, so a synthesiser may fold it into a constant."),
        F({"clk": 0, "a": 0, "b": 0}, "코드는 두 줄 그대로인데 회로가 다르다. 연산자 하나가 배선을 바꿨다.", "Same two lines of code, a different circuit. One operator rewired it."),
    ],
}

LATCH_NOELSE = {
    "id": "p03-latch-noelse",
    "title": {"ko": "else 가 없다", "en": "No else"},
    "code": [{"t": "always_comb"},
             {"t": "  if (sel) y = a;", "drives": ["y"]},
             {"t": "  // sel 이 0 이면? 아무 말이 없다"}],
    "circuit": {"w": 320, "h": 120,
        "nodes": [{"id": "l1", "kind": "latch", "x": 140, "y": 40, "in": {"d": "a", "en": "sel"}, "out": {"q": "y"}}],
        "ports": [{"sig": "a", "side": "in", "y": 56}, {"sig": "sel", "side": "in", "y": 74}, {"sig": "y", "side": "out", "y": 56}],
        "wires": [{"sig": "a", "pts": [[36, 56], [140, 56]]},
                  {"sig": "sel", "pts": [[36, 74], [140, 74]]},
                  {"sig": "y", "pts": [[196, 56], [284, 56]]}]},
    "signals": [{"n": "clk", "kind": "clk"}, {"n": "sel"}, {"n": "a"}, {"n": "y"}],
    "frames": [
        F({"clk": 1, "sel": 1, "a": 1, "y": 1}, "sel 이 1. y 는 a 를 따라 1. 여기까지는 조합 논리처럼 보인다.", "sel is 1. y follows a and is 1. So far it looks combinational."),
        F({"clk": 0, "sel": 1, "a": 1, "y": 1}, "회로를 보라. 합성기는 이 코드에서 latch 를 만들었다. always_comb 라고 썼는데도.", "Look at the circuit. The synthesiser built a latch from this code, despite the word always_comb."),
        F({"clk": 1, "sel": 1, "a": 1, "y": 1}, "아직은 문이 열려 있어서 티가 안 난다.", "The door is open, so nothing shows yet."),
        F({"clk": 0, "sel": 0, "a": 1, "y": 1}, "sel 이 0. 코드는 y 에 대해 아무 말이 없다. 그래서 y 는 '마지막 값' 1 을 붙든다. 문이 닫혔다.", "sel is 0. The code says nothing about y, so y keeps its last value, 1. The door has shut."),
        F({"clk": 1, "sel": 0, "a": 1, "y": 1}, "y 는 1. a 가 1 이라 아직 차이가 없다.", "y is 1. a is also 1, so no difference yet."),
        F({"clk": 0, "sel": 0, "a": 0, "y": 1}, "a 가 0 으로 내려갔다. 그런데 y 는 1 이다. 입력이 바뀌었는데 출력이 안 따라온다. 조합 논리가 아니다. 기억 소자다.", "a drops to 0, and y is still 1. The input changed and the output did not follow. This is not combinational logic; it is a memory element."),
        F({"clk": 1, "sel": 0, "a": 0, "y": 1}, "여전히 1 을 기억한다.", "Still remembering 1."),
        F({"clk": 0, "sel": 1, "a": 0, "y": 0}, "sel 이 1 로 돌아오자 문이 열리고 y 가 a 를 따라 0.", "sel returns to 1, the door opens, and y follows a to 0."),
        F({"clk": 1, "sel": 1, "a": 0, "y": 0}, "이 latch 는 clk 을 전혀 안 본다. 그래서 STA 가 재기 어렵고 테스트도 어렵다.", "This latch never looks at clk. That is why it is hard for STA to time and hard to test."),
        F({"clk": 0, "sel": 1, "a": 1, "y": 1}, "빠진 else 한 줄이 회로에 기억 소자를 하나 심었다.", "One missing else planted a memory element in the circuit."),
    ],
}

LATCH_ELSE = {
    "id": "p03-latch-else",
    "title": {"ko": "else 를 적었다", "en": "With the else"},
    "code": [{"t": "always_comb"},
             {"t": "  if (sel) y = a;", "drives": ["y"]},
             {"t": "  else     y = 1'b0;", "drives": ["y"]}],
    "circuit": {"w": 320, "h": 120,
        "nodes": [{"id": "c0", "kind": "const", "x": 70, "y": 36, "val": 0, "out": {"y": "zero"}},
                  {"id": "m1", "kind": "mux", "x": 140, "y": 36, "in": {"a": "zero", "b": "a", "sel": "sel"}, "out": {"y": "y"}}],
        "ports": [{"sig": "a", "side": "in", "y": 64}, {"sig": "sel", "side": "in", "y": 96}, {"sig": "y", "side": "out", "y": 56}],
        "wires": [{"sig": "zero", "pts": [[102, 48], [140, 48]]},
                  {"sig": "a", "pts": [[36, 64], [140, 64]]},
                  {"sig": "sel", "pts": [[36, 96], [164, 96], [164, 76]]},
                  {"sig": "y", "pts": [[188, 56], [284, 56]]}]},
    "signals": [{"n": "clk", "kind": "clk"}, {"n": "sel"}, {"n": "a"}, {"n": "zero"}, {"n": "y"}],
    "frames": [
        F({"clk": 1, "sel": 1, "a": 1, "zero": 0, "y": 1}, "같은 입력이다. sel 이 1, y 는 a 를 따라 1.", "Same inputs. sel is 1, y follows a and is 1."),
        F({"clk": 0, "sel": 1, "a": 1, "zero": 0, "y": 1}, "회로가 다르다. latch 대신 MUX 다. sel 이 위아래 중 하나를 고른다.", "The circuit is different: a MUX instead of a latch. sel picks one of the two inputs."),
        F({"clk": 1, "sel": 1, "a": 1, "zero": 0, "y": 1}, "MUX 는 기억이 없다. 항상 지금 입력만 본다.", "A MUX has no memory. It only ever looks at the inputs right now."),
        F({"clk": 0, "sel": 0, "a": 1, "zero": 0, "y": 0}, "sel 이 0. else 가 있으니 y 는 0. 왼쪽 시뮬레이션에서는 이 순간 1 을 붙들었다.", "sel is 0. With the else, y is 0. The simulation on the left held a 1 at this moment."),
        F({"clk": 1, "sel": 0, "a": 1, "zero": 0, "y": 0}, "y 는 0.", "y is 0."),
        F({"clk": 0, "sel": 0, "a": 0, "zero": 0, "y": 0}, "a 가 내려가도 y 는 0. 어차피 0 쪽을 고르고 있다.", "a drops and y is 0 regardless; the 0 input is selected anyway."),
        F({"clk": 1, "sel": 0, "a": 0, "zero": 0, "y": 0}, "기억할 것이 없다.", "Nothing to remember."),
        F({"clk": 0, "sel": 1, "a": 0, "zero": 0, "y": 0}, "sel 이 1. y 는 a 를 따라 0.", "sel is 1. y follows a and is 0."),
        F({"clk": 1, "sel": 1, "a": 0, "zero": 0, "y": 0}, "모든 경우에 y 를 정해주면 합성기는 기억 소자를 만들 이유가 없다.", "Give y a value in every case and the synthesiser has no reason to build memory."),
        F({"clk": 0, "sel": 1, "a": 1, "zero": 0, "y": 1}, "else 한 줄이 latch 를 MUX 로 바꿨다. 이것이 3 강이 말하는 latch inference 다.", "One else turned the latch into a MUX. This is what Lecture 3 calls latch inference."),
    ],
}

ALL = [XOR, FF, THREE, COUNTER, SWAP_NB, SWAP_B, LATCH_NOELSE, LATCH_ELSE]
```

- [ ] **Step 3: 본문 골격**

`.gstack/tmp/p03.py`. 이 Task 에서는 절마다 `.sim` 카드만 두고 글은 Task 7 에서 채운다.

```python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, ".gstack/tmp")
from pbuild import build
from p03_scen import ALL

TOC = [
    ("u1", "프로그램이 아니라 회로다", "Not a program, a circuit"),
    ("u2", "회로에는 '동시' 가 없다", "There is no 'at the same time' in a circuit"),
    ("u3", "flip-flop 은 엣지에서만 듣는다", "A flip-flop listens only at the edge"),
    ("u4", "comb, ff, latch 를 나란히", "comb, ff and latch side by side"),
    ("u5", "카운터: 시간이 입력이다", "A counter: time is the input"),
    ("u6", "= 과 <= 는 회로가 다르다", "= and <= build different circuits"),
    ("u7", "else 를 빼면 기억 소자가 생긴다", "Drop the else and you get memory"),
    ("u8", "3 강 어느 절로 가면 되나", "Where to go in Lecture 3"),
]

SEC = {
    "u1": "",
    "u2": '<div class="sim" data-sim="p03-xor"></div>',
    "u3": '<div class="sim" data-sim="p03-ff"></div>',
    "u4": '<div class="sim" data-sim="p03-three"></div>',
    "u5": '<div class="sim" data-sim="p03-counter"></div>',
    "u6": '<div class="grid2"><div class="sim" data-sim="p03-swap-nb"></div><div class="sim" data-sim="p03-swap-b"></div></div>',
    "u7": '<div class="grid2"><div class="sim" data-sim="p03-latch-noelse"></div><div class="sim" data-sim="p03-latch-else"></div></div>',
    "u8": "",
}

build(
    dst="notes/P03-before-lecture-3.html",
    lec="Before Lecture 3", title="회로로 생각하기",
    sub_ko="함수를 부르던 사람이 전선을 잇는 사람이 되기까지. 3 강을 읽기 전에 손에 익혀둘 동작 일곱 개.",
    sub_en="From calling functions to wiring gates. Seven behaviours to have in your hands before Lecture 3.",
    chips_ko=[("실습 입문", "hot"), ("시뮬레이션 8 개",), ("← → 키로도 넘어간다", "dim")],
    chips_en=[("hands-on primer", "hot"), ("8 simulations",), ("arrow keys work too", "dim")],
    toc=TOC, sections=SEC, scenarios=ALL, foot_lec="Before Lecture 3",
)
```

- [ ] **Step 4: 빌드하고 트레이스를 검사한다**

Run: `python .gstack/tmp/p03.py && node scripts/simcheck.mjs notes/P03-before-lecture-3.html`
Expected: 8 줄 전부 `[OK] … · frames N`, exit 0. `[FAIL]` 이 나오면 **시나리오를 고친다.** 검사기를 고치지 않는다. (검사기가 틀렸다고 확신할 때만 Task 1 로 돌아간다.)

- [ ] **Step 5: 카드가 전부 뜨는지**

Run: `node .gstack/tmp/simstep.mjs notes/P03-before-lecture-3.html`
Expected: 8 개 카드 전부 `[OK]`, 콘솔 에러 없음.

`grid2` 안의 두 카드가 900px 이상에서 나란히 서는지, 각 카드 안의 `sim-grid` 가 다시 둘로 갈라져서 너무 좁아지지 않는지 본다. 좁으면 `sim.js` CSS 에 `.grid2 .sim .sim-grid{grid-template-columns:minmax(0,1fr)}` 을 더한다 (나란히 놓인 카드 안에서는 코드와 회로를 세로로).

- [ ] **Step 6: 커밋**

```bash
git add notes/P03-before-lecture-3.html
git commit -m "P03: eight primer scenarios with checked traces, page skeleton"
```

---

### Task 7: P03 본문

**Files:**
- Modify: `.gstack/tmp/p03.py` (`SEC` 채우기)
- Output: `notes/P03-before-lecture-3.html`

**Interfaces:**
- Consumes: Task 6 의 시나리오 id 와 카드.
- 단원 형식: 흔한 그림 한 줄(`.callout`) → 짧은 도입 → `.sim` → `.def` 한 줄 정리. 3 강 노트로의 링크는 `L03-system-verilog-for-design.html#sN` 형식.

- [ ] **Step 1: 절 본문을 쓴다**

`SEC` 를 아래로 바꾼다. (`u2`~`u7` 의 `.sim` 자리는 Task 6 과 같다.)

```python
SIM = lambda i: f'<div class="sim" data-sim="{i}"></div>'
PAIR = lambda a, b: f'<div class="grid2">{SIM(a)}{SIM(b)}</div>'

SEC = {
"u1": '''
  <div class="callout">
    <p lang="ko"><strong>흔한 그림.</strong> "코드니까 첫 줄이 돌고, 그 다음 줄이 돌고, 그 다음 줄이 돈다."</p>
    <p lang="en"><strong>The usual picture.</strong> "It is code, so line one runs, then line two, then line three."</p>
  </div>
  <p lang="ko">Python 이나 C 에서 함수 세 개를 차례로 부르면 <strong>한 번에 하나만 살아 있다.</strong> 첫 함수가 끝나야 둘째가 시작한다. 그 사이 첫 함수는 존재하지 않는다.</p>
  <p lang="en">Call three functions in a row in Python or C and <strong>only one is alive at a time.</strong> The second starts when the first finishes, and in between the first does not exist.</p>
  <p lang="ko">HDL 로 쓴 세 줄은 <strong>세 개의 부품</strong>이다. 셋 다 기판 위에 납땜돼 있고, 셋 다 <strong>항상 켜져 있다.</strong> "실행 순서" 라는 게 없다. 있는 건 <strong>전선이 어디서 어디로 이어지는가</strong>뿐이다.</p>
  <p lang="en">Three lines of HDL are <strong>three components.</strong> All three are soldered onto the board and all three are <strong>always on.</strong> There is no execution order, only <strong>which wire goes where.</strong></p>
  <div class="grid2">
    <figure class="mini">
      <svg viewBox="0 0 320 150" role="img" aria-label="함수 호출. 세 상자가 위아래로 놓이고 화살표가 하나씩 차례로 내려간다">
        <text class="svgtxt" x="160" y="18" text-anchor="middle" style="font-size:10.5px;font-weight:700;fill:var(--ink2)" lang="ko">프로그램: 한 번에 하나</text>
        <text class="svgtxt" x="160" y="18" text-anchor="middle" style="font-size:10.5px;font-weight:700;fill:var(--ink2)" lang="en">a program: one at a time</text>
        <rect x="100" y="32" width="120" height="26" rx="6" fill="rgba(var(--ink-rgb),.06)" stroke="var(--ink3)" stroke-width="1.4"/>
        <text class="svglab" x="160" y="49" text-anchor="middle" style="font-size:10px;fill:var(--ink)">f()</text>
        <rect x="100" y="72" width="120" height="26" rx="6" fill="rgba(var(--ink-rgb),.06)" stroke="var(--ink3)" stroke-width="1.4"/>
        <text class="svglab" x="160" y="89" text-anchor="middle" style="font-size:10px;fill:var(--ink)">g()</text>
        <rect x="100" y="112" width="120" height="26" rx="6" fill="rgba(var(--ink-rgb),.06)" stroke="var(--ink3)" stroke-width="1.4"/>
        <text class="svglab" x="160" y="129" text-anchor="middle" style="font-size:10px;fill:var(--ink)">h()</text>
        <path d="M160 58 L160 70" stroke="var(--ink3)" stroke-width="1.4" marker-end="url(#p1a)"/>
        <path d="M160 98 L160 110" stroke="var(--ink3)" stroke-width="1.4" marker-end="url(#p1a)"/>
        <text class="svglab" x="236" y="49" style="font-size:9px;fill:var(--ink3)" lang="ko">끝나야</text>
        <text class="svglab" x="236" y="49" style="font-size:9px;fill:var(--ink3)" lang="en">must finish</text>
        <text class="svglab" x="236" y="89" style="font-size:9px;fill:var(--ink3)" lang="ko">끝나야</text>
        <text class="svglab" x="236" y="89" style="font-size:9px;fill:var(--ink3)" lang="en">must finish</text>
        <defs><marker id="p1a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="var(--ink3)"/></marker></defs>
      </svg>
      <figcaption lang="ko">위가 끝나야 아래가 산다.</figcaption>
      <figcaption lang="en">The one below lives only after the one above dies.</figcaption>
    </figure>
    <figure class="mini">
      <svg viewBox="0 0 320 150" role="img" aria-label="회로. 세 상자가 나란히 놓이고 전선으로 서로 이어져 있으며 셋 다 동시에 켜져 있다">
        <text class="svgtxt" x="160" y="18" text-anchor="middle" style="font-size:10.5px;font-weight:700;fill:var(--blue)" lang="ko">회로: 셋 다 항상 켜져 있다</text>
        <text class="svgtxt" x="160" y="18" text-anchor="middle" style="font-size:10.5px;font-weight:700;fill:var(--blue)" lang="en">a circuit: all three always on</text>
        <rect x="20" y="60" width="72" height="30" rx="6" fill="rgba(var(--blue-rgb),.14)" stroke="var(--blue)" stroke-width="1.6"/>
        <text class="svglab" x="56" y="79" text-anchor="middle" style="font-size:10px;fill:var(--blue)">f</text>
        <rect x="124" y="60" width="72" height="30" rx="6" fill="rgba(var(--blue-rgb),.14)" stroke="var(--blue)" stroke-width="1.6"/>
        <text class="svglab" x="160" y="79" text-anchor="middle" style="font-size:10px;fill:var(--blue)">g</text>
        <rect x="228" y="60" width="72" height="30" rx="6" fill="rgba(var(--blue-rgb),.14)" stroke="var(--blue)" stroke-width="1.6"/>
        <text class="svglab" x="264" y="79" text-anchor="middle" style="font-size:10px;fill:var(--blue)">h</text>
        <path d="M92 75 L120 75" stroke="var(--blue)" stroke-width="2" marker-end="url(#p1b)"/>
        <path d="M196 75 L224 75" stroke="var(--blue)" stroke-width="2" marker-end="url(#p1b)"/>
        <path d="M264 90 L264 118 L56 118 L56 94" fill="none" stroke="var(--blue)" stroke-width="2" marker-end="url(#p1b)"/>
        <text class="svglab" x="106" y="70" text-anchor="middle" style="font-size:8.5px;fill:var(--blue)" lang="ko">전선</text>
        <text class="svglab" x="106" y="70" text-anchor="middle" style="font-size:8.5px;fill:var(--blue)" lang="en">wire</text>
        <text class="svglab" x="160" y="132" text-anchor="middle" style="font-size:8.5px;fill:var(--blue)" lang="ko">되먹임도 그냥 전선이다</text>
        <text class="svglab" x="160" y="132" text-anchor="middle" style="font-size:8.5px;fill:var(--blue)" lang="en">feedback is just another wire</text>
        <defs><marker id="p1b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="var(--blue)"/></marker></defs>
      </svg>
      <figcaption lang="ko">순서가 아니라 연결이 전부다.</figcaption>
      <figcaption lang="en">Not order, only connection.</figcaption>
    </figure>
  </div>
  <div class="def">
    <p lang="ko"><strong>한 줄 정리.</strong> HDL 의 한 줄은 명령이 아니라 <strong>부품 하나</strong>다. 그래서 3 강이 첫 장부터 <strong>"You're not calling. You're instantiating."</strong> 이라고 못 박는다. 아래 일곱 단원은 전부 이 문장의 각주다.</p>
    <p lang="en"><strong>In one line.</strong> A line of HDL is not an instruction but <strong>a component.</strong> That is why Lecture 3 opens with <strong>"You're not calling. You're instantiating."</strong> The seven units below are footnotes to that sentence.</p>
  </div>
''',

"u2": f'''
  <div class="callout">
    <p lang="ko"><strong>흔한 그림.</strong> "a 와 b 를 같이 바꾸면 y 는 바로 맞는 값이 된다."</p>
    <p lang="en"><strong>The usual picture.</strong> "Change a and b together and y is right straight away."</p>
  </div>
  <p lang="ko">가장 단순한 회로부터. <code>y = a ^ b</code>. 게이트 하나다. 그런데 a 와 b 는 <strong>서로 다른 곳에서 서로 다른 길이의 전선을 타고 온다.</strong> 같은 순간에 바꿔도 같은 순간에 도착하지 않는다.</p>
  <p lang="en">Start with the simplest circuit: <code>y = a ^ b</code>, one gate. But a and b <strong>come from different places over wires of different lengths.</strong> Change them at the same moment and they still do not arrive at the same moment.</p>
  <p lang="ko">아래 파형의 <code>clk</code> 줄은 이 단원에서는 <strong>시간 눈금일 뿐</strong>이다. 아직 아무도 그 신호를 쓰지 않는다. 다음 단원부터 쓴다.</p>
  <p lang="en">In this unit the <code>clk</code> row in the waveform is <strong>only a ruler.</strong> Nothing uses it yet. The next unit does.</p>
  {SIM("p03-xor")}
  <div class="def">
    <p lang="ko"><strong>한 줄 정리.</strong> 조합 논리는 입력이 바뀌면 <strong>즉시</strong> 따라간다. 그래서 입력이 <strong>제각각</strong> 바뀌는 동안 출력은 <strong>틀린 값을 지나간다.</strong> 그걸 읽지 않으려면 <strong>언제 읽을지</strong>를 정해야 하고, 그 약속이 clk 이다.</p>
    <p lang="en"><strong>In one line.</strong> Combinational logic follows its inputs <strong>immediately</strong>, so while inputs change <strong>one by one</strong> the output <strong>passes through wrong values.</strong> To avoid reading those you need an agreement on <strong>when to read</strong>, and that agreement is clk.</p>
  </div>
''',

"u3": f'''
  <div class="callout">
    <p lang="ko"><strong>흔한 그림.</strong> "d 가 바뀌면 q 도 바뀐다. 대입이니까."</p>
    <p lang="en"><strong>The usual picture.</strong> "When d changes, q changes. It is an assignment."</p>
  </div>
  <p lang="ko">flip-flop 은 <strong>clk 의 올라가는 순간(posedge)에만</strong> D 를 본다. 그 순간의 D 값을 Q 에 옮기고, 다음 엣지까지 <strong>귀를 닫는다.</strong> 그 사이 D 가 열 번 바뀌어도 Q 는 모른다.</p>
  <p lang="en">A flip-flop looks at D <strong>only at the rising edge of clk (the posedge).</strong> It copies that instant's D into Q and then <strong>stops listening</strong> until the next edge. D may change ten times in between and Q will not know.</p>
  <p lang="ko">코드에서 그 약속이 <code>always_ff @(posedge clk)</code> 다. "이 블록은 posedge 에만 산다" 는 뜻이고, 회로에서는 <strong>상자 왼쪽 아래의 작은 삼각형</strong>이 그 표시다.</p>
  <p lang="en">In code the agreement is <code>always_ff @(posedge clk)</code>: "this block lives only at the posedge." In the circuit it is <strong>the small triangle at the bottom left of the box.</strong></p>
  {SIM("p03-ff")}
  <div class="def">
    <p lang="ko"><strong>한 줄 정리.</strong> <code>&lt;=</code> 는 "지금 옮겨라" 가 아니라 <strong>"다음 엣지에 옮겨라"</strong> 다. q 가 d 보다 <strong>늦는 것은 버그가 아니라 정의</strong>다. 그 '늦음' 이 2 단원의 틀린 값을 걸러낸다.</p>
    <p lang="en"><strong>In one line.</strong> <code>&lt;=</code> does not mean "copy now" but <strong>"copy at the next edge."</strong> q lagging d is <strong>not a bug but the definition</strong>, and that lag is what filters out unit 2's wrong values.</p>
  </div>
''',

"u4": f'''
  <div class="callout">
    <p lang="ko"><strong>흔한 그림.</strong> "셋 다 결국 q 에 d 를 넣는 거니까 같은 회로다."</p>
    <p lang="en"><strong>The usual picture.</strong> "All three end up putting d into q, so they are the same circuit."</p>
  </div>
  <p lang="ko">같은 d 를 세 갈래로 나눠 세 부품에 넣었다. <strong>조합 논리</strong>는 즉시 따라가고, <strong>flip-flop</strong> 은 엣지에서만 잡고, <strong>latch</strong> 는 <code>en</code> 이 열려 있는 동안 <strong>그대로 흘리다가</strong> 닫히면 마지막 값을 붙든다. 파형을 프레임 1 과 5 에서 멈춰서 보라.</p>
  <p lang="en">The same d is split three ways into three components. <strong>Combinational logic</strong> follows at once, the <strong>flip-flop</strong> captures only at the edge, and the <strong>latch</strong> <strong>passes d straight through</strong> while <code>en</code> is open, then holds the last value when it shuts. Stop the waveform at frames 1 and 5.</p>
  {SIM("p03-three")}
  <div class="def">
    <p lang="ko"><strong>한 줄 정리.</strong> 셋의 차이는 <strong>"언제 입력을 듣는가"</strong> 하나다. 항상 / 엣지 순간만 / en 이 열린 동안. 3 강은 이 셋 중 <strong>앞의 둘만 쓰고 셋째는 피하라</strong>고 한다. 왜 피하는지는 7 단원에서.</p>
    <p lang="en"><strong>In one line.</strong> The three differ in exactly one thing: <strong>when they listen to the input.</strong> Always; only at the edge instant; while en is open. Lecture 3 says <strong>use the first two and avoid the third.</strong> Why, in unit 7.</p>
  </div>
''',

"u5": f'''
  <div class="callout">
    <p lang="ko"><strong>흔한 그림.</strong> "<code>q &lt;= q + 1</code> 이니까 q 는 계속 커진다."</p>
    <p lang="en"><strong>The usual picture.</strong> "<code>q &lt;= q + 1</code>, so q keeps growing."</p>
  </div>
  <p lang="ko">flop 하나와 덧셈기 하나, 그리고 <strong>출력을 입력으로 되돌리는 전선 한 가닥.</strong> 이게 카운터의 전부다. 되먹임이 있는데도 무한 루프가 안 되는 이유는 <strong>flop 이 엣지에서만 듣기 때문</strong>이다. 엣지 한 번에 딱 한 번 돈다.</p>
  <p lang="en">One flop, one adder, and <strong>one wire carrying the output back to the input.</strong> That is the whole counter. There is feedback and yet no infinite loop, because <strong>the flop listens only at the edge.</strong> One edge, one step.</p>
  <p lang="ko">두 가지를 새로 본다. <strong>비트 수를 넘으면 0 으로 되감긴다</strong>는 것, 그리고 <strong>reset</strong>. 이 reset 은 <code>if (!rst_n)</code> 가 <code>always_ff</code> 안에 있어서 <strong>엣지에서 듣는다.</strong> 거는 순간 바로 0 이 되지 않는다. (4 강이 이 차이를 파고든다.)</p>
  <p lang="en">Two new things: <strong>past the last value it wraps to 0</strong>, and <strong>reset.</strong> This reset sits inside <code>always_ff</code> as <code>if (!rst_n)</code>, so <strong>it is heard at the edge</strong>; asserting it does not zero q at once. (Lecture 4 digs into that difference.)</p>
  {SIM("p03-counter")}
  <div class="def">
    <p lang="ko"><strong>한 줄 정리.</strong> 카운터에는 입력이 없다. <strong>시간이 입력</strong>이다. 그리고 하드웨어의 정수는 <strong>비트 수만큼만</strong> 센다.</p>
    <p lang="en"><strong>In one line.</strong> A counter has no input; <strong>time is the input.</strong> And a hardware integer counts <strong>only as far as its bits allow.</strong></p>
  </div>
''',

"u6": f'''
  <div class="callout">
    <p lang="ko"><strong>흔한 그림.</strong> "<code>=</code> 든 <code>&lt;=</code> 든 대입이니까 결과는 같다."</p>
    <p lang="en"><strong>The usual picture.</strong> "<code>=</code> or <code>&lt;=</code>, both are assignment, same result."</p>
  </div>
  <p lang="ko">두 flop 의 값을 맞바꾸는 코드 두 줄을 <strong>연산자만 바꿔서</strong> 나란히 놓았다. 왼쪽은 <code>&lt;=</code>, 오른쪽은 <code>=</code>. <strong>회로부터 비교하라.</strong> 왼쪽에는 교차 배선이 있고 오른쪽에는 없다.</p>
  <p lang="en">Two lines that swap two flops, placed side by side <strong>with only the operator changed.</strong> Left is <code>&lt;=</code>, right is <code>=</code>. <strong>Compare the circuits first.</strong> The left has crossing wires; the right does not.</p>
  {PAIR("p03-swap-nb", "p03-swap-b")}
  <div class="def">
    <p lang="ko"><strong>한 줄 정리.</strong> <code>&lt;=</code> 는 <strong>오른쪽을 전부 먼저 읽고 엣지에 한꺼번에 쓴다.</strong> <code>=</code> 는 <strong>위에서 아래로 차례로</strong> 쓰고 읽는다. 그래서 <code>always_ff</code> 안에서는 <code>&lt;=</code> 만 쓴다. 이게 3 강 17 절의 규칙 첫째 줄이다.</p>
    <p lang="en"><strong>In one line.</strong> <code>&lt;=</code> <strong>reads every right-hand side first and writes them all at the edge.</strong> <code>=</code> <strong>writes and reads top to bottom.</strong> That is why only <code>&lt;=</code> goes inside <code>always_ff</code>, the first rule in Lecture 3 &sect;17.</p>
  </div>
''',

"u7": f'''
  <div class="callout">
    <p lang="ko"><strong>흔한 그림.</strong> "<code>always_comb</code> 라고 썼으니 조합 논리다. else 는 있으면 좋고 없으면 말고."</p>
    <p lang="en"><strong>The usual picture.</strong> "I wrote <code>always_comb</code>, so it is combinational. The else is optional."</p>
  </div>
  <p lang="ko">4 단원에서 latch 를 봤다. 그걸 <strong>일부러 만든 적이 없는데도 생기는 순간</strong>이 이것이다. <code>if (sel) y = a;</code> 에서 sel 이 0 일 때 y 를 어떻게 하라는 말이 없으면, 합성기는 <strong>"그러면 유지하라는 뜻이겠지"</strong> 하고 latch 를 심는다. 왼쪽이 그 결과이고 오른쪽은 else 한 줄을 더한 것이다.</p>
  <p lang="en">Unit 4 showed a latch. This is the moment <strong>one appears without anyone asking for it.</strong> In <code>if (sel) y = a;</code>, if nothing says what y should be when sel is 0, the synthesiser concludes <strong>"then it must be held"</strong> and plants a latch. The left is that result; the right adds one else.</p>
  {PAIR("p03-latch-noelse", "p03-latch-else")}
  <div class="def">
    <p lang="ko"><strong>한 줄 정리.</strong> 조합 블록에서 <strong>모든 경우에 출력을 정해주지 않으면 기억 소자가 생긴다.</strong> <code>if</code> 에는 <code>else</code>, <code>case</code> 에는 <code>default</code>. 3 강이 <strong>latch inference</strong> 라고 부르는 것이 정확히 이 왼쪽 회로다.</p>
    <p lang="en"><strong>In one line.</strong> In a combinational block, <strong>leave any case without an output and you get memory.</strong> An <code>else</code> for every <code>if</code>, a <code>default</code> for every <code>case</code>. What Lecture 3 calls <strong>latch inference</strong> is exactly the circuit on the left.</p>
  </div>
''',

"u8": '''
  <p lang="ko">이 페이지의 단원이 3 강 노트의 어느 절에 대응하는지. <strong>여기서 손으로 본 것을 거기서 이름과 규칙으로 다시 만난다.</strong></p>
  <p lang="en">Where each unit lands in the Lecture 3 notes. <strong>What you stepped through here comes back there with names and rules.</strong></p>
  <table>
    <thead><tr><th><span lang="ko">여기</span><span lang="en">Here</span></th><th><span lang="ko">3 강에서</span><span lang="en">In Lecture 3</span></th></tr></thead>
    <tbody>
      <tr><td><a href="#u1">01</a></td><td><a href="L03-system-verilog-for-design.html#s1"><span lang="ko">§01 · HDL 은 프로그래밍 언어가 아니다</span><span lang="en">§01 · HDL is not a programming language</span></a></td></tr>
      <tr><td><a href="#u2">02</a> · <a href="#u3">03</a></td><td><a href="L03-system-verilog-for-design.html#s3"><span lang="ko">§03 · always_comb 와 always_ff</span><span lang="en">§03 · always_comb and always_ff</span></a></td></tr>
      <tr><td><a href="#u4">04</a> · <a href="#u7">07</a></td><td><a href="L03-system-verilog-for-design.html#s3"><span lang="ko">§03 · latch inference 함정</span><span lang="en">§03 · the latch inference trap</span></a></td></tr>
      <tr><td><a href="#u5">05</a></td><td><a href="L03-system-verilog-for-design.html#s16"><span lang="ko">§16 · 언제 무엇을 쓰나 (순차 논리 줄)</span><span lang="en">§16 · what to use when (the sequential row)</span></a></td></tr>
      <tr><td><a href="#u6">06</a></td><td><a href="L03-system-verilog-for-design.html#s17"><span lang="ko">§17 · 설계 규칙 넷 (blocking 을 섞지 마라)</span><span lang="en">§17 · the four design rules (do not mix blocking)</span></a></td></tr>
    </tbody>
  </table>
  <div class="callout">
    <p lang="ko"><strong>이 페이지가 안 다룬 것.</strong> typedef · enum · struct · interface · package 같은 <strong>규모를 다루는 문법</strong>은 여기 없다. 동작이 아니라 정리의 문제라 시뮬레이션으로 보여줄 것이 없다. 3 강 노트 4 · 5 절로 바로 가면 된다.</p>
    <p lang="en"><strong>Not covered here.</strong> Constructs that handle <strong>scale</strong>, typedef, enum, struct, interface, package, are absent. They are about organisation rather than behaviour, so there is nothing to simulate. Go straight to Lecture 3 &sect;4 and &sect;5.</p>
  </div>
  <div class="callout">
    <p lang="ko"><strong>다음.</strong> <a href="P04-before-lecture-4.html">4 강 전에 손에 익힐 것</a>. 여기서 당연하게 쓴 <strong>"엣지 순간"</strong> 이 사실은 폭이 있는 창이라는 것, 그리고 클럭이 둘이 되면 무슨 일이 나는지.</p>
    <p lang="en"><strong>Next.</strong> <a href="P04-before-lecture-4.html">Before Lecture 4</a>: that the <strong>"edge instant"</strong> taken for granted here is really a window with width, and what happens when there are two clocks.</p>
  </div>
''',
}
```

링크 대상 `#s1`, `#s3`, `#s16`, `#s17` 이 L03 노트에 실제로 있는지는 `verify.mjs` 가 검사한다. 없으면 L03 노트를 열어 맞는 절 id 로 고친다.

- [ ] **Step 2: 빌드 · 검사 넷**

```bash
python .gstack/tmp/p03.py
node scripts/simcheck.mjs notes/P03-before-lecture-3.html
node scripts/verify.mjs   notes/P03-before-lecture-3.html
node scripts/langcheck.mjs notes/P03-before-lecture-3.html
node .gstack/tmp/simstep.mjs notes/P03-before-lecture-3.html
```

Expected: 넷 다 exit 0. `verify` 는 `[--] 슬라이드 리더: data-slide 앵커가 없어 건너뜀` 이 정상이고, 도해 스크린샷이 **정적 도해 2 장 + 카드 8 장 = 10 장** 나와야 한다. (Task 5 의 링크 검사가 `P04-before-lecture-4.html` 을 아직 못 찾아 `[FAIL]` 하면 P04 를 만든 뒤 다시 돌린다. 그 하나만 예외다.)

- [ ] **Step 3: 스크린샷을 한 장씩 본다**

`shots/P03-before-lecture-3-fig01.png` 부터 `fig10.png` 까지 전부 연다. 볼 것:
- 배지 글자가 상자나 배선 위에 겹치지 않는가. 겹치면 그 신호의 첫 배선 `pts[0]` 을 옮긴다.
- 파형의 버스 값 글자가 띠 안에 들어가는가.
- `grid2` 안의 카드 둘이 너무 좁아 코드가 잘리지 않는가.
- 다크모드: `shots/…-desktop.png` 는 라이트다. 브라우저에서 ☾ 다크로 바꿔 배선과 배지가 보이는지 본다.

- [ ] **Step 4: 커밋**

```bash
git add notes/P03-before-lecture-3.html
git commit -m "P03: before Lecture 3, a hands-on primer in seven units"
```

---

### Task 8: P04 시나리오 여섯 개와 페이지 골격

**Files:**
- Create: `.gstack/tmp/p04_scen.py`
- Create: `.gstack/tmp/p04.py` (골격)
- Output: `notes/P04-before-lecture-4.html`

**Interfaces:**
- Consumes: Task 6 의 `pbuild.build`, Task 1 의 노드 의미 (`late`, `arst_n`, `X`, `M` 건너뜀).
- 시나리오 id: `p04-setup`, `p04-skew`, `p04-cdc`, `p04-rst-sync`, `p04-rst-async`, `p04-recovery`.

- [ ] **Step 1: 시나리오 데이터**

`.gstack/tmp/p04_scen.py`:

```python
# -*- coding: utf-8 -*-
"""P04 시나리오. X 는 '알 수 없음', M 은 metastable. 검사기는 그 칸을 건너뛴다."""


def F(v, ko, en):
    return {"v": v, "note": {"ko": ko, "en": en}}


FF_CIRCUIT = {"w": 320, "h": 120,
    "nodes": [{"id": "f1", "kind": "ff", "x": 140, "y": 40, "in": {"d": "d", "clk": "clk"}, "out": {"q": "q"}}],
    "ports": [{"sig": "d", "side": "in", "y": 56}, {"sig": "q", "side": "out", "y": 56}, {"sig": "clk", "side": "in", "y": 96}],
    "wires": [{"sig": "d", "pts": [[36, 56], [140, 56]]},
              {"sig": "q", "pts": [[196, 56], [284, 56]]},
              {"sig": "clk", "pts": [[36, 96], [120, 96], [120, 74], [140, 74]]}]}

SETUP = {
    "id": "p04-setup",
    "title": {"ko": "엣지 '순간' 에 d 가 바뀌면", "en": "When d changes 'at' the edge"},
    "code": [{"t": "always_ff @(posedge clk)"}, {"t": "  q <= d;", "drives": ["q"]}],
    "circuit": FF_CIRCUIT,
    "signals": [{"n": "clk", "kind": "clk"}, {"n": "d"}, {"n": "q"}],
    "frames": [
        F({"clk": 1, "d": 0, "q": 0}, "3 강 전 페이지에서 본 flop 그대로다. 다만 이번에는 d 를 바꾸는 시점을 고른다.", "The same flop as the P03 page. This time we choose when d changes."),
        F({"clk": 0, "d": 0, "q": 0}, "정착. d 는 아직 0.", "Settled. d is still 0."),
        F({"clk": 1, "d": 1, "q": "X"}, "d 가 엣지와 같은 순간에 1 로 올라갔다. flop 이 0 을 본 건지 1 을 본 건지 정해지지 않았다. q 는 X. '모른다' 는 뜻이다.", "d rose to 1 in the same instant as the edge. Whether the flop saw 0 or 1 is undecided. q is X, meaning unknown."),
        F({"clk": 0, "d": 1, "q": "X"}, "한 사이클 내내 X 다. 실물에서는 0 아니면 1 중 하나가 나오지만, 어느 쪽인지 설계자는 모른다. 그걸 받아 쓰는 논리도 모른다.", "X for the whole cycle. In silicon it is a 0 or a 1, but the designer does not know which, and neither does the logic downstream."),
        F({"clk": 1, "d": 1, "q": 1}, "다음 엣지. 이번엔 d 가 한참 전부터 1 이었다. q 는 깨끗하게 1.", "Next edge. This time d has been 1 for ages. q is a clean 1."),
        F({"clk": 0, "d": 0, "q": 1}, "d 가 정착 프레임에서 내려갔다. 엣지와 멀다. 안전하다.", "d falls in a settled frame, far from the edge. Safe."),
        F({"clk": 1, "d": 0, "q": 0}, "엣지. q 는 0. 문제없다.", "Edge. q is 0. No problem."),
        F({"clk": 0, "d": 0, "q": 0}, "엣지 앞뒤로 d 가 가만히 있어야 하는 폭이 있다. 앞이 setup time, 뒤가 hold time 이다. 4 강 01 절이 그 숫자를 잰다.", "There is a width on either side of the edge where d must sit still: setup time before, hold time after. Lecture 4 §01 measures those numbers."),
    ],
}

SKEW = {
    "id": "p04-skew",
    "title": {"ko": "같은 clk 인데 둘째 flop 에 늦게 도착하면", "en": "Same clk, but it reaches the second flop late"},
    "code": [{"t": "always_ff @(posedge clk) begin"},
             {"t": "  q1 <= din;", "drives": ["q1"]},
             {"t": "  q2 <= q1;    // 한 칸 뒤따라야 한다", "drives": ["q2"]},
             {"t": "end"}],
    "circuit": {"w": 380, "h": 150,
        "nodes": [{"id": "f1", "kind": "ff", "x": 110, "y": 30, "in": {"d": "din", "clk": "clk"}, "out": {"q": "q1"}},
                  {"id": "d1", "kind": "delay", "x": 150, "y": 100, "in": {"a": "clk"}, "out": {"y": "clk_late"}},
                  {"id": "f2", "kind": "ff", "x": 250, "y": 30, "late": True, "in": {"d": "q1", "clk": "clk_late"}, "out": {"q": "q2"}}],
        "ports": [{"sig": "din", "side": "in", "y": 46}, {"sig": "clk", "side": "in", "y": 114}, {"sig": "q2", "side": "out", "y": 46}],
        "wires": [{"sig": "din", "pts": [[36, 46], [110, 46]]},
                  {"sig": "q1", "pts": [[166, 46], [250, 46]]},
                  {"sig": "q2", "pts": [[306, 46], [344, 46]]},
                  {"sig": "clk", "pts": [[36, 114], [150, 114]]},
                  {"sig": "clk", "pts": [[70, 114], [70, 64], [110, 64]]},
                  {"sig": "clk_late", "pts": [[190, 114], [230, 114], [230, 64], [250, 64]]}]},
    "signals": [{"n": "clk", "kind": "clk"}, {"n": "clk_late"}, {"n": "din"}, {"n": "q1"}, {"n": "q2"}],
    "frames": [
        F({"clk": 1, "clk_late": 1, "din": 0, "q1": 0, "q2": 0}, "flop 두 개를 이어 놓았다. 제대로면 q2 는 q1 을 한 칸 뒤따라야 한다. 그런데 둘째 flop 의 clk 앞에 '지연' 상자가 있다. 배선이 길어서 늦게 도착한다는 뜻이다.", "Two flops in a chain. Done right, q2 should trail q1 by one step. But there is a 'delay' box in front of the second flop's clk: its wire is longer, so the clock arrives late."),
        F({"clk": 0, "clk_late": 0, "din": 1, "q1": 0, "q2": 0}, "din 이 1.", "din is 1."),
        F({"clk": 1, "clk_late": 1, "din": 1, "q1": 1, "q2": 1}, "엣지. q1 이 1 을 잡았다. 그리고 q2 도 1 이다. 늦게 온 엣지가 '방금 바뀐' q1 을 봐버렸다. 한 칸 늦어야 하는데 같은 칸에 와 있다.", "Edge. q1 captures 1. And q2 is 1 too. The late edge saw the q1 that had just changed. It should be one step behind and it is not."),
        F({"clk": 0, "clk_late": 0, "din": 0, "q1": 1, "q2": 1}, "이게 hold 위반이다. 엣지 직후에 D 가 가만히 있어야 하는데, 앞 flop 이 바꿔버린 새 값이 이미 와 있었다.", "This is a hold violation. D must sit still just after the edge, but the new value from the flop in front had already arrived."),
        F({"clk": 1, "clk_late": 1, "din": 0, "q1": 0, "q2": 0}, "엣지. 또 같이 바뀐다. 두 단짜리 shift register 가 한 단처럼 동작한다.", "Edge. They change together again. A two-stage shift register behaving like one stage."),
        F({"clk": 0, "clk_late": 0, "din": 1, "q1": 0, "q2": 0}, "코드는 틀린 데가 없다. 틀린 것은 clk 이 두 flop 에 도착하는 시각의 차이, 즉 skew 다.", "Nothing in the code is wrong. What is wrong is the difference in when clk reaches the two flops: skew."),
        F({"clk": 1, "clk_late": 1, "din": 1, "q1": 1, "q2": 1}, "엣지.", "Edge."),
        F({"clk": 0, "clk_late": 0, "din": 1, "q1": 1, "q2": 1}, "이 문제는 RTL 만 보고는 알 수 없다. 배선이 깔린 뒤에야 skew 가 정해진다. 4 강 03 절이 그 이야기다.", "You cannot see this from the RTL. Skew is decided only after the wires are laid out. Lecture 4 §03 is about that."),
    ],
}

CDC = {
    "id": "p04-cdc",
    "title": {"ko": "다른 클럭에서 온 신호를 잡으면", "en": "Capturing a signal from another clock"},
    "code": [{"t": "// a 는 clkA 도메인에서 온다"},
             {"t": "always_ff @(posedge clkB) begin"},
             {"t": "  q1 <= a;", "drives": ["q1"]},
             {"t": "  q2 <= q1;   // 두 번째 단", "drives": ["q2"]},
             {"t": "end"}],
    "circuit": {"w": 380, "h": 150,
        "nodes": [{"id": "f1", "kind": "ff", "x": 110, "y": 30, "in": {"d": "a", "clk": "clkB"}, "out": {"q": "q1"}},
                  {"id": "f2", "kind": "ff", "x": 230, "y": 30, "in": {"d": "q1", "clk": "clkB"}, "out": {"q": "q2"}}],
        "ports": [{"sig": "a", "side": "in", "y": 46}, {"sig": "clkB", "side": "in", "y": 114}, {"sig": "q2", "side": "out", "y": 46}],
        "wires": [{"sig": "a", "pts": [[36, 46], [110, 46]]},
                  {"sig": "q1", "pts": [[166, 46], [230, 46]]},
                  {"sig": "q2", "pts": [[286, 46], [344, 46]]},
                  {"sig": "clkB", "pts": [[36, 114], [70, 114], [70, 64], [110, 64]]},
                  {"sig": "clkB", "pts": [[70, 114], [190, 114], [190, 64], [230, 64]]}]},
    "signals": [{"n": "clkB", "kind": "clk"}, {"n": "clkA"}, {"n": "a"}, {"n": "q1"}, {"n": "q2"}],
    "frames": [
        F({"clkB": 1, "clkA": 1, "a": 0, "q1": 0, "q2": 0}, "clkA 줄을 보라. clkB 와 박자가 다르다. a 는 clkA 에 맞춰 바뀌므로 clkB 입장에서는 아무 때나 바뀌는 신호다.", "Look at the clkA row. It beats differently from clkB. a changes to clkA's rhythm, so from clkB's point of view it changes at random."),
        F({"clkB": 0, "clkA": 1, "a": 0, "q1": 0, "q2": 0}, "정착.", "Settled."),
        F({"clkB": 1, "clkA": 0, "a": 1, "q1": "M", "q2": 0}, "a 가 하필 clkB 의 엣지에 바뀌었다. 첫 flop 이 metastable 로 빠졌다. M. 0 도 1 도 아닌 중간 전압이다.", "a changed right on clkB's edge. The first flop went metastable: M, a voltage between 0 and 1."),
        F({"clkB": 0, "clkA": 0, "a": 1, "q1": 1, "q2": 0}, "반 클럭이 지나는 동안 가라앉았다. 1 이 됐다. 0 이 됐을 수도 있다. 중요한 것은 둘째 flop 이 볼 때쯤엔 정해져 있다는 것이다.", "Over the half clock it settled, to 1 here; it could have been 0. What matters is that by the time the second flop looks, it has decided."),
        F({"clkB": 1, "clkA": 1, "a": 1, "q1": 1, "q2": 1}, "엣지. q2 가 1 을 잡았다. q2 는 M 을 본 적이 없다.", "Edge. q2 captures 1. q2 never saw the M."),
        F({"clkB": 0, "clkA": 1, "a": 0, "q1": 1, "q2": 1}, "a 가 내려갔다. 이번엔 엣지와 멀다.", "a drops, this time far from the edge."),
        F({"clkB": 1, "clkA": 0, "a": 0, "q1": 0, "q2": 1}, "엣지. q1 은 깨끗하게 0.", "Edge. q1 is a clean 0."),
        F({"clkB": 0, "clkA": 0, "a": 0, "q1": 0, "q2": 1}, "만약 둘째 flop 이 없었다면 프레임 2 의 M 이 뒤의 논리로 그대로 나갔다. 둘째 flop 은 M 을 없애는 게 아니라 가라앉을 시간을 한 클럭 벌어준다.", "Without the second flop, frame 2's M would have gone straight into the logic behind. The second flop does not remove the M; it buys one clock for it to settle."),
        F({"clkB": 1, "clkA": 1, "a": 0, "q1": 0, "q2": 0}, "엣지. q2 가 0.", "Edge. q2 is 0."),
        F({"clkB": 0, "clkA": 1, "a": 0, "q1": 0, "q2": 0}, "이 두 단을 synchronizer 라고 부른다. 4 강 06 · 07 절, 그리고 5 강 FIFO 의 포인터가 건널 때 다시 만난다.", "These two stages are called a synchronizer. You meet them again in Lecture 4 §06 and §07, and when the FIFO pointers cross in Lecture 5."),
    ],
}

RST_CIRCUIT = lambda pin: {"w": 320, "h": 130,
    "nodes": [{"id": "c1", "kind": "const", "x": 60, "y": 40, "val": 1, "out": {"y": "one"}},
              {"id": "f1", "kind": "ff", "x": 140, "y": 36, "in": {"d": "one", "clk": "clk", pin: pin}, "out": {"q": "q"}}],
    "ports": [{"sig": "clk", "side": "in", "y": 70}, {"sig": pin, "side": "in", "y": 110}, {"sig": "q", "side": "out", "y": 52}],
    "wires": [{"sig": "one", "pts": [[92, 52], [140, 52]]},
              {"sig": "q", "pts": [[196, 52], [284, 52]]},
              {"sig": "clk", "pts": [[36, 70], [140, 70]]},
              {"sig": pin, "pts": [[36, 110], [168, 110], [168, 80]]}]}

RST_SYNC = {
    "id": "p04-rst-sync",
    "title": {"ko": "동기 reset", "en": "Synchronous reset"},
    "code": [{"t": "always_ff @(posedge clk)"},
             {"t": "  if (!rst_n) q <= 1'b0;", "drives": ["q"]},
             {"t": "  else        q <= 1'b1;", "drives": ["q"]}],
    "circuit": RST_CIRCUIT("rst_n"),
    "signals": [{"n": "clk", "kind": "clk"}, {"n": "rst_n"}, {"n": "one"}, {"n": "q"}],
    "frames": [
        F({"clk": 1, "rst_n": 1, "one": 1, "q": 1}, "flop 이 계속 1 을 잡고 있다. rst_n 이 sensitivity list 에 없다. 그래서 이 reset 은 엣지에서만 들린다.", "The flop keeps capturing 1. rst_n is not in the sensitivity list, so this reset is heard only at the edge."),
        F({"clk": 0, "rst_n": 1, "one": 1, "q": 1}, "정착.", "Settled."),
        F({"clk": 1, "rst_n": 1, "one": 1, "q": 1}, "엣지. 여전히 1.", "Edge. Still 1."),
        F({"clk": 0, "rst_n": 0, "one": 1, "q": 1}, "rst_n 을 걸었다. 그런데 q 는 아직 1 이다. 엣지가 안 왔으니까.", "rst_n asserted, and q is still 1, because no edge has come."),
        F({"clk": 1, "rst_n": 0, "one": 1, "q": 0}, "엣지. 이제야 0. 걸고 나서 반 클럭이 지났다.", "Edge. Only now 0, half a clock after asserting."),
        F({"clk": 0, "rst_n": 1, "one": 1, "q": 0}, "rst_n 을 풀었다. q 는 0 그대로. 다음 엣지까지.", "rst_n released. q stays 0 until the next edge."),
        F({"clk": 1, "rst_n": 1, "one": 1, "q": 1}, "엣지. 다시 1.", "Edge. Back to 1."),
        F({"clk": 0, "rst_n": 1, "one": 1, "q": 1}, "reset 이 클럭에 묶여 있다. 클럭이 없으면 reset 도 없다. 4 강이 왜 그게 문제인지 말한다.", "The reset is tied to the clock. No clock, no reset. Lecture 4 says why that is a problem."),
    ],
}

RST_ASYNC = {
    "id": "p04-rst-async",
    "title": {"ko": "비동기 reset", "en": "Asynchronous reset"},
    "code": [{"t": "always_ff @(posedge clk or negedge arst_n)"},
             {"t": "  if (!arst_n) q <= 1'b0;", "drives": ["q"]},
             {"t": "  else         q <= 1'b1;", "drives": ["q"]}],
    "circuit": RST_CIRCUIT("arst_n"),
    "signals": [{"n": "clk", "kind": "clk"}, {"n": "arst_n"}, {"n": "one"}, {"n": "q"}],
    "frames": [
        F({"clk": 1, "arst_n": 1, "one": 1, "q": 1}, "같은 flop. 다른 점은 arst_n 이 sensitivity list 에 들어 있다는 것 하나다.", "The same flop. The one difference: arst_n is in the sensitivity list."),
        F({"clk": 0, "arst_n": 1, "one": 1, "q": 1}, "정착.", "Settled."),
        F({"clk": 1, "arst_n": 1, "one": 1, "q": 1}, "엣지. 1.", "Edge. 1."),
        F({"clk": 0, "arst_n": 0, "one": 1, "q": 0}, "arst_n 을 걸었다. q 가 즉시 0. 엣지를 기다리지 않는다. 왼쪽과 이 프레임을 비교하라.", "arst_n asserted. q is 0 immediately, without waiting for an edge. Compare this frame with the left."),
        F({"clk": 1, "arst_n": 0, "one": 1, "q": 0}, "엣지가 와도 reset 이 이긴다. 0.", "The edge comes and reset still wins. 0."),
        F({"clk": 0, "arst_n": 1, "one": 1, "q": 0}, "풀었다. 이쪽은 푸는 것도 즉시 반영되지만, 새 값을 잡는 건 엣지의 몫이라 q 는 아직 0.", "Released. Release takes effect at once too, but capturing a new value is the edge's job, so q is still 0."),
        F({"clk": 1, "arst_n": 1, "one": 1, "q": 1}, "엣지. 1.", "Edge. 1."),
        F({"clk": 0, "arst_n": 1, "one": 1, "q": 1}, "걸 때는 즉시, 풀고 나서 새 값은 엣지에서. 이 비대칭이 4 강 09 · 10 절의 결론으로 이어진다.", "Assert takes effect at once; a new value after release waits for the edge. That asymmetry leads to the conclusion of Lecture 4 §09 and §10."),
    ],
}

RECOVERY = {
    "id": "p04-recovery",
    "title": {"ko": "비동기 reset 을 엣지 근처에서 풀면", "en": "Releasing an async reset near the edge"},
    "code": [{"t": "always_ff @(posedge clk or negedge arst_n)"},
             {"t": "  if (!arst_n) q <= 1'b0;", "drives": ["q"]},
             {"t": "  else         q <= 1'b1;", "drives": ["q"]}],
    "circuit": RST_CIRCUIT("arst_n"),
    "signals": [{"n": "clk", "kind": "clk"}, {"n": "arst_n"}, {"n": "one"}, {"n": "q"}],
    "frames": [
        F({"clk": 1, "arst_n": 1, "one": 1, "q": 1}, "앞 단원과 같은 flop 이다. 이번엔 reset 을 푸는 시점을 엣지에 겹쳐본다.", "The same flop as the previous unit. This time the release is made to coincide with the edge."),
        F({"clk": 0, "arst_n": 0, "one": 1, "q": 0}, "걸었다. 즉시 0.", "Asserted. 0 at once."),
        F({"clk": 1, "arst_n": 0, "one": 1, "q": 0}, "엣지. 아직 걸려 있으니 0.", "Edge. Still asserted, so 0."),
        F({"clk": 0, "arst_n": 0, "one": 1, "q": 0}, "정착.", "Settled."),
        F({"clk": 1, "arst_n": 1, "one": 1, "q": "X"}, "엣지와 같은 순간에 풀었다. flop 은 '아직 reset 중' 인지 '이제 1 을 잡아야' 하는지 정하지 못했다. X.", "Released in the same instant as the edge. The flop could not decide between 'still in reset' and 'capture the 1 now'. X."),
        F({"clk": 0, "arst_n": 1, "one": 1, "q": "X"}, "1 단원의 setup/hold 와 같은 종류의 사고다. 대상이 d 가 아니라 reset 을 푸는 시점일 뿐이다.", "The same kind of accident as unit 1's setup/hold, except the subject is the reset release rather than d."),
        F({"clk": 1, "arst_n": 1, "one": 1, "q": 1}, "다음 엣지. 이제는 깨끗하게 1.", "Next edge. Now a clean 1."),
        F({"clk": 0, "arst_n": 1, "one": 1, "q": 1}, "그래서 reset 은 걸 때는 아무 때나 걸어도 되지만 풀 때는 엣지에 맞춰 풀어야 한다. 4 강 10 절이 이걸 recovery time 이라고 부른다.", "So a reset may be asserted any time but must be released in step with the edge. Lecture 4 §10 calls this recovery time."),
    ],
}

ALL = [SETUP, SKEW, CDC, RST_SYNC, RST_ASYNC, RECOVERY]
```

`RST_CIRCUIT` 에서 `"in": {…, pin: pin}` 은 `rst_n` 또는 `arst_n` 키를 그 자리에 만든다. 포트 이름도 같이 바뀐다.

- [ ] **Step 2: 골격**

`.gstack/tmp/p04.py`:

```python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, ".gstack/tmp")
from pbuild import build
from p04_scen import ALL

TOC = [
    ("u0", "먼저 3 강 전 페이지", "The P03 page first"),
    ("u1", "엣지는 순간이 아니라 창이다", "The edge is a window, not an instant"),
    ("u2", "같은 clk 도 같은 순간에 오지 않는다", "Even the same clk does not arrive at once"),
    ("u3", "다른 클럭에서 온 신호", "A signal from another clock"),
    ("u4", "reset 을 걸 때: 동기와 비동기", "Asserting reset: sync and async"),
    ("u5", "reset 을 풀 때", "Releasing reset"),
    ("u6", "4 강 어느 절로 가면 되나", "Where to go in Lecture 4"),
]

SEC = {
    "u0": "",
    "u1": '<div class="sim" data-sim="p04-setup"></div>',
    "u2": '<div class="sim" data-sim="p04-skew"></div>',
    "u3": '<div class="sim" data-sim="p04-cdc"></div>',
    "u4": '<div class="grid2"><div class="sim" data-sim="p04-rst-sync"></div><div class="sim" data-sim="p04-rst-async"></div></div>',
    "u5": '<div class="sim" data-sim="p04-recovery"></div>',
    "u6": "",
}

build(
    dst="notes/P04-before-lecture-4.html",
    lec="Before Lecture 4", title="엣지에는 폭이 있다",
    sub_ko="3 강 전 페이지에서 '엣지 순간' 이라고 넘어간 것에 사실은 폭이 있고, 클럭이 둘이 되면 그 폭이 사고가 된다. 4 강을 읽기 전에 손에 익혀둘 동작 다섯 개.",
    sub_en="The 'edge instant' the P03 page took for granted has width, and with two clocks that width becomes an accident. Five behaviours to have in your hands before Lecture 4.",
    chips_ko=[("실습 입문", "hot"), ("시뮬레이션 6 개",), ("P03 의 3 · 4 단원을 전제", "dim")],
    chips_en=[("hands-on primer", "hot"), ("6 simulations",), ("assumes P03 units 3 and 4", "dim")],
    toc=TOC, sections=SEC, scenarios=ALL, foot_lec="Before Lecture 4",
)
```

- [ ] **Step 3: 빌드 · 트레이스 검사 · 카드 확인**

```bash
python .gstack/tmp/p04.py
node scripts/simcheck.mjs notes/P04-before-lecture-4.html
node .gstack/tmp/simstep.mjs notes/P04-before-lecture-4.html
```

Expected: `simcheck` 6 개 전부 `[OK]` (X · M 칸은 건너뛰므로 통과해야 한다. `p04-skew` 는 `late:true` 덕에 통과한다). `simstep` 6 개 카드 `[OK]`, 콘솔 에러 없음.

- [ ] **Step 4: 커밋**

```bash
git add notes/P04-before-lecture-4.html
git commit -m "P04: six primer scenarios with checked traces, page skeleton"
```

---

### Task 9: P04 본문

**Files:**
- Modify: `.gstack/tmp/p04.py` (`SEC` 채우기)
- Output: `notes/P04-before-lecture-4.html`

- [ ] **Step 1: 절 본문을 쓴다**

```python
SIM = lambda i: f'<div class="sim" data-sim="{i}"></div>'
PAIR = lambda a, b: f'<div class="grid2">{SIM(a)}{SIM(b)}</div>'

SEC = {
"u0": '''
  <p lang="ko">이 페이지는 <a href="P03-before-lecture-3.html">3 강 전 페이지</a>의 <strong>3 단원(flip-flop)과 4 단원(comb · ff · latch)</strong>을 안다고 전제한다. flop 이 엣지에서만 듣는다는 것이 손에 안 익었으면 거기부터.</p>
  <p lang="en">This page assumes <strong>units 3 (the flip-flop) and 4 (comb, ff, latch)</strong> of <a href="P03-before-lecture-3.html">the P03 page</a>. If "a flop listens only at the edge" is not yet in your hands, start there.</p>
  <p lang="ko">거기서는 <strong>"엣지 순간"</strong> 이라는 말을 아무 의심 없이 썼다. 이 페이지는 그 말을 의심한다. <strong>순간에는 폭이 있고, 그 폭 안에서 무슨 일이 나는지</strong>가 4 강 전체의 주제다.</p>
  <p lang="en">That page used the phrase <strong>"the edge instant"</strong> without a second thought. This page has the second thought. <strong>The instant has width, and what happens inside that width</strong> is the whole of Lecture 4.</p>
  <div class="callout">
    <p lang="ko"><strong>파형에 새 글자가 둘 나온다.</strong> <code>X</code> 는 "0 인지 1 인지 모른다", <code>M</code> 은 "0 도 1 도 아닌 중간에 걸려 있다(metastable)". 둘 다 <strong>amber</strong> 로 칠한다. 이 페이지에서 amber 가 보이면 그 자리가 사고다.</p>
    <p lang="en"><strong>Two new letters appear in the waveforms.</strong> <code>X</code> means "0 or 1, unknown"; <code>M</code> means "stuck between 0 and 1 (metastable)". Both are drawn in <strong>amber</strong>. Wherever you see amber on this page, that is the accident.</p>
  </div>
''',

"u1": f'''
  <div class="callout">
    <p lang="ko"><strong>흔한 그림.</strong> "엣지에 딱 맞춰 d 를 바꾸면 그 새 값이 잡힌다."</p>
    <p lang="en"><strong>The usual picture.</strong> "Change d exactly at the edge and the new value is captured."</p>
  </div>
  <p lang="ko">flop 이 엣지에서 D 를 '보는' 데는 <strong>시간이 든다.</strong> 엣지 <strong>직전</strong> 얼마 동안과 <strong>직후</strong> 얼마 동안 D 가 가만히 있어야 한다. 그 사이에 D 가 움직이면 flop 은 옛 값과 새 값 중 <strong>어느 쪽도 확실히 못 잡는다.</strong></p>
  <p lang="en">A flop takes <strong>time</strong> to 'see' D at the edge. D must sit still for a while <strong>before</strong> the edge and a while <strong>after</strong>. If D moves inside that span, the flop <strong>cannot reliably capture either</strong> the old value or the new one.</p>
  {SIM("p04-setup")}
  <div class="def">
    <p lang="ko"><strong>한 줄 정리.</strong> 엣지 앞의 폭이 <strong>setup time</strong>, 뒤의 폭이 <strong>hold time</strong> 이다. 그 창을 지키는지 재는 도구가 STA 이고, 4 강 01 절이 그 다섯 개의 시간에 이름을 붙인다.</p>
    <p lang="en"><strong>In one line.</strong> The width before the edge is <strong>setup time</strong>, the width after is <strong>hold time</strong>. STA is the tool that checks the window is respected, and Lecture 4 &sect;01 names its five times.</p>
  </div>
''',

"u2": f'''
  <div class="callout">
    <p lang="ko"><strong>흔한 그림.</strong> "같은 clk 이니까 두 flop 은 같은 순간에 잡는다."</p>
    <p lang="en"><strong>The usual picture.</strong> "It is the same clk, so both flops capture at the same instant."</p>
  </div>
  <p lang="ko">clk 도 전선을 타고 온다. 2 단원의 a 와 b 처럼 <strong>도착 시각이 flop 마다 다르다.</strong> 그 차이를 <strong>skew</strong> 라고 한다. 대개는 아무 문제가 없다. 문제가 되는 경우 하나를 골라 보여준다. <strong>앞 flop 의 새 출력이, 늦게 온 엣지보다 먼저 뒤 flop 에 도착할 때.</strong></p>
  <p lang="en">clk travels over wires too, so like a and b in P03 unit 2 <strong>it reaches each flop at a different time.</strong> That difference is <strong>skew</strong>. Usually harmless. Here is the one case where it is not: <strong>the front flop's new output reaches the back flop before the late edge does.</strong></p>
  {SIM("p04-skew")}
  <div class="def">
    <p lang="ko"><strong>한 줄 정리.</strong> 1 단원의 창을 <strong>d 가 아니라 clk 이 어긴 것</strong>이다. RTL 에는 흔적이 없고 <strong>배선이 깔린 뒤에야</strong> 드러난다. 4 강 03 절이 클럭 트리와 skew 를 다룬다.</p>
    <p lang="en"><strong>In one line.</strong> Unit 1's window violated <strong>by clk rather than by d.</strong> There is no trace of it in the RTL; it shows up <strong>only once the wires are laid.</strong> Lecture 4 &sect;03 covers the clock tree and skew.</p>
  </div>
''',

"u3": f'''
  <div class="callout">
    <p lang="ko"><strong>흔한 그림.</strong> "다른 클럭에서 온 신호도 flop 에 넣으면 그냥 잡힌다."</p>
    <p lang="en"><strong>The usual picture.</strong> "A signal from another clock gets captured like any other if you feed it to a flop."</p>
  </div>
  <p lang="ko">지금까지는 입력이 <strong>같은 clk 에 맞춰</strong> 바뀌었다. 그래서 1 단원의 창을 피할 수 있었다. <strong>다른 클럭</strong>에서 온 신호는 우리 엣지와 아무 약속이 없다. <strong>충분히 오래 돌리면 반드시 창 안에서 바뀌는 순간이 온다.</strong> 그때 flop 은 <code>X</code> 보다 나쁜 상태, <code>M</code> 에 빠진다.</p>
  <p lang="en">So far the inputs changed <strong>in step with the same clk</strong>, which is how they avoided unit 1's window. A signal from <strong>another clock</strong> has no agreement with our edge. <strong>Run long enough and it is guaranteed to change inside the window.</strong> The flop then enters something worse than <code>X</code>: <code>M</code>.</p>
  {SIM("p04-cdc")}
  <div class="def">
    <p lang="ko"><strong>한 줄 정리.</strong> 없앨 수는 없다. <strong>flop 을 하나 더 붙여 가라앉을 시간을 한 클럭 벌어준다.</strong> 그 두 단이 synchronizer 이고, 4 강 06 · 07 절과 5 강 FIFO 의 포인터 경로가 전부 이 상자 둘로 시작한다.</p>
    <p lang="en"><strong>In one line.</strong> It cannot be eliminated. <strong>Add one more flop to buy a clock for it to settle.</strong> Those two stages are a synchronizer, and Lecture 4 &sect;06, &sect;07 and the pointer paths of Lecture 5's FIFO all start from these two boxes.</p>
  </div>
''',

"u4": f'''
  <div class="callout">
    <p lang="ko"><strong>흔한 그림.</strong> "reset 을 걸면 즉시 0 이 된다."</p>
    <p lang="en"><strong>The usual picture.</strong> "Assert reset and it goes to 0 immediately."</p>
  </div>
  <p lang="ko">P03 의 카운터에서 reset 이 <strong>엣지까지 기다리는 것</strong>을 봤다. 그게 전부가 아니다. reset 을 <strong>sensitivity list 에 넣으면</strong> 엣지와 상관없이 즉시 듣는 flop 이 된다. 코드 한 줄 차이를 나란히 놓았다. <strong>프레임 3 에서 멈춰 둘을 비교하라.</strong></p>
  <p lang="en">In P03's counter you saw reset <strong>wait for the edge.</strong> That is not the whole story. Put the reset <strong>in the sensitivity list</strong> and the flop hears it at once, edge or no edge. The two are side by side, one line apart. <strong>Stop at frame 3 and compare.</strong></p>
  {PAIR("p04-rst-sync", "p04-rst-async")}
  <div class="def">
    <p lang="ko"><strong>한 줄 정리.</strong> 구별법은 하나다. <strong>reset 이 sensitivity list 에 있는가.</strong> 있으면 비동기, 없으면 동기. 왜 실무가 비동기로 거는지(전원 직후에는 클럭이 없다)는 4 강 09 절.</p>
    <p lang="en"><strong>In one line.</strong> One test: <strong>is the reset in the sensitivity list?</strong> If yes, asynchronous; if no, synchronous. Why practice asserts asynchronously (there is no clock right after power-up) is Lecture 4 &sect;09.</p>
  </div>
''',

"u5": f'''
  <div class="callout">
    <p lang="ko"><strong>흔한 그림.</strong> "reset 을 풀면 바로 정상 동작한다."</p>
    <p lang="en"><strong>The usual picture.</strong> "Release reset and normal operation resumes at once."</p>
  </div>
  <p lang="ko">비동기 reset 은 <strong>거는 것</strong>은 아무 때나 해도 된다. 모두를 0 으로 몰아넣을 뿐이니까. 그런데 <strong>푸는 것</strong>은 다르다. 푸는 순간이 엣지와 겹치면 flop 은 "아직 reset 중" 과 "이제 새 값" 사이에서 <strong>1 단원과 똑같은 사고</strong>를 낸다.</p>
  <p lang="en">An asynchronous reset may be <strong>asserted</strong> at any time; it only drives everything to 0. <strong>Releasing</strong> it is different. If the release coincides with the edge, the flop has <strong>exactly unit 1's accident</strong> between "still in reset" and "new value now".</p>
  {SIM("p04-recovery")}
  <div class="def">
    <p lang="ko"><strong>한 줄 정리.</strong> <strong>걸 때는 비동기로, 풀 때는 동기로.</strong> 이 비대칭이 4 강 09 · 10 절의 결론이고, 그걸 회로로 만든 것이 reset synchronizer 다. 그리고 그 회로는 3 단원의 두 상자와 <strong>모양이 똑같다.</strong></p>
    <p lang="en"><strong>In one line.</strong> <strong>Assert asynchronously, release synchronously.</strong> That asymmetry is the conclusion of Lecture 4 &sect;09 and &sect;10, and the circuit that implements it is the reset synchronizer, which <strong>looks exactly like</strong> unit 3's two boxes.</p>
  </div>
''',

"u6": '''
  <p lang="ko">이 페이지의 단원이 4 강 노트의 어느 절에 대응하는지.</p>
  <p lang="en">Where each unit lands in the Lecture 4 notes.</p>
  <table>
    <thead><tr><th><span lang="ko">여기</span><span lang="en">Here</span></th><th><span lang="ko">4 강에서</span><span lang="en">In Lecture 4</span></th></tr></thead>
    <tbody>
      <tr><td><a href="#u1">01</a></td><td><a href="L04-clock-and-reset.html#s1"><span lang="ko">§01 · Timing basics: setup · hold · 다섯 개의 시간</span><span lang="en">§01 · Timing basics: setup, hold, the five times</span></a></td></tr>
      <tr><td><a href="#u2">02</a></td><td><a href="L04-clock-and-reset.html#s3"><span lang="ko">§03 · Clock distribution 과 skew</span><span lang="en">§03 · Clock distribution and skew</span></a></td></tr>
      <tr><td><a href="#u3">03</a></td><td><a href="L04-clock-and-reset.html#s6"><span lang="ko">§06 · CDC · Metastability</span><span lang="en">§06 · CDC and metastability</span></a> · <a href="L04-clock-and-reset.html#s7"><span lang="ko">§07 · Double-FF</span><span lang="en">§07 · Double-FF</span></a></td></tr>
      <tr><td><a href="#u4">04</a></td><td><a href="L04-clock-and-reset.html#s9"><span lang="ko">§09 · Sync reset 과 Async reset</span><span lang="en">§09 · Sync and async reset</span></a></td></tr>
      <tr><td><a href="#u5">05</a></td><td><a href="L04-clock-and-reset.html#s10"><span lang="ko">§10 · Assertion · De-assertion · recovery time</span><span lang="en">§10 · Assertion, de-assertion, recovery time</span></a></td></tr>
    </tbody>
  </table>
  <div class="callout">
    <p lang="ko"><strong>이 페이지가 안 다룬 것.</strong> PLL · DLL · clock gating (4 강 02 · 04 절), RDC (11 · 12 절), gray code 와 FIFO (07 절과 5 강). 앞의 둘은 동작보다 부품 이야기고, 뒤의 둘은 이 페이지의 3 단원을 안 뒤에 읽으면 그대로 읽힌다.</p>
    <p lang="en"><strong>Not covered here.</strong> PLL, DLL and clock gating (Lecture 4 &sect;02, &sect;04), RDC (&sect;11, &sect;12), gray code and FIFOs (&sect;07 and Lecture 5). The first two are about components more than behaviour; the last two read fine once unit 3 here is in your hands.</p>
  </div>
''',
}
```

- [ ] **Step 2: 빌드 · 검사 넷, 그리고 P03 도 다시**

```bash
python .gstack/tmp/p04.py
node scripts/simcheck.mjs notes/P04-before-lecture-4.html
node scripts/verify.mjs   notes/P04-before-lecture-4.html
node scripts/langcheck.mjs notes/P04-before-lecture-4.html
node .gstack/tmp/simstep.mjs notes/P04-before-lecture-4.html
node scripts/verify.mjs   notes/P03-before-lecture-3.html    # P04 링크가 이제 살아 있는지
```

Expected: 전부 exit 0. P04 도해 스크린샷 6 장.

- [ ] **Step 3: 스크린샷을 한 장씩 본다**

`shots/P04-before-lecture-4-fig01.png` ~ `fig06.png`. 특히 `X` · `M` 칸의 amber 상자 안 글자가 읽히는지, `p04-skew` 의 `delay` 상자와 `clk_late` 배선이 flop 상자를 관통하지 않는지.

- [ ] **Step 4: 커밋**

```bash
git add notes/P04-before-lecture-4.html
git commit -m "P04: before Lecture 4, edge windows, skew, metastability and reset"
```

---

### Task 10: 허브 · 콜아웃 · 스킬 문서 · 푸시

**Files:**
- Modify: `index.html` (glossary 카드 아래에 입문 카드)
- Modify: `notes/L03-system-verilog-for-design.html` (00 절 첫머리에 콜아웃)
- Modify: `notes/L04-clock-and-reset.html` (같은 자리)
- Modify: `.claude/skills/note-html/SKILL.md` (파일 명명 표, 인라인 규칙 예외)

- [ ] **Step 1: `index.html` 입문 카드**

glossary 카드(`<a class="gloss"` 로 시작하는 블록) **바로 뒤**에 넣는다. 클래스는 glossary 카드와 같은 것을 쓴다 (`gloss`). 안의 아이콘 자리는 glossary 카드의 것을 복사하고 글자만 `A→Z` 대신 `▶|` 로.

```html
  <a class="gloss" href="notes/P03-before-lecture-3.html">
    <span class="gi">▶|</span>
    <span class="gt" lang="ko"><b>실습 입문</b> · Verilog 를 한 번도 안 봤으면 여기부터. 클럭 · flip-flop · comb / ff / latch 를 코드 · 회로 · 파형 나란히 놓고 반 클럭씩 밟아본다. <a href="notes/P03-before-lecture-3.html">3 강 전</a> · <a href="notes/P04-before-lecture-4.html">4 강 전</a></span>
    <span class="gt" lang="en"><b>Hands-on primer</b> · Never seen Verilog? Start here. Clock, flip-flop, comb / ff / latch with code, circuit and waveform side by side, stepped half a clock at a time. <a href="notes/P03-before-lecture-3.html">Before L3</a> · <a href="notes/P04-before-lecture-4.html">Before L4</a></span>
    <span class="go" lang="ko">밟아보기 →</span>
    <span class="go" lang="en">Step through →</span>
  </a>
```

**`<a>` 안에 `<a>` 는 verify 가 중복 id 검사에서 잡는다.** 그래서 위처럼 쓰면 실패한다. 바깥을 `<div class="gloss">` 로 바꾸고 `.gloss` 의 hover 규칙이 `a.gloss` 에만 걸려 있으면 `div.gloss:hover` 를 하나 더한다. 아니면 안쪽 링크 둘을 빼고 카드 전체를 P03 으로 보내고 P03 마지막 절이 P04 로 잇게 둔다 (이미 그렇게 돼 있다). **둘째 방법이 단순하다. 그걸 쓴다.** 안쪽 `<a>` 둘을 지우고 `3 강 전 · 4 강 전` 을 그냥 글자로 둔다.

- [ ] **Step 2: L03 · L04 콜아웃**

각 노트의 `<section id="s0">` 안, `.sec-head` 바로 다음 줄에:

```html
  <div class="callout">
    <p lang="ko"><strong>Verilog 를 한 번도 안 봤으면</strong> 이 노트보다 <a href="P03-before-lecture-3.html">3 강 전에 손에 익힐 것</a>이 먼저다. 클럭 · flip-flop · comb / ff / latch 를 코드 · 회로 · 파형으로 반 클럭씩 밟아본다.</p>
    <p lang="en"><strong>Never seen Verilog?</strong> <a href="P03-before-lecture-3.html">Before Lecture 3</a> comes before this note. It steps through clock, flip-flop and comb / ff / latch half a clock at a time, with code, circuit and waveform side by side.</p>
  </div>
```

L04 는 `P04-before-lecture-4.html` 과 "4 강 전에" 로 바꿔 넣는다.

- [ ] **Step 3: `note-html` 스킬**

파일 명명 표에 두 행:

```
  P03-before-lecture-3.html                       실습 입문 (아래 참조)
  P{NN}-{kebab}.html                              n 강을 읽기 전에 손에 익힐 동작. data-slide 없음, reader.js 없음, sim.js 사용

sim.js                                            반 클럭 프레임 시뮬레이션 뷰어 (P 페이지가 공유)
```

"자체완결형" 절의 예외 문장을 이렇게 고친다:

> 예외는 둘이다. PDF 리더(`reader.js`)와 **실습 입문 페이지의 시뮬레이션 뷰어(`sim.js`)**. 둘 다 repo 안 로컬 파일이므로 "외부 의존성 없음" 은 유지된다. 둘 다 없어도 노트 본문은 그대로 읽혀야 한다.

그리고 "P 페이지" 소절을 파일 명명 절 끝에 더한다:

> ### 실습 입문 페이지 (`P{NN}-*.html`)
>
> 강의 요약이 아니라 **"이 코드는 이 회로이고 이렇게 돈다"** 를 보여주는 장르다. 단원은 **코드 → 회로 → 밟아본다 → 한 줄 정리** 네 단. 시나리오는 페이지 안 `<script type="application/json" id="sim-data">` 에 두고 `.sim[data-sim="id"]` 카드가 부른다. 형식과 노드 의미는 `docs/superpowers/specs/2026-09-13-hands-on-primer-design.md`. **트레이스는 손으로 쓰므로 `node scripts/simcheck.mjs <페이지>` 를 반드시 돌린다.** `verify.mjs` 는 `.sim` 카드도 도해처럼 찍는다.

- [ ] **Step 4: 검사**

```bash
node scripts/verify.mjs index.html
node scripts/langcheck.mjs index.html
node scripts/verify.mjs notes/L03-system-verilog-for-design.html
node scripts/verify.mjs notes/L04-clock-and-reset.html
node scripts/langcheck.mjs notes/L03-system-verilog-for-design.html
node scripts/langcheck.mjs notes/L04-clock-and-reset.html
```

Expected: 전부 exit 0. `index.html` 의 페이지 간 링크 개수가 2 늘어난다.

- [ ] **Step 5: 커밋 · 푸시**

```bash
git add index.html notes/L03-system-verilog-for-design.html notes/L04-clock-and-reset.html .claude/skills/note-html/SKILL.md
git commit -m "Link the hands-on primer from the hub and from Lectures 3 and 4; document P pages and sim.js"
git push
```

푸시 뒤 GitHub Pages 에서 `notes/P03-before-lecture-3.html` 을 열어 `sim.js` 가 로드되는지 (시크바가 보이는지) 한 번 본다. 로컬과 달리 경로 대소문자가 엄격하다.

---

## 계획 자체 점검

- **spec 대조.** 장르 규칙 표 → Task 10 스킬 문서. 단원 목록 P03 · P04 → Task 6 ~ 9. `.sim` 카드 모양 · 조작 · 색 → Task 2 ~ 4. 데이터 형식 → Task 1 인터페이스와 Task 6 · 8 데이터. `sim.js` 위치와 없을 때의 동작 → Task 2 (`sim-fail`). `simcheck.mjs` 규칙 여섯 줄 → Task 1. 검증 네 명령 → Task 7 · 9. 허브 · 콜아웃 · 스킬 → Task 10. "안 하는 것" 은 어느 Task 에도 없다.
- **자리표시자.** 없음. 모든 코드 단계에 코드가 있다.
- **이름 일관성.** `checkScenario` · `extractData` (Task 1) 는 CLI 만 쓴다. `renderWave` · `renderCircuit` · `renderCode` 는 `mount` 의 `renderers` 에 같은 서명 `(sc, host) → (i) => void` 으로 들어간다. `card.simGo` · `card.simFrame` 은 Task 2 가 만들고 `simstep.mjs` 가 읽는다. 시나리오 id 는 Task 6 · 8 의 데이터와 Task 7 · 9 의 `SIM(...)` 이 같은 문자열이다. 노드 핀 좌표는 Task 3 의 `GEOM` 과 Task 6 · 8 의 `wires[].pts` 끝점이 같은 표를 따른다.
- **spec 과 다른 곳 하나.** spec 의 P03 6 단원 "회로에서 flop 하나가 사라진다" 는 정확하지 않아 계획에서는 **"교차 배선이 사라지고 b 가 자기 자신을 잡는다"** 로 썼다. spec 도 같이 고친다 (Task 6 커밋에 포함).
