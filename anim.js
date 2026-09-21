// 애니메이션 슬라이더. 강의 덱이 같은 그림을 여러 장에 걸쳐 움직이는 구간을,
// 노트 안에서 독자가 직접 앞뒤로 밟아보게 한다. 슬라이드를 한 장씩 넘겨야
// 보이던 것을 한 자리에서 끝까지 돌려볼 수 있게 하는 것이 목적이다.
//
// 마크업 규약 (note-html 스킬의 "애니메이션 슬라이더" 절이 단일 출처):
//
//   <figure class="anim">
//     <svg viewBox="…" role="img" aria-label="…">
//       <g data-f="0 1 2">…</g>          data-f 가 없으면 항상 보이는 뼈대
//     </svg>
//     <div class="animcap" data-f="0" data-src="7">
//       <span lang="ko">…</span><span lang="en">…</span>
//     </div>
//     …프레임 수만큼…
//     <figcaption>…</figcaption>
//   </figure>
//
// data-f 는 "그 요소가 보이는 프레임 번호 목록"이다. 범위 표기가 아니라
// 공백으로 나열한다. CSS 의 [data-f~="0"] 가 스크립트 없이도 첫 프레임을
// 띄우려면 이 형태여야 한다.
//
// 프레임 개수는 .animcap 의 개수로 정한다. 그림에만 있고 설명이 없는
// 프레임은 없어야 한다는 뜻이고, 이건 의도한 제약이다.
//
// 상태는 전부 JS 변수로만 들고 브라우저 저장소를 쓰지 않는다.
// 이 파일이 없거나 로드에 실패해도 노트 본문은 그대로 읽힌다.
// 그 경우 첫 프레임이 보이고 조작 막대가 없다.

(function () {
  'use strict';

  var STEP_MS = 1400;

  function L(ko, en) {
    return document.documentElement.dataset.lang === 'en' ? en : ko;
  }

  function frameList(el) {
    return (el.getAttribute('data-f') || '').trim().split(/\s+/);
  }

  function init(fig) {
    var caps = [].slice.call(fig.querySelectorAll('.animcap[data-f]'));
    if (caps.length < 2) return;

    var keyed = [].slice.call(fig.querySelectorAll('[data-f]'));
    var svg = fig.querySelector('svg');
    var n = caps.length;
    var at = 0;
    var timer = null;

    fig.classList.add('js-anim');

    // ── 조작 막대 ──────────────────────────────────────────────
    // 스크립트가 직접 만든다. 이 파일이 없으면 막대도 없어서,
    // 눌러도 아무 일 없는 버튼이 남지 않는다.
    var bar = document.createElement('div');
    bar.className = 'animbar';

    function mkBtn(cls) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = cls;
      bar.appendChild(b);
      return b;
    }

    var prev = mkBtn('animprev');
    var play = mkBtn('animplay');
    var next = mkBtn('animnext');

    var range = document.createElement('input');
    range.type = 'range';
    range.min = '0';
    range.max = String(n - 1);
    range.step = '1';
    range.value = '0';
    range.className = 'animrange';
    bar.appendChild(range);

    var step = document.createElement('span');
    step.className = 'animstep';
    bar.appendChild(step);

    if (svg && svg.nextSibling) svg.parentNode.insertBefore(bar, svg.nextSibling);
    else fig.appendChild(bar);

    // ── 프레임 전환 ────────────────────────────────────────────
    function show(i) {
      at = Math.max(0, Math.min(n - 1, i));
      for (var k = 0; k < keyed.length; k++) {
        var on = frameList(keyed[k]).indexOf(String(at)) !== -1;
        keyed[k].classList.toggle('on', on);
      }
      range.value = String(at);
      paint();
    }

    function paint() {
      step.textContent = (at + 1) + ' / ' + n;
      prev.textContent = '◀';
      next.textContent = '▶';
      prev.disabled = at === 0;
      next.disabled = at === n - 1;
      play.textContent = timer
        ? L('❚❚ 멈춤', '❚❚ Pause')
        : L('▶ 재생', '▶ Play');
      prev.setAttribute('aria-label', L('이전 프레임', 'Previous frame'));
      next.setAttribute('aria-label', L('다음 프레임', 'Next frame'));
      range.setAttribute('aria-label', L('프레임 선택', 'Choose a frame'));
      bar.setAttribute('aria-label', L('애니메이션 조작', 'Animation controls'));
    }

    function stop() {
      if (timer) { clearInterval(timer); timer = null; }
      paint();
    }

    function start() {
      if (timer) { stop(); return; }
      if (at === n - 1) show(0);
      timer = setInterval(function () {
        if (at >= n - 1) { stop(); return; }
        show(at + 1);
      }, STEP_MS);
      paint();
    }

    prev.addEventListener('click', function () { stop(); show(at - 1); });
    next.addEventListener('click', function () { stop(); show(at + 1); });
    play.addEventListener('click', start);
    range.addEventListener('input', function () { stop(); show(+range.value); });

    // 그림 위에서도 방향키가 먹게 한다. 슬라이더에 손이 갈 필요를 줄인다.
    fig.setAttribute('tabindex', '0');
    fig.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') { stop(); show(at - 1); e.preventDefault(); }
      else if (e.key === 'ArrowRight') { stop(); show(at + 1); e.preventDefault(); }
      else if (e.key === 'Home') { stop(); show(0); e.preventDefault(); }
      else if (e.key === 'End') { stop(); show(n - 1); e.preventDefault(); }
    });

    window.addEventListener('langchange', paint);
    show(0);
  }

  function boot() {
    var figs = document.querySelectorAll('figure.anim');
    for (var i = 0; i < figs.length; i++) init(figs[i]);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
