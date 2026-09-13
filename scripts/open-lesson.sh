#!/usr/bin/env bash
# scripts/open-lesson.sh "<레슨 제목>" [강좌 lessons URL]
# Synopsys Learning Center 의 레슨 하나를 열고 SCORM 콘텐츠 프레임까지 들어간다.
# 투어 팝업, 쿠키 배너, Resume 프롬프트를 순서대로 치운다. 절차는 .claude/skills/synopsys-training 참조.

set -u
TITLE="${1:?레슨 제목을 달라}"
URL="${2:-https://training.synopsys.com/learn/courses/86/design-compiler-rtl-synthesis-202212/lessons}"

B="$HOME/.claude/skills/gstack/browse/dist/browse.exe"
[ -x "$B" ] || B="$HOME/.claude/skills/gstack/browse/dist/browse"

mkdir -p .gstack/tmp   # browse eval 은 cwd 아래 경로만 읽는다

"$B" frame main >/dev/null 2>&1
"$B" goto "$URL" >/dev/null 2>&1
"$B" viewport 1600x1000 >/dev/null 2>&1

# 투어 팝업과 쿠키 배너를 먼저 치운다. 안 치우면 클릭이 가로막힌다.
"$B" js '(()=>{const t=[...document.querySelectorAll("button")].find(e=>/Explore on my own/i.test(e.innerText||"")); if(t)t.click(); const a=[...document.querySelectorAll("button")].find(e=>/^Accept$/i.test((e.innerText||"").trim())); if(a)a.click(); return "ok";})()' >/dev/null 2>&1

cat > .gstack/tmp/_open.js <<JS
(() => {
  const s = [...document.querySelectorAll('span')].find(e => e.innerText.trim() === ${TITLE@Q});
  if (!s) return 'lesson not found';
  let n = s, h = 0;
  while (n && h < 8) { if (/list-item|lesson/i.test(n.className||'') || /LESSON/i.test(n.tagName)) { n.click(); return 'clicked'; } n = n.parentElement; h++; }
  return 'no clickable ancestor';
})()
JS
# goto 는 Angular 렌더보다 먼저 돌아온다. 목록이 그려질 때까지 기다렸다가 클릭한다.
for i in $(seq 1 10); do
  r=$("$B" eval .gstack/tmp/_open.js 2>&1 | tail -1)
  case "$r" in *clicked*) echo "lesson: $r"; break;; esac
  sleep 2
done
[ "${r:-}" = "clicked" ] || echo "lesson: $r"

# 완료된 레슨은 Retake, 처음이면 Resume/Start 다.
sleep 2
"$B" js '(()=>{const el=[...document.querySelectorAll("button,a")].find(e=>/Retake the lesson|Resume training|Start learning now|Launch/i.test(e.innerText||"")); if(el){el.click(); return "launched: "+el.innerText.trim();} return "already open";})()' 2>&1 | tail -1

# SCORM iframe 이 뜰 때까지 기다린다.
for i in 1 2 3 4 5 6 7 8; do
  n=$("$B" js 'document.querySelectorAll("iframe").length' 2>/dev/null | tail -1)
  [ "$n" != "0" ] && break
  sleep 2
done

# --name 은 프레임 트리 전체에서 찾아 준다. CSS 선택자는 main 기준이라 중첩 프레임에 못 닿는다.
# sco 프레임은 launcher 가 SCORM 패키지를 받아온 뒤에야 생기므로 붙을 때까지 다시 시도한다.
for i in $(seq 1 12); do
  f=$("$B" frame --name sco 2>&1 | tail -1)
  case "$f" in *"Switched to frame"*) echo "frame: ok"; break;; esac
  sleep 2
done
case "${f:-}" in *"Switched to frame"*) ;; *) echo "frame: $f";; esac

# Resume 프롬프트가 있으면 처음부터로 답한다. el.click() 은 안 먹고 browse click 은 먹는다.
sleep 2
if "$B" js 'document.querySelector(".slide") && /cs-ResumePromptSlide/.test(document.querySelector(".slide").className)' 2>/dev/null | tail -1 | grep -q true; then
  "$B" click 'button:has-text("No")' >/dev/null 2>&1
  echo "resume prompt: dismissed"
fi

"$B" js '"outline items = " + document.querySelectorAll(".cs-outline .cs-listitem").length' 2>&1 | tail -1
