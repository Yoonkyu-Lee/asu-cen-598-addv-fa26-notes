// scripts/articulate-step.js
// browse eval 로 Articulate 플레이어의 `sco` 프레임 안에서 돈다.
// 목차 항목을 하나 클릭한 뒤 이 파일을 돌리고, 그 다음에 스크린샷을 찍는다.
//
// 하는 일: 슬라이드를 타임라인 끝으로 밀어서 **다 그려진 상태**로 만들고, 그 판정 근거를 돌려준다.
// 왜 필요한가: 슬라이드의 오브젝트는 나레이션 타임라인을 따라 하나씩 쌓인다.
//   목차만 클릭하고 바로 찍으면 백지이거나 bullet 한 줄이다. 실제로 그렇게 80 장 중 52 장을 날렸다.
//
// **클래식과 HTML5 를 자동 판별한다.** 둘은 seek 단위도 끝 신호도 다르다.
//
//   | | 클래식 (index_lms.html) | HTML5 (index_lms_html5.html) |
//   |---|---|---|
//   | seek input | aria-label="slide progress", max 가 ms (예: 26000) | aria-label="Seekbar", max 가 1 |
//   | 끝 신호 | `#play-pause svg` 의 id 가 `icon-play` | `.cs-seekcontrol` 첫 버튼 텍스트가 `play` |
//   | 완료 판정 | seek 이 max 에 닿았는가 (본문 텍스트가 접근성용과 중복돼 못 센다) | renderedLen / bodyLen |
//
// `await` 가 있으므로 browse 가 async 로 감싼다. top-level return 이 필요하다.

const sleep = ms => new Promise(r => setTimeout(r, ms));
const q = s => document.querySelector(s);

const isClassic = () => /index_lms\.html/.test(location.href) || !!q('#play-pause');

// 화면에 실제로 그려질 수 있는 글자 수. hidden 레이어(Notes, 대체 상태)는 뺀다.
const shownLen = () => [...document.querySelectorAll('.slide .slide-layer')]
  .filter(l => !/(^|\s)hidden(\s|$)/.test(l.className))
  .reduce((n, l) => n + l.textContent.length, 0);

// 끝났는가. 클래식은 아이콘, HTML5 는 버튼 텍스트다.
const ended = () => {
  if (isClassic()) {
    const icon = q('#play-pause svg');
    return !!icon && /icon-play/.test(icon.id || '');
  }
  const b = q('.cs-seekcontrol button');
  return !!b && /^play$/i.test((b.textContent || '').trim());
};

// 볼륨 슬라이더도 range 라 type 만으로 고르면 그걸 집는다. aria-label 로 거른다.
const seekInput = () => [...document.querySelectorAll('input[type=range]')]
  .find(i => /seek|slide progress/i.test(i.getAttribute('aria-label') || ''));

// __seekTo 는 항상 0..1 의 비율이다. 실제 값은 플레이어의 max 단위로 환산한다.
// 끝까지(1.0) 밀면 자동 진행이 켜진 슬라이드는 그대로 다음 장으로 넘어간다.
// 드라이버가 어긋남을 보면 __seekTo 를 낮춰서 다시 부른다.
const pushToEnd = inp => {
  const frac = Number(window.__seekTo === undefined ? 0.999 : window.__seekTo);
  const max = Number(inp.max || 1) || 1;
  const step = Number(inp.step || 0) || 0;
  const to = max <= 1
    ? String(frac)                                              // HTML5. max 가 1 이다
    : String(Math.min(Math.round(frac * max), max - (step || 100)));  // 클래식. ms 다
  const setV = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
  setV.call(inp, to);
  ['input', 'change'].forEach(t => inp.dispatchEvent(new Event(t, { bubbles: true })));
  return to;
};

// 지금까지 그려진 양. 오브젝트 수와 글자 수를 같이 본다. 둘 중 하나만 움직이는 슬라이드가 있다.
const drawn = () => document.querySelectorAll('.slide .slide-object.shown').length * 10000
  + (q('.slide') ? q('.slide').innerText.length : 0);

// 지금 선택된 목차 항목이 몇 번째인가. 드라이버가 원한 index 와 다르면 그 shot 은 엉뚱한 슬라이드다.
const selectedIdx = () => {
  const items = [...document.querySelectorAll('.cs-outline .cs-listitem')];
  return items.findIndex(e => /(^|\s)cs-selected(\s|$)/.test(e.className));
};

