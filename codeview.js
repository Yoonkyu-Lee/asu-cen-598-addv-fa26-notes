// codeview.js · 접히는 파일 트리와 diff / 원문 뷰어.
//
// Lab 기록 페이지가 코드 "내용" 을 줄 단위로 설명할 때 쓴다. 왼쪽은 접히는 트리
// (파일, 모듈 계층, 코드 윤곽, 커밋), 오른쪽은 선택한 파일의 diff 또는 원문과
// 설명 카드다. 설명 카드는 그 블록 바로 앞에 끼운다. 설명을 먼저 읽고 코드를 본다.
//
// 데이터는 페이지 안 <script type="application/json" id="cv-data"> 에 있고
// .cv[data-cv="id"] 카드가 부른다. 형식은 write-lab-note 스킬이 단일 출처다.
// 이 파일이 없거나 실패해도 본문은 읽힌다. 카드 안의 정적 안내가 그대로 남는다.
//
// reader.js · sim.js · anim.js 와 같은 로컬 예외다. 외부에서 아무것도 받지 않는다.
// 브라우저 저장소를 쓰지 않는다. 상태는 전부 JS 변수다.

const CSS = `
.cv{border:1px solid var(--rule);border-radius:10px;background:var(--card);margin:26px 0;overflow:hidden}
.cv-top{display:flex;flex-wrap:wrap;align-items:center;gap:8px;padding:10px 14px;border-bottom:1px solid var(--rule);background:var(--paper)}
.cv-title{font-family:var(--mono);font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink3);margin-right:auto}
.cv-top button,.cv-tabs button,.cv-links button{font-family:var(--mono);font-size:11px;padding:5px 9px;background:var(--card);border:1px solid var(--rule);border-radius:5px;color:var(--ink2);cursor:pointer}
.cv-top button:hover,.cv-tabs button:hover,.cv-links button:hover{border-color:var(--sel);color:var(--sel)}
.cv-tabs button.on{border-color:var(--sel);color:var(--sel);background:var(--sel-soft)}
.cv-body{display:grid;grid-template-columns:minmax(0,230px) minmax(0,1fr)}
.cv-side{border-right:1px solid var(--rule);padding:10px 6px 12px;max-height:78vh;overflow:auto;background:var(--paper)}
.cv-tabs{display:flex;flex-wrap:wrap;gap:5px;padding:0 6px 10px}
.cv-tree,.cv-tree ul{list-style:none;margin:0;padding:0}
.cv-tree ul{padding-left:14px;border-left:1px dashed var(--rule);margin-left:9px}
.cv-tree li{margin:1px 0}
.cv-node{display:flex;align-items:flex-start;gap:2px}
.cv-caret{flex:none;width:18px;height:22px;border:0;background:none;color:var(--ink3);cursor:pointer;font-size:10px;padding:0}
.cv-caret.none{visibility:hidden}
.cv-lab{flex:1;min-width:0;text-align:left;border:0;background:none;padding:3px 6px;border-radius:5px;font-family:var(--mono);font-size:11.5px;color:var(--ink2);cursor:pointer;line-height:1.45;word-break:break-word}
.cv-lab:hover{background:var(--sel-soft);color:var(--ink)}
.cv-lab.on{background:var(--sel-soft);color:var(--sel);font-weight:700}
.cv-lab .b{font-size:10px;color:var(--ink3);margin-left:5px;font-weight:400}
.cv-main{min-width:0;display:flex;flex-direction:column}
.cv-head{padding:12px 16px 10px;border-bottom:1px solid var(--rule)}
.cv-path{font-family:var(--mono);font-size:13px;font-weight:700;color:var(--ink);word-break:break-all}
.cv-from{font-family:var(--mono);font-size:11px;color:var(--ink3);margin-top:3px;word-break:break-all}
.cv-stat{font-family:var(--mono);font-size:11px;margin-top:4px;color:var(--ink3)}
.cv-stat .p{color:var(--blue)}.cv-stat .m{color:var(--ink3)}
.cv-sum{font-size:14px;line-height:1.7;color:var(--ink2);margin-top:8px}
.cv-links{display:flex;flex-wrap:wrap;gap:5px;margin-top:9px}
.cv-links button.on{border-color:var(--sel);color:var(--sel);background:var(--sel-soft)}
.cv-sub{margin-top:12px;padding-top:10px;border-top:1px dashed var(--rule)}
.cv-code{max-height:78vh;overflow:auto;font-family:var(--mono);font-size:12.5px;line-height:1.55;background:var(--code-bg)}
.cv-row{display:grid;grid-template-columns:40px 40px 16px max-content;min-width:100%}
.cv.file .cv-row{grid-template-columns:44px max-content}
.cv.file .cv-o,.cv.file .cv-s{display:none}
.cv-o,.cv-n{color:var(--ink3);text-align:right;padding-right:8px;user-select:none;font-size:11px;padding-top:1px}
.cv-s{color:var(--ink3);user-select:none;text-align:center}
.cv-t{white-space:pre;padding-right:18px;color:var(--ink)}
.cv-row.add{background:rgba(var(--blue-rgb),.10)}
.cv-row.add .cv-s{color:var(--blue)}
.cv.rv .cv-row.add{background:rgba(var(--pink-rgb),.10)}
.cv.rv .cv-row.add .cv-s{color:var(--pink)}
.cv.rt .cv-row.add{background:rgba(var(--violet-rgb),.10)}
.cv.rt .cv-row.add .cv-s{color:var(--violet)}
.cv-row.del{background:rgba(var(--ink-rgb),.05)}
.cv-row.del .cv-t{color:var(--ink3)}
.cv-row.hit{background:var(--sel-soft)!important}
.cv-t .k{color:var(--violet);font-weight:600}
.cv-t .s{color:var(--green-deep)}
.cv-t .c{color:var(--ink3);font-style:italic}
.cv-t .n{color:var(--brown)}
.cv-note{margin:8px 14px 8px 12px;padding:10px 14px;background:var(--card);border:1px solid var(--rule);border-left:3px solid var(--blue);border-radius:0 7px 7px 0;font-family:var(--sans);font-size:13.5px;line-height:1.65;color:var(--ink2);white-space:normal;position:sticky;left:12px;max-width:min(720px,calc(100% - 28px))}
.cv.rv .cv-note{border-left-color:var(--pink)}
.cv.rt .cv-note{border-left-color:var(--violet)}
.cv-note code{font-family:var(--mono);font-size:12px;background:var(--chip);padding:1px 4px;border-radius:3px}
.cv.nonotes .cv-note{display:none}
.cv-fold{display:block;width:100%;text-align:left;border:0;border-top:1px dashed var(--rule);border-bottom:1px dashed var(--rule);background:var(--paper);color:var(--ink3);font-family:var(--mono);font-size:11px;padding:4px 16px;cursor:pointer}
.cv-fold:hover{color:var(--sel)}
.cv-empty{padding:18px 16px;color:var(--ink3);font-size:13.5px}
.cv-go{font-family:var(--mono);font-size:11.5px;padding:2px 8px;margin:0 2px;background:var(--card);border:1px solid var(--rule);border-radius:5px;color:var(--sel);cursor:pointer;vertical-align:1px}
.cv-go:hover{border-color:var(--sel);background:var(--sel-soft)}
@media(max-width:760px){
  .cv-body{grid-template-columns:minmax(0,1fr)}
  .cv-side{border-right:0;border-bottom:1px solid var(--rule);max-height:230px}
  .cv-code{max-height:70vh}
}
`;

