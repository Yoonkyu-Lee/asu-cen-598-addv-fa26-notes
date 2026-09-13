# scripts/rename-shots.py
# 사용법: python scripts/rename-shots.py lab/lab0/materials          (전체)
#        python scripts/rename-shots.py "lab/lab0/materials/Timing Analysis"
#        python scripts/rename-shots.py lab/lab0/materials --dry     (미리보기)
#
# 수집기가 찍은 s00.png, s01.png ... 을 **목차 번호와 이름**에 맞춰 바꾼다.
#   s09.png -> 09_1.3_pure-verilog-flow-2-step.png
#   s11.png -> 11_how-is-the-target-library-used.png      (목차에 번호가 없는 경우)
#
# 인덱스를 맨 앞에 둔다. 목차 번호만으로는 1.10 이 1.2 보다 앞서서 정렬이 목차 순서와 어긋난다.
#
# 이름의 출처는 세 곳이고, 아래일수록 우선한다. 기준은 **목차에 적힌 라벨**이다.
#   3) shots.jsonl 의 selected      플레이어가 하이라이트한 항목. 섹션 헤더에서는 다음 장 이름이 나온다
#   2) transcript.md 의 `## [NN] 제목`  TechSmith(Verdi)처럼 jsonl 이 없는 강좌를 덮는다
#   1) slides.jsonl 의 toc          목차 라벨 그대로라 가장 정확하다
#
# 다시 돌려도 안전하다. 수집기가 s00.png 를 새로 만들면 같은 인덱스의 옛 이름 파일을 지우고 바꾼다.

import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# "1.3. Pure Verilog Flow (2-step)" -> ("1.3", "Pure Verilog Flow (2-step)")
# "IV. Objectives"                  -> ("IV", "Objectives")
# "How is the Target Library Used?" -> (None, 전체)
NUMBERED = re.compile(r"^((?:\d+|[IVXLCDM]+)(?:\.\d+)*)\.\s+(.+)$")


def split_label(label):
    m = NUMBERED.match(label.strip())
    if m:
        return m.group(1), m.group(2)
    return None, label.strip()


def slug(text):
    s = text.lower()
    s = s.replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s[:60].rstrip("-") or "untitled"


def labels_from_jsonl(path, key):
    out = {}
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            v = r.get(key)
            if r.get("idx") is not None and v:
                out[r["idx"]] = v
    return out


def labels_from_transcript(path):
    out = {}
    if not os.path.exists(path):
        return out
    for m in re.finditer(r"^## \[(\d+)\]\s+(.+)$", open(path, encoding="utf8").read(), re.M):
        out[int(m.group(1))] = m.group(2).strip()
    return out


def labels_for(course):
    # 뒤에 오는 것이 앞을 덮는다. **목차 라벨**을 가장 우선한다.
    # shots.jsonl 의 selected 는 플레이어가 하이라이트한 항목이라 섹션 헤더에서 다음 장 이름이 나온다.
    # (예: 목차 0 번은 'Unit 1-1' 인데 selected 는 'Introduction' 이다)
    labels = {}
    labels.update(labels_from_jsonl(os.path.join(course, "shots.jsonl"), "selected"))
    labels.update(labels_from_transcript(os.path.join(course, "transcript.md")))
    labels.update(labels_from_jsonl(os.path.join(course, "slides.jsonl"), "toc"))
    return labels


def fix_references(course, mapping, dry):
    """transcript.md 등이 가리키는 shots/... 경로를 새 이름으로 고친다.
    이걸 안 하면 이름만 바뀌고 문서의 링크가 전부 깨진다."""
    pat = re.compile(r"shots/(s?(\d+)[^\s)\"']*\.png)")
    touched = 0
    for name in sorted(os.listdir(course)):
        if not name.endswith(".md"):
            continue
        path = os.path.join(course, name)
        text = open(path, encoding="utf8").read()

        def sub(m):
            idx = int(m.group(2))
            return "shots/" + mapping[idx] if idx in mapping else m.group(0)

        new_text = pat.sub(sub, text)
        if new_text != text:
            n = sum(1 for _ in pat.finditer(text))
            print("  %s  참조 %d 곳 %s" % (name, n, "고칠 것" if dry else "고쳤다"))
            if not dry:
                open(path, "w", encoding="utf8").write(new_text)
            touched += 1
    return touched


def target_name(idx, label):
    num, title = split_label(label)
    # 목차 번호가 인덱스와 같으면 (Verdi 처럼) 중복이라 뺀다. 10_10_... 이 되는 걸 막는다.
    if num and num.isdigit() and int(num) == idx:
        num = None
    parts = ["%02d" % idx] + ([num] if num else []) + [slug(title)]
    return "_".join(parts) + ".png"


def rename_course(course, dry):
    shots = os.path.join(course, "shots")
    if not os.path.isdir(shots):
        return 0, 0
    labels = labels_for(course)
    print("=== %s" % os.path.basename(course))

    files = sorted(n for n in os.listdir(shots) if n.lower().endswith(".png"))
    # 이미 바꾼 파일도 매핑에 넣어야 문서 참조 고치기가 다시 돌려도 동작한다.
    idx_of = {}
    for n in files:
        m = re.match(r"^s?(\d+)", os.path.splitext(n)[0])
        if m:
            idx_of.setdefault(int(m.group(1)), []).append(n)

    done = skipped = 0
    mapping = {}   # idx -> 새 파일 이름. 문서 참조를 고치는 데 쓴다.
    for idx in sorted(idx_of):
        label = labels.get(idx)
        if not label:
            print("  ! %02d  목차 이름을 못 찾았다. 그대로 둔다" % idx)
            skipped += 1
            continue
        target = target_name(idx, label)
        mapping[idx] = target

        here = idx_of[idx]
        if here == [target]:
            continue   # 이미 맞다

        src = os.path.join(shots, here[0])
        dst = os.path.join(shots, target)
        stale = [n for n in here if n != target]
        if dry:
            print("  %s -> %s" % (here[0], target))
        else:
            # 원본을 먼저 옮기고, 같은 인덱스의 낡은 이름만 치운다.
            if os.path.abspath(src) != os.path.abspath(dst):
                if os.path.exists(dst):
                    os.remove(dst)
                os.rename(src, dst)
                stale = [n for n in stale if n != here[0]]
            for n in stale:
                os.remove(os.path.join(shots, n))
            print("  %s -> %s" % (here[0], target))
        done += 1

    if done == 0:
        print("  파일 이름은 이미 목차에 맞다")
    fix_references(course, mapping, dry)
    return done, skipped


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry" in sys.argv
    target = args[0] if args else "lab/lab0/materials"
    if not os.path.isdir(target):
        print("경로 없음: %s" % target)
        return 2

    if os.path.isdir(os.path.join(target, "shots")):
        courses = [target]
    else:
        courses = [os.path.join(target, n) for n in sorted(os.listdir(target))
                   if os.path.isdir(os.path.join(target, n, "shots"))]
    if not courses:
        print("shots/ 를 가진 강좌 폴더가 없다: %s" % target)
        return 2

    td = ts = 0
    for c in courses:
        d, s = rename_course(c, dry)
        td += d
        ts += s
    print()
    print("%s %d 장, 이름 못 찾아 건너뛴 것 %d 장" % ("바꿀 것" if dry else "바꿨다", td, ts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
