#!/usr/bin/env bash
# scripts/collect-articulate.sh
# 사용법: scripts/collect-articulate.sh "<수집물 폴더>" [시작index] [끝index]
#   예:  scripts/collect-articulate.sh "lab/lab0/materials/Timing Analysis" 0 17
#
# 전제: gstack browse 가 headed 로 떠 있고, Synopsys 로그인이 살아 있고,
#       레슨 플레이어가 열려 있고, `browse frame --name sco` 로 콘텐츠 프레임에 들어가 있다.
#       절차 전체는 .claude/skills/synopsys-training 참조.
#
# 한 슬라이드마다: 목차 클릭 → articulate-step.js 로 끝까지 밀고 판정 → 뷰포트 스크린샷.
# 판정 결과는 shots.jsonl 에 append 한다. 끊겨도 그 index 부터 다시 돌리면 된다.

set -u

DIR="${1:?수집물 폴더를 달라}"
FROM="${2:-0}"
TO="${3:-}"

B="$HOME/.claude/skills/gstack/browse/dist/browse.exe"
[ -x "$B" ] || B="$HOME/.claude/skills/gstack/browse/dist/browse"
STEP="scripts/articulate-step.js"

mkdir -p "$DIR/shots"
LOG="$DIR/shots.jsonl"

if [ -z "$TO" ]; then
  TO=$("$B" js '(document.querySelectorAll(".cs-outline .cs-listitem").length - 1)' 2>/dev/null | tail -1)
fi

# 플레이어에 따라 seek 목표 사다리가 다르다.
# 클래식은 끝에 닿으면 **무조건** 다음 장으로 자동 진행하므로 0.999 로 시작하면 매번 헛돈다.
PLAYER=$("$B" js '(/index_lms\.html/.test(location.href) || !!document.querySelector("#play-pause")) ? "classic" : "html5"' 2>/dev/null | tail -1)
case "$PLAYER" in
  classic) LADDER="0.95 0.90 0.80 0" ;;
  *)       LADDER="0.999 0.95 0.85 0" ;;
esac
FIRST=${LADDER%% *}
REST=${LADDER#* }

echo "수집: $DIR  index $FROM..$TO  (player=$PLAYER, seek 사다리=$LADDER)"

# 클래식(VCS)의 목차는 아코디언이다. 섹션이 접혀 있으면 하위 항목이 hidden 이라 클릭이 안 된다.
# 안 보이면 그 항목을 감싸는 섹션 행을 먼저 눌러서 펼친다. 펼침에 애니메이션이 있어 기다려야 한다.
ensure_visible() {
  vis=$("$B" js "(()=>{const it=[...document.querySelectorAll('.cs-outline .cs-listitem')]; return it[$1] ? (it[$1].offsetParent!==null) : false;})()" 2>/dev/null | tail -1)
  [ "$vis" = "true" ] && return 0
  scene=$("$B" js "(()=>{const it=[...document.querySelectorAll('.cs-outline .cs-listitem')]; let s=-1; for(let k=0;k<=$1&&k<it.length;k++) if(/is-scene/.test(it[k].className)) s=k; return s;})()" 2>/dev/null | tail -1)
  [ "${scene:--1}" = "-1" ] && return 1
  "$B" click ".cs-outline .cs-listitem >> nth=$scene" >/dev/null 2>&1
  sleep 3
}

shot_once() {  # $1=index  $2=seek 목표(0..1 비율)
  ensure_visible "$1"
  "$B" js "window.__seekTo=$2; 'ok'" >/dev/null 2>&1
  "$B" click ".cs-outline .cs-listitem >> nth=$1" >/dev/null 2>&1
  "$B" eval "$STEP" 2>&1 | tail -1
}

for i in $(seq "$FROM" "$TO"); do
  n=$(printf "%02d" "$i")
  out=$(shot_once "$i" "$FIRST")
  # 자동 진행이 켜진 슬라이드는 끝까지 밀면 다음 장으로 넘어간다.
  # 선택된 목차가 어긋났으면 덜 밀어서 다시 잡는다.
  # 원한 슬라이드이면서(selectedIdx) 다 그려졌을 때만(stable) 통과다. 둘 중 하나라도 아니면 다시 잡는다.
  for to in $REST; do
    case "$out" in
      *'"stable":true'*)
        case "$out" in *"\"selectedIdx\":$i,"*) break;; esac ;;
    esac
    out=$(shot_once "$i" "$to")
  done
  "$B" screenshot --viewport "$DIR/shots/s$n.png" >/dev/null 2>&1
  echo "{\"idx\":$i,$(echo "$out" | sed 's/^{//')" >> "$LOG"
  echo "  s$n  $out"
done

echo
echo "끝났다."
echo "  검사:   python scripts/shotcheck.py \"$DIR\""
echo "  이름:   python scripts/rename-shots.py \"$DIR\"   (목차 번호/이름으로 바꾸고 문서 참조까지 고친다)"
