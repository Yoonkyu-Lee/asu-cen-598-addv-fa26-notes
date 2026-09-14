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
.sim .wire{fill:none;stroke-linejoin:round;transition:stroke-width .15s}
.sim .wire.w0{stroke:var(--blue);stroke-width:1.4;opacity:.45}
.sim .wire.w1{stroke:var(--blue);stroke-width:2.6}
.sim .wire.wx{stroke:var(--amber);stroke-width:2.4;stroke-dasharray:4 3}
.sim .wire.wc0{stroke:var(--brown);stroke-width:1.3;opacity:.5}
.sim .wire.wc1{stroke:var(--brown);stroke-width:2.2}
.sim .wire.chg{filter:drop-shadow(0 0 3px rgba(var(--blue-rgb),.7))}
.sim .wire.wx.chg{filter:drop-shadow(0 0 3px rgba(var(--amber-rgb),.8))}
.sim .wire.wc0.chg,.sim .wire.wc1.chg{filter:none}
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
// LG 는 신호 이름을 적는 왼쪽 여백의 하한이다. 긴 이름은 여백을 넘겨 음수 x 로 나가고
// verify 의 SVG 넘침 검사에 걸리므로, 시나리오마다 제일 긴 이름에 맞춰 늘린다.
const CW = 30, RH = 28, LG = 68, TOP = 10;

function renderWave(sc, host) {
  const N = sc.frames.length, S = sc.signals;
  const lg = Math.max(LG, 16 + 7 * Math.max(0, ...S.map(s => String(s.n).length)));
  const W = lg + N * CW + 10, H = TOP + S.length * RH + 20;
  const svg = svgEl('svg', { viewBox: `0 0 ${W} ${H}`, width: W, height: H, role: 'img',
    'aria-label': L('프레임별 신호 파형', 'signal waveform per frame') });
  host.replaceChildren(svg);

  // 사이클 눈금. 엣지 프레임마다 세로선과 번호.
  for (let i = 0; i < N; i += 2) {
    const x = lg + i * CW;
    svg.appendChild(svgEl('line', { x1: x, y1: TOP, x2: x, y2: TOP + S.length * RH, class: 'grid' }));
    svg.appendChild(svgEl('text', { x: x + CW, y: H - 6, 'text-anchor': 'middle', class: 'cyc' }, String(i / 2)));
  }

  S.forEach((s, r) => {
    const y0 = TOP + r * RH, hi = y0 + 5, lo = y0 + RH - 7;
    const bits = s.bits || 1;
    svg.appendChild(svgEl('text', { x: lg - 8, y: y0 + RH / 2 + 4, 'text-anchor': 'end',
      class: 'lab' + (s.kind === 'clk' ? ' clk' : '') }, s.n));
    const val = i => sc.frames[i].v[s.n];

    if (bits === 1) {
      let d = '', pen = false;
      for (let i = 0; i < N; i++) {
        const x = lg + i * CW, v = val(i);
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
        const x0 = lg + i * CW, x1 = lg + (j + 1) * CW, v = val(i);
        if (isXM(v)) { for (let k = i; k <= j; k++) xmCell(svg, lg + k * CW, y0, v); i = j + 1; continue; }
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
      svg.appendChild(svgEl('rect', { x: lg + i * CW + 2, y: y0 + RH - 4, width: CW - 4, height: 3, class: 'chgbar', 'data-sig': s.n, 'data-i': i }));
  });

  const cur = svgEl('rect', { x: lg, y: TOP - 2, width: CW, height: S.length * RH + 4, class: 'cur', 'data-i': 0 });
  svg.appendChild(cur);
  return i => {
    cur.setAttribute('x', lg + i * CW);
    cur.setAttribute('data-i', i);
    // 현재 칸까지의 변화만 진하게. 앞으로 올 변화는 흐리게 남겨 예고한다.
    // presentation attribute 로는 안 된다. 위 .chgbar 규칙이 이기기 때문에 인라인 스타일로 쓴다.
    svg.querySelectorAll('.chgbar').forEach(b => { b.style.opacity = Number(b.dataset.i) <= i ? '0.55' : '0.15'; });
    const box = host.getBoundingClientRect();
    const cx = lg + i * CW;
    if (cx < host.scrollLeft + lg || cx + CW > host.scrollLeft + box.width) host.scrollLeft = Math.max(0, cx - box.width / 2);
  };
}

function xmCell(svg, x, y0, v) {
  const g = svgEl('g', { class: 'xm' });
  g.appendChild(svgEl('rect', { x: x + 1, y: y0 + 4, width: CW - 2, height: RH - 10, rx: 2 }));
  g.appendChild(svgEl('text', { x: x + CW / 2, y: y0 + RH / 2 + 3, 'text-anchor': 'middle' }, v));
  svg.appendChild(g);
}

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
  // 회로 없는 시나리오도 있다. 파형만으로 충분한 카드까지 예외로 죽이지 않는다.
  if (!C) { host.replaceChildren(); return () => {}; }
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
  card.simGo = go;
  go(0);
  // 첫 그리기가 끝난 뒤에 붙인다. 망가진 시나리오가 go(0) 에서 던지고도 리스너를 남기면
  // 언어를 바꿀 때마다 그 카드가 다시 던져서 페이지 전체에 에러가 뜬다.
  window.addEventListener('langchange', () => { paintText(); renderers.forEach(r => r(i)); });
}

// ── 시작 ─────────────────────────────────────────────────────────
(function main() {
  injectCSS();
  let data = [];
  try { data = JSON.parse(document.getElementById('sim-data').textContent); } catch { data = []; }
  const byId = Object.fromEntries(data.map(s => [s.id, s]));
  // 시나리오 하나가 망가져도 거기서 멈추지 않는다. 안 잡으면 예외가 forEach 를 끊어서
  // 뒤에 오는 멀쩡한 카드까지 전부 빈 상자로 남는다. 망가진 카드만 대체 문구로 끝낸다.
  document.querySelectorAll('.sim[data-sim]').forEach(card => {
    try { mount(card, byId[card.dataset.sim]); }
    catch (e) {
      console.error(`sim.js: "${card.dataset.sim}" 시나리오를 그리지 못했다`, e);
      card.replaceChildren();
      card.appendChild(el('p', { class: 'sim-fail' }, L('시뮬레이션을 못 불러왔다', 'simulation failed to load')));
    }
  });
})();
