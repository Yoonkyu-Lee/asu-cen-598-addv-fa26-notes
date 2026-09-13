# scripts/shotcheck.py
# 사용법: python scripts/shotcheck.py "lab/lab0/materials/Timing Analysis"
#        python scripts/shotcheck.py lab/lab0/materials      (하위 전체)
#
# 잡는 것: Synopsys 트레이닝 수집 shot 이 "덜 그려진 채" 찍혔는지.
#   1) slides.jsonl 의 stable / renderedLen / bodyLen  (수집기가 남긴 판정 근거)
#   2) 슬라이드 본문 영역의 잉크 비율          (로그가 없거나 못 믿을 때의 독립 증거)
# 못 잡는 것: 내용이 맞는지, 도해가 읽히는지. FLAG 난 것은 사람이 눈으로 본다.
#
# 왜 있나: 2026-09-08 수집 때 DC 3 개 강좌 80 장 중 52 장이 나레이션 시작 직후에 찍혀
#   백지이거나 bullet 한 줄만 있었다. 실패 근거가 slides.jsonl 에 이미 있었는데
#   아무도 비교하지 않았다. 그 비교를 기계가 하게 만든 것이 이 파일이다.

import json
import os
import re
import sys
from PIL import Image

# Windows 콘솔이 cp1252 로 잡혀서 한글을 못 뱉는다. 출력만 utf-8 로 돌린다.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Articulate 레슨을 1600x1000 뷰포트로 찍었을 때의 슬라이드 본문 영역.
# 제목줄 아래부터 플레이어 컨트롤 위까지. 왼쪽 Menu 패널과 아래 여백은 뺀다.
BODY_BOX_1600x1000 = (318, 158, 1592, 778)

INK_BLANK = 0.015    # 이 아래면 사실상 백지
INK_SPARSE = 0.035   # 이 아래면 거의 비었다. 본문이 한 줄뿐인 슬라이드도 여기 걸리니 눈으로 본다
# renderedLen / bodyLen 이 이 위여야 다 그려진 것.
# 퀴즈 슬라이드는 정답/오답 피드백 글자가 shown 레이어에 섞여 있어 1.0 이 안 나온다.
# 실측 하한이 0.96 이라 0.95 로 잡는다. 수집기의 stable 판정과 같은 값이다.
RENDER_OK = 0.95


def ink_fraction(path, box):
    im = Image.open(path).convert("L")
    if box:
        if box[2] > im.width or box[3] > im.height:
            return None
        im = im.crop(box)
    px = im.load()
    w, h = im.size
    ink = tot = 0
    for y in range(0, h, 3):
        for x in range(0, w, 3):
            tot += 1
            if px[x, y] < 230:
                ink += 1
    return ink / tot if tot else None


