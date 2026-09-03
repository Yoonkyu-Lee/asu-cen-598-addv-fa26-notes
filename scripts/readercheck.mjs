// 노트의 섹션으로 스크롤하면서 슬라이드 리더가 실제로 그 쪽으로 따라오는지 확인한다.
// verify.mjs 는 리더가 뜨는지와 앵커 개수만 보므로, 어느 섹션이 어느 쪽을 가리키는지는 이걸로 본다.
//
// 사용법: node scripts/readercheck.mjs L04-system-verilog-for-design.html s0,s3,s9,s18
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { extname, join } from 'node:path';
import { chromium } from 'playwright';

const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8',
  '.pdf': 'application/pdf', '.json': 'application/json', '.png': 'image/png' };

const file = process.argv[2];
const ids = (process.argv[3] || '').split(',').filter(Boolean);
if (!file || !ids.length) { console.error('usage: node scripts/readercheck.mjs <note.html> <id,id,...>'); process.exit(1); }

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
const port = server.address().port;

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1600, height: 950 } });
await page.goto(`http://127.0.0.1:${port}/${file}`, { waitUntil: 'networkidle' });
await page.waitForTimeout(1500);

for (const id of ids) {
  await page.evaluate(i => document.getElementById(i)?.scrollIntoView(), id);
  await page.waitForTimeout(900);
  const info = await page.evaluate(i => {
    const el = document.getElementById(i);
    const head = el?.querySelector('.sec-head');
    const want = head?.getAttribute('data-slide') || '(앵커 없음)';
    const aside = document.querySelector('aside');
    const shown = aside ? aside.innerText.split('\n').filter(Boolean).slice(0, 2).join(' / ') : '(리더 없음)';
    const title = el?.querySelector('h2')?.textContent || i;
    return { want, shown, title };
  }, id);
  console.log(`${id.padEnd(5)} ${info.title.slice(0, 28).padEnd(30)} data-slide=${String(info.want).padEnd(8)} 리더: ${info.shown}`);
}

await browser.close();
server.close();