const SV_KW = new Set(('module endmodule input output inout logic wire reg bit int integer time string parameter localparam ' +
  'assign always always_ff always_comb always_latch begin end if else case endcase unique priority default for while repeat ' +
  'forever fork join join_any join_none initial task endtask function endfunction automatic return typedef enum struct packed ' +
  'interface endinterface modport posedge negedge or and not wait void ifdef ifndef define endif else genvar generate endgenerate').split(' '));

const lang = () => (document.documentElement.dataset.lang === 'en' ? 'en' : 'ko');
const L = (o) => (o == null ? '' : typeof o === 'string' ? o : (o[lang()] != null ? o[lang()] : o.ko));
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

function injectCSS() {
  if (document.getElementById('cv-css')) return;
  const s = document.createElement('style');
  s.id = 'cv-css';
  s.textContent = CSS;
  document.head.appendChild(s);
}

// 한 줄 하이라이팅. 칠하는 것은 키워드 · 문자열 · 주석 · 숫자 넷뿐이다 (note-html 규칙).
function hlSV(line) {
  let out = '', i = 0;
  const n = line.length;
  while (i < n) {
    const c = line[i];
    if (c === '/' && line[i + 1] === '/') { out += '<span class="c">' + esc(line.slice(i)) + '</span>'; break; }
    if (c === '"') {
      let j = i + 1;
      while (j < n && line[j] !== '"') { if (line[j] === '\\') j++; j++; }
      out += '<span class="s">' + esc(line.slice(i, j + 1)) + '</span>'; i = j + 1; continue;
    }
    if (c === '$' || c === '`') {
      let j = i + 1;
      while (j < n && /[\w$]/.test(line[j])) j++;
      out += '<span class="k">' + esc(line.slice(i, j)) + '</span>'; i = j; continue;
    }
    if (/[0-9']/.test(c) && !/[\w]/.test(line[i - 1] || '')) {
      const m = /^(\d*'[sS]?[bBoOdDhH]?[0-9a-fA-FxXzZ_]+|'[01xz]|\d+(\.\d+)?)/.exec(line.slice(i));
      if (m) { out += '<span class="n">' + esc(m[0]) + '</span>'; i += m[0].length; continue; }
    }
    if (/[A-Za-z_]/.test(c)) {
      let j = i + 1;
      while (j < n && /[\w]/.test(line[j])) j++;
      const w = line.slice(i, j);
      out += SV_KW.has(w) ? '<span class="k">' + w + '</span>' : esc(w); i = j; continue;
    }
    out += esc(c); i++;
  }
  return out;
}

function hlShell(line) {
  const t = line.replace(/^\s*/, '');
  if (t.startsWith('#')) return '<span class="c">' + esc(line) + '</span>';
  return esc(line)
    .replace(/(\$\$?\([^)]*\)|\$\w+)/g, '<span class="n">$1</span>')
    .replace(/^([\w.\-$()]+)(\s*[:?]?=)/, '<span class="k">$1</span>$2')
    .replace(/^([\w.\-$()]+):(?!=)/, '<span class="k">$1</span>:')
    .replace(/^(export|setenv)\b/, '<span class="k">$1</span>');
}

