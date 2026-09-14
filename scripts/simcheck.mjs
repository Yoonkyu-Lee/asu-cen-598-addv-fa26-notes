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
