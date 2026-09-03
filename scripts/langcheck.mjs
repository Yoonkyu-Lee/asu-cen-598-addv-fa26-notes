// 영어 모드로 바꾼 뒤 lang="ko" 조상이 없는데 한글이 남아 있는 요소를 찾는다.
// 번역 누락은 눈으로 못 잡는다.
//
// 주의 두 가지 (CLAUDE.md 참조):
//  - <html lang="ko"> 때문에 closest('[lang="ko"]') 가 모든 요소에서 참이 된다. 루트를 제외한다.
//  - SVG 요소에는 offsetParent 가 없다. 가시성은 계산된 display 로 판정한다.
//
// 사용법: node scripts/langcheck.mjs L04-system-verilog-for-design.html
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { extname, join } from 'node:path';
import { chromium } from 'playwright';

const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8',
  '.pdf': 'application/pdf', '.json': 'application/json', '.png': 'image/png' };

const file = process.argv[2];
if (!file) { console.error('usage: node scripts/langcheck.mjs <note.html>'); process.exit(1); }

const root = process.cwd();
const server = createServer(async (req, res) => {
  const p = join(root, decodeURIComponent(req.url.split('?')[0]));
  try {
    const buf = await readFile(p);
    res.writeHead(200, { 'content-type': MIME[extname(p)] || 'application/octet-stream' });
    res.end(buf);
  } catch { res.writeHead(404); res.end(); }
});
await new Promise(r => server.listen(0, '127.0.0.1', r));

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
await page.goto(`http://127.0.0.1:${server.address().port}/${file}`, { waitUntil: 'networkidle' });

// 실제 토글 버튼을 눌러야 langchange 이벤트가 돌아서 JS 가 찍는 문자열까지 영어가 된다.
await page.click('.lang-btn');
await page.evaluate(() => {
  document.querySelectorAll('details').forEach(d => { d.open = true; });
});
await page.waitForTimeout(400);

const bad = await page.evaluate(() => {
  const HANGUL = /[가-힣]/;
  const out = [];
  const root = document.documentElement;
  document.querySelectorAll('*').forEach(el => {
    if (el === root) return;
    // 직계 텍스트만 본다. 자식이 가진 한글은 그 자식이 보고한다.
    const own = [].filter.call(el.childNodes, n => n.nodeType === 3)
                  .map(n => n.textContent).join('').trim();
    if (!own || !HANGUL.test(own)) return;
    // lang="ko" 조상이 있으면 영어 모드에서 어차피 숨겨진다 (루트는 제외).
    let p = el;
    while (p && p !== root) { if (p.getAttribute('lang') === 'ko') return; p = p.parentElement; }
    // SVG 에는 offsetParent 가 없으므로 계산된 display 로 판정한다.
    for (let q = el; q && q !== root; q = q.parentElement) {
      if (getComputedStyle(q).display === 'none') return;
    }
    // 토글 버튼 자체는 일부러 한국어다 (누르면 한국어로 돌아간다는 뜻).
    if (el.classList.contains('lang-btn') || el.classList.contains('theme-btn')) return;
    out.push(el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.split(' ')[0] : '')
             + '  ' + own.slice(0, 70));
  });
  return out;
});

console.log(`영어 모드 번역 누락 검사: ${file}`);
if (!bad.length) console.log('[OK] 영어 모드에 남은 한글 없음');
else { console.log(`[FAIL] ${bad.length}건`); bad.forEach(b => console.log('  · ' + b)); }

await browser.close();
server.close();
process.exit(bad.length ? 1 : 0);