function hl(path, text) {
  return /\.(sv|v|svh)$/.test(path) ? hlSV(text) : hlShell(text);
}

function el(tag, cls, html) {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (html != null) n.innerHTML = html;
  return n;
}

const LBL = {
  notesOff: { ko: '설명 숨기기', en: 'hide notes' },
  notesOn: { ko: '설명 보이기', en: 'show notes' },
  expand: { ko: '접힌 줄 모두 펼치기', en: 'expand all' },
  collapse: { ko: '다시 접기', en: 'fold again' },
  folded: { ko: '줄 접힘. 눌러서 펼치기', en: 'lines folded, click to expand' },
  from: { ko: '출발점', en: 'from' },
  newf: { ko: '새 파일', en: 'new file' },
  pick: { ko: '왼쪽에서 파일을 고르자.', en: 'Pick a file on the left.' },
  files: { ko: '이 커밋이 바꾼 파일', en: 'files in this commit' },
  noCode: { ko: '코드 변화 없음. 주석이나 문서만 바뀌었다.', en: 'No code change: only comments or documents.' }
};

const PROV = {
  lift: { ko: '논문을 문법만 올림', en: 'syntax lifted' },
  extend: { ko: '논문에 설계를 얹음', en: 'design added' },
  add: { ko: '새로 씀', en: 'written new' }
};