const t0 = Date.now();
const CAP = 45000;
const classic = isClassic();

let s = q('.slide');
for (let i = 0; i < 40 && !s; i++) { await sleep(250); s = q('.slide'); }
if (!s) { return JSON.stringify({ stable: false, why: 'no .slide' }); }

let last = -1, same = 0, seeks = 0, sentTo = null;
let advanced = false, settled = false;

if (classic) {
  // **클래식은 타임라인 끝에 닿으면 무조건 다음 장으로 자동 진행한다.**
  // 그래서 ended 를 기다리면 안 된다. 기다리면 덱을 끝까지 걸어간다 (실측: 3 번에서 12 번까지 11 초).
  // 한 번만 밀고 바로 돌려준다. 드라이버가 어긋남을 보면 목표를 낮춰 다시 부른다.
  // 클릭 직후에는 아직 **이전 슬라이드**의 seek input 이다. 거기 밀면 그 장이 끝나 버린다.
  // 새 슬라이드가 자리를 잡을 때까지 기다렸다 민다. (실측: 이걸 안 하면 섹션 첫 장이 매번 실패)
  await sleep(700);
  const inp = seekInput();
  const maySeek = (window.__seekTo === undefined) || Number(window.__seekTo) > 0;
  if (inp && maySeek) { sentTo = pushToEnd(inp); seeks = 1; }

  // 다 그려졌는지는 **시계가 아니라 그리기 진행도**로 본다.
  // 시계로 보면 목표를 낮췄을 때 영영 통과 못 하는 모순이 생긴다.
  // 그리는 중에 자동 진행으로 다음 장에 넘어가면 그 자리에서 실패로 끝낸다.
  const idx0 = selectedIdx();
  let prev = -1, still = 0;
  for (let k = 0; k < 14; k++) {
    await sleep(250);
    if (selectedIdx() !== idx0) { advanced = true; break; }
    const n = drawn();
    if (n === prev) { if (++still >= 2) break; } else { still = 0; prev = n; }
  }
  settled = !advanced && still >= 2;
} else {
  while (Date.now() - t0 < CAP) {
    const inp = seekInput();
    const n = q('.slide').innerText.length;
    if (n === last) { same++; } else { same = 0; last = n; }
    if (ended() && same >= 1) break;
    // __seekTo 가 0 이면 밀지 않는다. 짧은 타이틀 슬라이드는 어디로 밀어도 자동 진행으로 넘어간다.
    const maySeek = (window.__seekTo === undefined) || Number(window.__seekTo) > 0;
    if (inp && maySeek && !ended() && (seeks === 0 || same >= 3)) { sentTo = pushToEnd(inp); seeks++; same = 0; }
    if (inp && !maySeek && same >= 6) break;
    // 퀴즈 슬라이드처럼 seekbar 가 없는 것은 안정되면 끝난 것으로 본다.
    if (!inp && same >= 6) break;
    await sleep(400);
  }
}

s = q('.slide');
const sel = q('.cs-outline .cs-selected');
const body = shownLen();
const rendered = s.innerText.length;
const inp = seekInput();
const seek = inp ? { value: inp.value, max: inp.max || '1' } : null;
const seekRatio = (seek && Number(seek.max)) ? Number(seek.value) / Number(seek.max) : null;

// 클래식은 본문 텍스트가 시각용/접근성용 두 벌이라 renderedLen 과 bodyLen 을 못 비교한다.
// 대신 타임라인이 끝에 닿았는지로 본다.
const stable = classic
  ? settled
  : (body === 0 ? true : rendered >= body * 0.95);

return JSON.stringify({
  player: classic ? 'classic' : 'html5',
  stable,
  advanced,
  ended: ended(),
  seeks,
  seekTo: window.__seekTo === undefined ? 0.999 : window.__seekTo,
  sentTo,
  seek,
  waited: Date.now() - t0,
  renderedLen: rendered,
  bodyLen: body,
  notesLen: s.textContent.length - body,
  selectedIdx: selectedIdx(),
  selected: sel ? sel.innerText.trim() : null
});
