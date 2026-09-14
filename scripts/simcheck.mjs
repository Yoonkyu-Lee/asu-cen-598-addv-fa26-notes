#!/usr/bin/env node
// scripts/simcheck.mjs
// P 페이지의 시뮬레이션 트레이스는 손으로 쓴다. 그래서 틀릴 수 있다.
// #sim-data 의 시나리오를 꺼내 노드 종류(ff · latch · 게이트)의 의미대로
// 값을 다시 계산하고 손으로 쓴 값과 대조한다. 어긋나면 exit 1.
import fs from 'node:fs';

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
  // 핀 이름에 오타가 나면 그 노드의 값이 undefined 가 되고, expect 가 조용히 넘어간다.
  // 검사가 통째로 사라지는 셈이라 여기서 잡는다.
  for (const n of (sc.circuit && sc.circuit.nodes) || [])
    for (const [pin, name] of [...Object.entries(n.in || {}), ...Object.entries(n.out || {})])
      if (!sigs[name]) errs.push(`${sc.id}: 노드 ${n.id} 의 ${pin} 이 없는 신호 ${name}`);

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
      case 'mul': expect(i, OUT.y, gate(v(i, IN.a), v(i, IN.b), (a, b) => (a * b) & mask(bits(OUT.y)))); break;
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
// ff 하나로는 게이트 · latch · add 의 mask 가 한 번도 안 돌아간다. 노드를 섞은 두 번째 시나리오.
// rst_n 이 걸린 ff, late ff, latch, xor, and, const, 그리고 2 bit 로 자리올림이 잘리는 add.
const GOOD2 = {
  id: 'self-mix',
  code: [
    { t: 'always_ff @(posedge clk) q1 <= !rst_n ? 0 : d;', drives: ['q1'] },
    { t: 'always_ff @(posedge clk) q2 <= e;', drives: ['q2'] },
    { t: 'always_latch if (en) ql = dl;', drives: ['ql'] },
    { t: 'assign xy = q1 ^ ql;', drives: ['xy'] },
    { t: 'assign an = q2 & ql;', drives: ['an'] },
    { t: 'assign sum = x + one;', drives: ['sum'] },
  ],
  circuit: { w: 560, h: 320,
    nodes: [
      { id: 'f1', kind: 'ff', x: 160, y: 30, in: { d: 'd', clk: 'clk', rst_n: 'rst_n' }, out: { q: 'q1' } },
      { id: 'f2', kind: 'ff', x: 160, y: 100, late: true, in: { d: 'e', clk: 'clk' }, out: { q: 'q2' } },
      { id: 'l1', kind: 'latch', x: 160, y: 170, in: { d: 'dl', en: 'en' }, out: { q: 'ql' } },
      { id: 'x1', kind: 'xor', x: 340, y: 60, in: { a: 'q1', b: 'ql' }, out: { y: 'xy' } },
      { id: 'a1', kind: 'and', x: 340, y: 140, in: { a: 'q2', b: 'ql' }, out: { y: 'an' } },
      { id: 'c1', kind: 'const', x: 160, y: 250, val: 1, out: { y: 'one' } },
      { id: 's1', kind: 'add', x: 340, y: 250, in: { a: 'x', b: 'one' }, out: { y: 'sum' } },
      { id: 'm1', kind: 'mul', x: 460, y: 250, in: { a: 'x', b: 'one' }, out: { y: 'pm' } },
    ],
    ports: [], wires: [{ sig: 'd', pts: [[20, 50], [160, 50]] }, { sig: 'ql', pts: [[240, 190], [340, 190]] }] },
  signals: [
    { n: 'clk', kind: 'clk' }, { n: 'rst_n' }, { n: 'd' }, { n: 'q1' }, { n: 'e' }, { n: 'q2' },
    { n: 'en' }, { n: 'dl' }, { n: 'ql' }, { n: 'xy' }, { n: 'an' },
    { n: 'x', bits: 2 }, { n: 'one', bits: 2 }, { n: 'sum', bits: 2 }, { n: 'pm', bits: 4 },
  ],
  frames: [
    { v: { clk: 1, rst_n: 0, d: 1, q1: 0, e: 1, q2: 1, en: 0, dl: 1, ql: 0, xy: 0, an: 0, x: 0, one: 1, sum: 1, pm: 0 } },
    { v: { clk: 0, rst_n: 0, d: 1, q1: 0, e: 0, q2: 1, en: 0, dl: 0, ql: 0, xy: 0, an: 0, x: 1, one: 1, sum: 2, pm: 1 } },
    { v: { clk: 1, rst_n: 1, d: 1, q1: 0, e: 1, q2: 1, en: 1, dl: 1, ql: 1, xy: 1, an: 1, x: 2, one: 1, sum: 3, pm: 2 } },
    { v: { clk: 0, rst_n: 1, d: 1, q1: 0, e: 1, q2: 1, en: 1, dl: 0, ql: 0, xy: 0, an: 0, x: 3, one: 1, sum: 0, pm: 3 } },
    { v: { clk: 1, rst_n: 1, d: 0, q1: 1, e: 0, q2: 0, en: 0, dl: 1, ql: 0, xy: 1, an: 0, x: 3, one: 1, sum: 0, pm: 3 } },
    { v: { clk: 0, rst_n: 1, d: 0, q1: 1, e: 1, q2: 0, en: 0, dl: 0, ql: 0, xy: 1, an: 0, x: 0, one: 1, sum: 1, pm: 0 } },
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
  ['mul 곱이 틀림', (() => { const s = clone(GOOD2); s.frames[2].v.pm = 9; return s; })(), 1],
  ['X 는 건너뜀', (() => { const s = clone(GOOD); s.frames[2].v.q = 'X'; s.frames[3].v.q = 'X'; return s; })(), 0],
  ['노드 핀 이름에 오타', (() => { const s = clone(GOOD); s.circuit.nodes[0].in.d = 'dd'; return s; })(), 1],
  ['정상 (여러 노드)', GOOD2, 0],
  ['latch 가 en=1 인데 앞 값을 붙듦', (() => { const s = clone(GOOD2); s.frames[3].v.ql = 1; return s; })(), 1],
  ['late 플롭이 d[i-1] 을 읽음', (() => { const s = clone(GOOD2); s.frames[2].v.q2 = 0; return s; })(), 1],
  ['엣지에서 rst_n 을 무시함', (() => { const s = clone(GOOD2); s.frames[2].v.q1 = 1; return s; })(), 1],
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