class Viewer {
  constructor(host, data, id) {
    this.host = host; this.d = data; this.id = id;
    this.tree = 0; this.key = data.start || null; this.at = null;
    this.notes = true; this.expanded = false;
    this.openSet = new Set();
    this.seedOpen(data.trees);
    this.render();
  }

  seedOpen(trees) {
    const walk = (nodes, path) => nodes.forEach((n, i) => {
      const p = path + '/' + i;
      if (n.open !== false && n.kids) this.openSet.add(p);
      if (n.kids) walk(n.kids, p);
    });
    trees.forEach((t, ti) => walk(t.nodes, 't' + ti));
  }

  render() {
    const d = this.d, f = this.key ? d.files[this.key] : null;
    const role = f ? f.role : 'd';
    this.host.className = 'cv' + (d.mode === 'file' ? ' file' : '') + (role === 'v' ? ' rv' : role === 't' ? ' rt' : '') + (this.notes ? '' : ' nonotes');
    this.host.replaceChildren();

    const top = el('div', 'cv-top');
    top.appendChild(el('div', 'cv-title', esc(L(d.title))));
    const bn = el('button', null, esc(L(this.notes ? LBL.notesOff : LBL.notesOn)));
    bn.type = 'button';
    bn.onclick = () => { this.notes = !this.notes; this.render(); };
    top.appendChild(bn);
    const be = el('button', null, esc(L(this.expanded ? LBL.collapse : LBL.expand)));
    be.type = 'button';
    be.onclick = () => { this.expanded = !this.expanded; this.render(); };
    top.appendChild(be);
    this.host.appendChild(top);

    const body = el('div', 'cv-body');
    body.appendChild(this.renderSide());
    body.appendChild(this.renderMain(f));
    this.host.appendChild(body);

    if (this.at != null) {
      const hit = this.host.querySelector('.cv-row.hit');
      if (hit) {
        // 그 줄의 설명 카드가 있으면 카드부터 보이게 한다
        const prev = hit.previousElementSibling;
        const top = prev && prev.classList.contains('cv-note') ? prev : hit;
        const box = this.host.querySelector('.cv-code');
        box.scrollTop = Math.max(0, top.offsetTop - box.offsetTop - 16);
      }
    }
  }

  renderSide() {
    const side = el('div', 'cv-side');
    const trees = this.d.trees;
    if (trees.length > 1) {
      const tabs = el('div', 'cv-tabs');
      trees.forEach((t, i) => {
        const b = el('button', i === this.tree ? 'on' : null, esc(L(t.name)));
        b.type = 'button';
        b.onclick = () => { this.tree = i; this.render(); };
        tabs.appendChild(b);
      });
      side.appendChild(tabs);
    }
    const ul = el('ul', 'cv-tree');
    this.renderNodes(ul, trees[this.tree].nodes, 't' + this.tree);
    side.appendChild(ul);
    return side;
  }

  renderNodes(ul, nodes, path) {
    nodes.forEach((n, i) => {
      const p = path + '/' + i;
      const li = el('li');
      const row = el('div', 'cv-node');
      const kids = n.kids && n.kids.length;
      const open = this.openSet.has(p);
      const caret = el('button', 'cv-caret' + (kids ? '' : ' none'), kids ? (open ? '▾' : '▸') : '');
      caret.type = 'button';
      caret.setAttribute('aria-label', open ? 'collapse' : 'expand');
      caret.onclick = () => { if (open) this.openSet.delete(p); else this.openSet.add(p); this.render(); };
      row.appendChild(caret);
      const on = n.file && n.file === this.key && (n.at == null ? this.at == null : n.at === this.at);
      const lab = el('button', 'cv-lab' + (on ? ' on' : ''), esc(L(n.label)) + (n.badge ? '<span class="b">' + esc(L(n.badge)) + '</span>' : ''));
      lab.type = 'button';
      lab.onclick = () => {
        if (n.file) { this.key = n.file; this.at = n.at != null ? n.at : null; this.expanded = this.expanded && this.at == null; }
        if (kids && !n.file) { if (open) this.openSet.delete(p); else this.openSet.add(p); }
        else if (kids) this.openSet.add(p);
        this.render();
      };
      row.appendChild(lab);
      li.appendChild(row);
      if (kids && open) {
        const sub = el('ul');
        this.renderNodes(sub, n.kids, p);
        li.appendChild(sub);
      }
      ul.appendChild(li);
    });
  }

