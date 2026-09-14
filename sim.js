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
