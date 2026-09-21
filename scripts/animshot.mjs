// 애니메이션 슬라이더를 프레임마다 찍는다. verify.mjs 는 첫 프레임만 보므로
// 나머지 프레임의 글자 넘침과 겹침은 이걸로 눈으로 확인한다.
//
//   node scripts/animshot.mjs notes/L05-fifo-design.html            전 프레임
//   node scripts/animshot.mjs notes/L05-fifo-design.html 0,4,8      고른 프레임만
//   node scripts/animshot.mjs notes/L05-fifo-design.html 4 --en --dark --w=390
//
// exit 0 이어야 통과. 글자 겹침과 viewBox 이탈을 프레임마다 다시 잰다.
import { chromium } from 'playwright';
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { extname, basename } from 'node:path';
import { mkdirSync } from 'node:fs';

const args = process.argv.slice(2);
const file = args.find(x => !x.startsWith('-') && x.endsWith('.html'));
if (!file) { console.error('사용: node scripts/animshot.mjs <노트 파일> [프레임,쉼표] [--en] [--dark] [--w=390]'); process.exit(2); }
const frameArg = args.find(x => !x.startsWith('-') && x !== file);
const want = frameArg ? frameArg.split(',').map(Number) : null;
const EN = args.includes('--en');
const DARK = args.includes('--dark');
const WIDTH = Number((args.find(x => x.startsWith('--w=')) || '--w=1100').slice(4));
const suffix = (EN ? '-en' : '') + (DARK ? '-dark' : '') + (WIDTH !== 1100 ? `-w${WIDTH}` : '');
const stem = basename(file).replace(/\.html$/, '');
mkdirSync('shots', { recursive: true });

const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css', '.pdf': 'application/pdf', '.json': 'application/json', '.map': 'application/json' };
const site = createServer(async (req, res) => {
  const p = decodeURIComponent(req.url.split('?')[0]).replace(/^\//, '') || 'index.html';
  try {
    const buf = await readFile(p);
    res.writeHead(200, { 'Content-Type': MIME[extname(p)] || 'application/octet-stream' });
    res.end(buf);
  } catch { res.writeHead(404); res.end(); }
});
await new Promise(r => site.listen(0, '127.0.0.1', r));
const url = `http://127.0.0.1:${site.address().port}/${file.split('\\').join('/')}`;

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: WIDTH, height: 900 } });
const errs = [];
page.on('pageerror', e => errs.push(String(e)));
await page.goto(url, { waitUntil: 'networkidle' });
await page.waitForTimeout(500);
// 토글은 반드시 버튼을 눌러서 바꾼다. dataset 을 직접 건드리면 langchange 가
// 안 돌아서 JS 가 찍는 문자열이 한국어로 남는다. langcheck.mjs 와 같은 이유다.
if (EN) { await page.click('.lang-btn'); await page.waitForTimeout(200); }
if (DARK) { await page.click('.theme-btn'); await page.waitForTimeout(200); }

const figs = await page.$$('figure.anim');
console.log(`figure.anim ${figs.length}개`);
let bad = 0;
for (let i = 0; i < figs.length; i++) {
  const n = await figs[i].evaluate(f => f.querySelectorAll('.animcap[data-f]').length);
  const frames = want || [...Array(n).keys()];
  for (const f of frames) {
    if (f >= n) continue;
    await figs[i].evaluate((el, f) => {
      const r = el.querySelector('.animrange');
      r.value = String(f);
      r.dispatchEvent(new Event('input', { bubbles: true }));
    }, f);
    await page.waitForTimeout(120);
    const id = `${String(i + 1).padStart(2, '0')}-f${String(f).padStart(2, '0')}${suffix}`;
    await figs[i].screenshot({ path: `shots/${stem}-anim${id}.png` });
    // 이 프레임에서만 보이는 것들에 대해 겹침과 viewBox 이탈을 다시 잰다
    const hits = await figs[i].evaluate(el => {
      const vis = e => getComputedStyle(e).display !== 'none';
      const ov = (a, b) => a.left < b.right - 1 && b.left < a.right - 1 && a.top < b.bottom - 1 && b.top < a.bottom - 1;
      const out = { over: [], out: [] };
      el.querySelectorAll('svg').forEach(svg => {
        const vb = svg.viewBox.baseVal;
        const ts = [...svg.querySelectorAll('text')].filter(vis);
        ts.forEach(t => {
          let b; try { b = t.getBBox(); } catch { return; }
          if (!b.width && !b.height) return;
          if (b.x < vb.x - 1.5 || b.x + b.width > vb.x + vb.width + 1.5 || b.y < vb.y - 1.5 || b.y + b.height > vb.y + vb.height + 1.5)
            out.out.push((t.textContent || '').trim().slice(0, 20));
        });
        const bbs = ts.map(t => ({ b: t.getBoundingClientRect(), t: (t.textContent || '').trim().slice(0, 14) })).filter(x => x.b.width > .5);
        for (let a = 0; a < bbs.length; a++) for (let c = a + 1; c < bbs.length; c++)
          if (ov(bbs[a].b, bbs[c].b)) out.over.push(`"${bbs[a].t}" 와 "${bbs[c].t}"`);
      });
      return out;
    });
    const tag = `anim${id}`;
    if (hits.out.length) { bad++; console.log(`  [FAIL] ${tag} viewBox 이탈: ${[...new Set(hits.out)].join(', ')}`); }
    if (hits.over.length) { bad++; console.log(`  [FAIL] ${tag} 글자 겹침: ${[...new Set(hits.over)].join(', ')}`); }
  }
  console.log(`  anim${String(i + 1).padStart(2, '0')}: ${frames.length}프레임 찍음`);
}
await browser.close();
await site.close();
if (errs.length) { console.log('[FAIL] JS 에러:', errs.join(' / ')); bad++; }
console.log(bad ? `\n실패 ${bad}건` : '\n프레임 전부 통과. shots/ 의 그림을 눈으로 확인할 것.');
process.exit(bad ? 1 : 0);