  renderMain(f) {
    const main = el('div', 'cv-main');
    if (!f) { main.appendChild(el('div', 'cv-empty', esc(L(LBL.pick)))); return main; }
    // 커밋을 고르면 요약과 함께 그 커밋의 첫 파일 diff 를 바로 보인다. 파일을 고르면 위에 커밋 요약이 남는다.
    let c = null, cur = null;
    if (f.kind === 'commit') { c = f; cur = f.links && f.links.length ? f.links[0] : null; f = cur ? this.d.files[cur] : null; }
    else if (f.ck) { c = this.d.files[f.ck]; cur = this.key; }
    const head = el('div', 'cv-head');
    if (c) {
      head.appendChild(el('div', 'cv-path', esc(c.meta.hash + '  ' + c.meta.subject)));
      head.appendChild(el('div', 'cv-from', esc(c.meta.date)));
      if (c.sum) head.appendChild(el('div', 'cv-sum', L(c.sum)));
      if (c.links && c.links.length) {
        head.appendChild(el('div', 'cv-stat', esc(L(LBL.files))));
        const box = el('div', 'cv-links');
        c.links.forEach(k => {
          const g = this.d.files[k];
          const b = el('button', k === cur ? 'on' : null, esc(g.path));
          b.type = 'button';
          b.onclick = () => { this.key = k; this.at = null; this.render(); };
          box.appendChild(b);
        });
        head.appendChild(box);
      } else {
        head.appendChild(el('div', 'cv-stat', esc(L(LBL.noCode))));
      }
    }
    if (f) {
      const fh = c ? el('div', 'cv-sub') : head;
      fh.appendChild(el('div', 'cv-path', esc(f.path)));
      if (f.from) fh.appendChild(el('div', 'cv-from', esc(L(LBL.from)) + ': ' + esc(f.from)));
      else if (f.isnew) fh.appendChild(el('div', 'cv-from', esc(L(LBL.newf))));
      if (this.d.mode !== 'file') {
        const a = f.rows.filter(r => r[0] === '+').length, m = f.rows.filter(r => r[0] === '-').length;
        const pv = f.prov ? ' · ' + esc(L(PROV[f.prov])) : '';
        if (a || m) fh.appendChild(el('div', 'cv-stat', '<span class="p">+' + a + '</span> <span class="m">−' + m + '</span>' + pv));
      } else if (f.prov) {
        fh.appendChild(el('div', 'cv-stat', esc(L(PROV[f.prov]))));
      }
      if (f.sum) fh.appendChild(el('div', 'cv-sum', L(f.sum)));
      if (c) head.appendChild(fh);
    }
    main.appendChild(head);
    if (f && f.rows && f.rows.length) main.appendChild(this.renderCode(f));
    return main;
  }