def load_log(course):
    # shots.jsonl 이 수집기의 판정 근거(stable/bodyLen)를 가진 새 로그다.
    # slides.jsonl 은 텍스트 수집용 구 로그라 분모에 Notes 가 섞여 있다. 있으면 새 것을 쓴다.
    path = os.path.join(course, "shots.jsonl")
    if not os.path.exists(path):
        path = os.path.join(course, "slides.jsonl")
    if not os.path.exists(path):
        return {}
    rows = {}
    with open(path, encoding="utf8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            rows[r.get("idx")] = r
    return rows


def check_course(course):
    shots_dir = os.path.join(course, "shots")
    if not os.path.isdir(shots_dir):
        return None
    shots = sorted(n for n in os.listdir(shots_dir) if n.lower().endswith(".png"))
    if not shots:
        return None

    rows = load_log(course)
    print("=== %s  (%d shots, %d log rows)" % (os.path.basename(course), len(shots), len(rows)))

    flagged = []
    for name in shots:
        path = os.path.join(shots_dir, name)
        # 파일 이름은 s00.png 이거나 목차 이름을 붙인 00_1.3_pure-verilog-flow.png 다.
        # 어느 쪽이든 **맨 앞의 숫자**가 인덱스다. 이름 안의 다른 숫자를 섞으면 안 된다.
        stem = os.path.splitext(name)[0]
        m = re.match(r"^s?(\d+)", stem)
        idx = int(m.group(1)) if m else -1
        r = rows.get(idx, {})

        im = Image.open(path)
        box = BODY_BOX_1600x1000 if im.size == (1600, 1000) else None
        frac = ink_fraction(path, box)

        why = []

        # 1) 수집기의 판정 근거. 있으면 이게 가장 정확하다.
        if "stable" in r and not r["stable"]:
            why.append("NOT_SETTLED")
        body = r.get("bodyLen")
        if body:
            ratio = r.get("renderedLen", 0) / body
            if ratio < RENDER_OK:
                why.append("PARTIAL %d%%" % round(ratio * 100))
        elif r.get("fullLen"):
            # 구 스키마. fullLen 은 Notes 를 포함해서 분모가 부풀어 있으니 참고용으로만 본다.
            ratio = r.get("renderedLen", 0) / r["fullLen"]
            if ratio < 0.5:
                why.append("PARTIAL? %d%% (구 스키마, Notes 포함 분모)" % round(ratio * 100))

        # 1b) Articulate 클래식(VCS)은 seek 을 ms 로 기록한다. 끝까지 안 갔으면 알려준다.
        #     끝이 아니어도 마지막 오브젝트가 이미 나왔으면 멀쩡하니, 자동 실패가 아니라 눈으로 볼 거리다.
        sk = r.get("seek")
        if isinstance(sk, dict):
            try:
                v, m = float(sk.get("value", 0)), float(sk.get("max", 0))
                if m and v / m < 0.95:
                    why.append("SEEK_SHORT %d%% (끝까지 안 밀렸다. 내용은 멀쩡할 수 있으니 눈으로 본다)"
                               % round(v / m * 100))
            except (TypeError, ValueError):
                pass

        # 2) 픽셀. 로그와 독립이라 로그를 믿을 수 없을 때 판을 가른다.
        if frac is None:
            why.append("본문 영역 미상 (%dx%d)" % im.size)
        elif frac < INK_BLANK:
            why.append("BLANK ink=%.3f" % frac)
        elif frac < INK_SPARSE:
            why.append("SPARSE ink=%.3f" % frac)

        # 3) 엉뚱한 슬라이드를 찍었는지. 끝까지 밀면 자동 진행으로 다음 장이 찍힐 수 있다.
        # 목차 0 번은 'Unit 1-1' 같은 섹션 헤더라 자기 슬라이드가 없고 1 번을 가리킨다. 정상이다.
        header_alias = (idx == 0 and r.get("selectedIdx") == 1)
        if "selectedIdx" in r and r["selectedIdx"] != idx and not header_alias:
            why.append("WRONG_SLIDE selectedIdx=%s (원한 것은 %d) %r"
                       % (r["selectedIdx"], idx, r.get("selected")))
        elif r.get("toc") and r.get("selected") and r["toc"] != r["selected"]:
            why.append("MISMATCH toc=%r selected=%r" % (r["toc"], r["selected"]))

        if why:
            flagged.append((name, r.get("toc") or r.get("selected") or "", why))

    for name, toc, why in flagged:
        print("  FLAG %-54s %s" % (name[:54], " / ".join(why)))
    print("  flagged %d / %d" % (len(flagged), len(shots)))
    return len(flagged), len(shots)


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "lab/lab0/materials"
    if not os.path.isdir(target):
        print("경로 없음: %s" % target)
        return 2

    courses = []
    if os.path.isdir(os.path.join(target, "shots")):
        courses = [target]
    else:
        courses = [os.path.join(target, n) for n in sorted(os.listdir(target))
                   if os.path.isdir(os.path.join(target, n, "shots"))]
    if not courses:
        print("shots/ 를 가진 강좌 폴더가 없다: %s" % target)
        return 2

    total_flag = total_shot = 0
    for c in courses:
        res = check_course(c)
        if res:
            total_flag += res[0]
            total_shot += res[1]

    print()
    print("합계: %d / %d 장이 걸렸다." % (total_flag, total_shot))
    if total_flag:
        print("FLAG 난 것은 눈으로 확인하고, 덜 그려진 것이면 그 슬라이드만 다시 찍는다.")
    return 1 if total_flag else 0


if __name__ == "__main__":
    sys.exit(main())