  renderCode(f) {
    const box = el('div', 'cv-code');
    const rows = f.rows, notes = f.notes || {};
    const N = rows.length, M = 3, FOLD = 12;
    const keep = new Array(N).fill(false);
    const mark = (i) => { for (let k = Math.max(0, i - M); k <= Math.min(N - 1, i + M); k++) keep[k] = true; };
    rows.forEach((r, i) => { if (r[0] !== ' ') mark(i); });
    Object.keys(notes).forEach(k => { const i = +k; for (let j = i; j <= Math.min(N - 1, i + 14); j++) keep[j] = true; mark(i); });
    if (this.at != null) for (let j = this.at; j <= Math.min(N - 1, this.at + 20); j++) keep[j] = true;
    if (this.d.mode === 'file' && !Object.keys(notes).length) keep.fill(true);

    const makeRow = (r, i) => {
      const cls = 'cv-row' + (r[0] === '+' ? ' add' : r[0] === '-' ? ' del' : '') + (this.at === i ? ' hit' : '');
      const row = el('div', cls);
      row.appendChild(el('span', 'cv-o', r[1] == null ? '' : String(r[1])));
      row.appendChild(el('span', 'cv-n', r[2] == null ? '' : String(r[2])));
      row.appendChild(el('span', 'cv-s', r[0] === '+' ? '+' : r[0] === '-' ? '−' : ''));
      row.appendChild(el('span', 'cv-t', hl(f.path, r[3]) || ' '));
      return row;
    };
    const addRow = (r, i) => {
      if (notes[i] && this.notes) box.appendChild(el('div', 'cv-note', L(notes[i])));
      box.appendChild(makeRow(r, i));
    };

    // 설명이 붙은 블록과 바뀐 줄 근처는 늘 보이고, 그 밖의 긴 구간만 접는다.
    let i = 0;
    while (i < N) {
      if (this.expanded || keep[i] || notes[i]) { addRow(rows[i], i); i++; continue; }
      let j = i;
      while (j < N && !keep[j] && !notes[j]) j++;
      if (j - i < FOLD) {
        for (let k = i; k < j; k++) addRow(rows[k], k);
      } else {
        const b = el('button', 'cv-fold', '⋯ ' + (j - i) + ' ' + esc(L(LBL.folded)));
        b.type = 'button';
        const a0 = i, a1 = j;
        b.onclick = () => {
          const frag = document.createDocumentFragment();
          for (let k = a0; k < a1; k++) frag.appendChild(makeRow(rows[k], k));
          box.insertBefore(frag, b);
          b.remove();
        };
        box.appendChild(b);
      }
      i = j;
    }
    return box;
  }

  open(key, at) {
    const f = this.d.files[key];
    if (!f) return;
    if (typeof at === 'string' && at !== '') {
      const i = f.rows ? f.rows.findIndex(r => r[0] !== '-' && r[3].includes(at)) : -1;
      at = /^\d+$/.test(at) ? +at : (i >= 0 ? i : null);
    } else if (at === '') at = null;
    this.key = key; this.at = at != null ? at : null;
    this.render();
    this.host.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

const viewers = {};

function boot() {
  const src = document.getElementById('cv-data');
  if (!src) return;
  let data;
  try { data = JSON.parse(src.textContent); } catch (e) { console.error('codeview: bad cv-data', e); return; }
  injectCSS();
  document.querySelectorAll('.cv[data-cv]').forEach(host => {
    const id = host.dataset.cv;
    if (!data[id]) { console.error('codeview: no data for', id); return; }
    viewers[id] = new Viewer(host, data[id], id);
  });
  window.addEventListener('langchange', () => Object.values(viewers).forEach(v => v.render()));
}

// 다른 스크립트(파일 지도 위젯)가 특정 파일을 열게 한다. at 은 행 번호거나 그 줄에 든 글자다.
window.cvOpen = (id, key, at) => { if (viewers[id]) viewers[id].open(key, at); };

// 본문의 <button class="cv-go" data-cv="p1" data-key="fifo_wptr" data-at="wused_next"> 가
// 해당 뷰어의 그 줄로 데려간다. 본문이 코드를 다시 베끼지 않고 가리키게 하려는 것이다.
document.addEventListener('click', (e) => {
  const b = e.target.closest && e.target.closest('.cv-go');
  if (!b) return;
  e.preventDefault();
  window.cvOpen(b.dataset.cv, b.dataset.key, b.dataset.at);
});

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
else boot();
