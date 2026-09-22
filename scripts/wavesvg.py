# -*- coding: utf-8 -*-
"""시뮬레이션 트레이스 CSV 를 노트에 넣을 SVG 파형으로 그린다.

왜 Verdi 스크린샷을 안 쓰나. 스크린샷에 구운 주석은 이중 언어가 안 되고,
다크모드에서 흰 배경만 남고, 나중에 한 글자도 못 고친다. 벡터로 그리면 셋 다 된다.

트레이스를 만드는 쪽은 testbench 의 +TRACE 다. 이 스크립트는 값을 지어내지 않는다.
CSV 에 있는 것만 그린다.

사용법:
  신호 스펙은 name:kind:role 이다. kind 는 bit / bus / busx / clk, role 은 색을 정한다
  (clk sig ver ok warn dim, 비우면 이름으로 짐작). CLAUDE.md 의 의미 고정 색상 그대로다.

  python scripts/wavesvg.py wave --csv t.csv --time cycle \\
      --signals "write_en:bit,data_in:bus,out_valid:bit,data_out:bus" \\
      --from 0 --to 60 --marks "12=1,41=2" --out frag.svg

  python scripts/wavesvg.py occ --csv t.csv --time cycle \\
      --series "occ_even,occ_odd" --out frag.svg

SVG 규칙은 note-html 스킬이 단일 출처다. 여기서 지키는 것:
  viewBox 만 쓰고 width/height 를 안 준다. role 과 aria-label 을 단다.
  색은 토큰만 쓴다. 크기는 인라인 style 로 준다 (프레젠테이션 속성은 클래스에 진다).
  서술은 SVG 에 안 넣는다. 숫자 마커만 찍고 설명은 HTML 이 한다.
"""
import argparse
import csv
import io
import sys

# 의미 고정 색상. CLAUDE.md 의 표 그대로다.
CLK = 'var(--brown)'      # 클럭
SIG = 'var(--blue)'       # 설계 쪽 신호
VER = 'var(--pink)'       # 검증 쪽에서 미는 신호
OK = 'var(--green)'       # 통과, 유효
WARN = 'var(--amber)'     # 함정, 버그. 파형에서는 안 쓴다
MARK = 'var(--sel)'       # 읽을 자리 마커. 선택 강조 토큰이다
DIM = 'var(--ink3)'
INK = 'var(--ink)'
INK2 = 'var(--ink2)'
GRID = 'var(--rule)'

GUTTER = 96      # 신호 이름 칸
PAD_R = 12
ROW = 26         # 신호 한 줄 높이
WAVE = 15        # 0 과 1 의 높이차
HEAD = 40        # 눈금 + 마커 자리. 마커 동그라미가 눈금 글자를 안 덮게 벌려 둔다
W = 720


def esc(s):
    return (str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


def read_csv(path, time_col):
    rows = []
    with io.open(path, encoding='utf-8', newline='') as fh:
        for r in csv.DictReader(fh):
            if not r.get(time_col):
                continue
            rows.append({k: (v.strip() if v is not None else '') for k, v in r.items()})
    if not rows:
        sys.exit('빈 CSV: %s' % path)
    return rows


def window(rows, time_col, lo, hi):
    out = [r for r in rows if lo <= int(r[time_col]) <= hi]
    if not out:
        sys.exit('그 구간에 값이 없다: %s..%s' % (lo, hi))
    return out


ROLE = {'clk': CLK, 'sig': SIG, 'ver': VER, 'ok': OK, 'warn': WARN, 'dim': DIM}


def colour_for(name, kind, role=''):
    if role:
        return ROLE[role]
    if kind == 'clk':
        return CLK
    if name.endswith('_en') or name.startswith('write') or name.startswith('read'):
        return VER          # testbench 가 미는 신호
    if 'valid' in name or name.startswith('out'):
        return OK
    return SIG


def fmt(v, kind):
    if v in ('x', 'X', ''):
        return 'X'
    if kind == 'busx':
        return '%02x' % int(v)
    return str(int(v))


def render_wave(rows, time_col, specs, marks, label, title_note):
    n = len(rows)
    plot = W - GUTTER - PAD_R
    step = plot / float(n)
    h = HEAD + ROW * len(specs) + 16

    t0 = int(rows[0][time_col])
    t1 = int(rows[-1][time_col])

    o = []
    o.append('<svg viewBox="0 0 %d %d" role="img" aria-label="%s">' % (W, h, esc(label)))

    # 시간 눈금. 너무 촘촘하면 글자가 겹치므로 6 칸으로 자른다.
    ticks = 6
    for i in range(ticks + 1):
        frac = i / float(ticks)
        x = GUTTER + plot * frac
        t = int(round(t0 + (t1 - t0) * frac))
        o.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" style="stroke:%s;stroke-width:1"/>'
                 % (x, HEAD - 14, x, h - 16, GRID))
        o.append('<text class="svgnum" x="%.1f" y="%d" style="font-size:10px;text-anchor:middle;fill:%s">%d</text>'
                 % (x, HEAD - 28, DIM, t))
    o.append('<text class="svglab" x="%d" y="%d" style="font-size:10px;fill:%s">%s</text>'
             % (4, HEAD - 28, DIM, esc(title_note)))

    for si, (name, kind, role) in enumerate(specs):
        top = HEAD + ROW * si
        base = top + ROW - 8          # 0 레벨
        high = base - WAVE            # 1 레벨
        col = colour_for(name, kind, role)

        o.append('<text class="svglab" x="%d" y="%.1f" style="font-size:11px;fill:%s">%s</text>'
                 % (4, base - 2, INK2, esc(name)))

        vals = [r.get(name, '') for r in rows]

        if kind in ('bus', 'busx'):
            # 값이 바뀌는 곳에서 육각형을 끊고 그 안에 숫자를 적는다.
            i = 0
            while i < n:
                j = i
                while j + 1 < n and vals[j + 1] == vals[i]:
                    j += 1
                x0 = GUTTER + step * i
                x1 = GUTTER + step * (j + 1)
                k = min(3.0, (x1 - x0) / 3.0)
                o.append('<path d="M%.1f,%.1f L%.1f,%.1f L%.1f,%.1f L%.1f,%.1f L%.1f,%.1f L%.1f,%.1f Z" '
                         'style="fill:none;stroke:%s;stroke-width:1.3"/>'
                         % (x0, (base + high) / 2.0, x0 + k, high, x1 - k, high,
                            x1, (base + high) / 2.0, x1 - k, base, x0 + k, base, col))
                if x1 - x0 > 20:
                    o.append('<text class="svgnum" x="%.1f" y="%.1f" style="font-size:10px;text-anchor:middle;fill:%s">%s</text>'
                             % ((x0 + x1) / 2.0, base - 3, INK, esc(fmt(vals[i], kind))))
                i = j + 1
        else:
            # 0 과 1 의 사각 파형. 값이 바뀌는 곳에서만 꺾는다. 샘플마다 점을 찍으면
            # 1 ns 격자 트레이스에서 파일이 수십 KB 가 된다.
            d = []
            prev = None
            for i, v in enumerate(vals):
                lvl = high if v not in ('0', '', 'x', 'X') else base
                x0 = GUTTER + step * i
                if prev is None:
                    d.append('M%.1f,%.1f' % (x0, lvl))
                elif lvl != prev:
                    d.append('H%.1f V%.1f' % (x0, lvl))
                prev = lvl
            d.append('H%.1f' % (GUTTER + step * n))
            o.append('<path d="%s" style="fill:none;stroke:%s;stroke-width:1.5"/>' % (' '.join(d), col))

    # 눈으로 짚을 자리. 숫자만 찍고 말은 HTML 이 한다.
    for t, tag in marks:
        idx = None
        for i, r in enumerate(rows):
            if int(r[time_col]) >= t:
                idx = i
                break
        if idx is None:
            continue
        x = GUTTER + step * idx
        o.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" '
                 'style="stroke:%s;stroke-width:1.2;stroke-dasharray:3 3"/>'
                 % (x, HEAD - 14, x, h - 18, MARK))
        o.append('<circle cx="%.1f" cy="%d" r="8" style="fill:%s"/>' % (x, HEAD - 14, MARK))
        o.append('<text class="svgnum" x="%.1f" y="%d" style="font-size:10px;text-anchor:middle;fill:var(--paper)">%s</text>'
                 % (x, HEAD - 11, esc(tag)))

    o.append('</svg>')
    return '\n'.join(o)


def render_occ(rows, time_col, series, label, ymax=None):
    """series 는 [(name, role, dashed)]. 두 FIFO 는 둘 다 설계 쪽이라 같은 파랑이고
    실선과 점선으로 가른다. 색으로 가르면 의미 고정 색상을 어긴다."""
    n = len(rows)
    plot = W - GUTTER - PAD_R
    h = 200
    top, bot = 26, h - 30
    step = plot / float(n - 1 if n > 1 else 1)

    data = {s: [int(r[s]) for r in rows] for s, _, _ in series}
    hi = ymax or max(1, max(max(v) for v in data.values()))

    t0 = int(rows[0][time_col])
    t1 = int(rows[-1][time_col])

    o = ['<svg viewBox="0 0 %d %d" role="img" aria-label="%s">' % (W, h, esc(label))]

    # y 눈금
    for i in range(5):
        y = bot - (bot - top) * i / 4.0
        val = int(round(hi * i / 4.0))
        o.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" style="stroke:%s;stroke-width:1"/>'
                 % (GUTTER, y, W - PAD_R, y, GRID))
        o.append('<text class="svgnum" x="%d" y="%.1f" style="font-size:10px;text-anchor:end;fill:%s">%d</text>'
                 % (GUTTER - 6, y + 3, DIM, val))

    # x 눈금
    for i in range(7):
        frac = i / 6.0
        x = GUTTER + plot * frac
        t = int(round(t0 + (t1 - t0) * frac))
        o.append('<text class="svgnum" x="%.1f" y="%d" style="font-size:10px;text-anchor:middle;fill:%s">%d</text>'
                 % (x, h - 12, DIM, t))

    for si, (s, role, dashed) in enumerate(series):
        col = ROLE.get(role or 'sig', SIG)
        dash = ';stroke-dasharray:5 4' if dashed else ''
        pts = []
        for i, v in enumerate(data[s]):
            x = GUTTER + step * i
            y = bot - (bot - top) * (v / float(hi))
            pts.append('%s%.1f,%.1f' % ('M' if i == 0 else 'L', x, y))
        o.append('<path d="%s" style="fill:none;stroke:%s;stroke-width:1.8%s"/>' % (' '.join(pts), col, dash))
        peak = max(data[s])
        pi = data[s].index(peak)
        px = GUTTER + step * pi
        py = bot - (bot - top) * (peak / float(hi))
        o.append('<circle cx="%.1f" cy="%.1f" r="3" style="fill:%s"/>' % (px, py, col))
        o.append('<text class="svgnum" x="%.1f" y="%.1f" style="font-size:10px;fill:%s">%d</text>'
                 % (px + 6, py - 4, col, peak))
        # 범례는 오른쪽 위에 가로로 늘어놓는다. 왼쪽에 두면 y 축 눈금 글자와 겹친다.
        lx = W - PAD_R - 150 * (len(series) - si)
        o.append('<line x1="%d" y1="%d" x2="%d" y2="%d" style="stroke:%s;stroke-width:1.8%s"/>'
                 % (lx, 11, lx + 22, 11, col, dash))
        o.append('<text class="svglab" x="%d" y="%d" style="font-size:11px;fill:%s">%s</text>'
                 % (lx + 28, 15, INK2, esc(s)))

    o.append('</svg>')
    return '\n'.join(o)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['wave', 'occ'])
    ap.add_argument('--csv', required=True)
    ap.add_argument('--time', default='cycle')
    ap.add_argument('--signals', default='')
    ap.add_argument('--series', default='')
    ap.add_argument('--marks', default='')
    ap.add_argument('--label', default='simulation waveform')
    ap.add_argument('--note', default='')
    ap.add_argument('--ymax', type=int, default=0)
    ap.add_argument('--out', default='')
    ap.add_argument('--from', dest='lo', type=int, default=-10 ** 9)
    ap.add_argument('--to', dest='hi', type=int, default=10 ** 9)
    a = ap.parse_args()

    rows = window(read_csv(a.csv, a.time), a.time, a.lo, a.hi)

    if a.mode == 'wave':
        specs = []
        for tok in a.signals.split(','):
            tok = tok.strip()
            if not tok:
                continue
            parts = tok.split(':')
            name = parts[0]
            kind = parts[1] if len(parts) > 1 and parts[1] else 'bit'
            role = parts[2] if len(parts) > 2 else ''
            if role and role not in ROLE:
                sys.exit('모르는 역할: %s (가능: %s)' % (role, ', '.join(ROLE)))
            specs.append((name, kind, role))
        missing = [n for n, _, _ in specs if n not in rows[0]]
        if missing:
            sys.exit('CSV 에 없는 신호: %s\n있는 것: %s'
                     % (', '.join(missing), ', '.join(rows[0].keys())))
        marks = []
        for tok in a.marks.split(','):
            tok = tok.strip()
            if not tok:
                continue
            t, _, tag = tok.partition('=')
            marks.append((int(t), tag))
        out = render_wave(rows, a.time, specs, marks, a.label, a.note)
    else:
        series = []
        for tok in a.series.split(','):
            tok = tok.strip()
            if not tok:
                continue
            parts = tok.split(':')
            series.append((parts[0], parts[1] if len(parts) > 1 else 'sig',
                           len(parts) > 2 and parts[2] == 'dash'))
        missing = [s for s, _, _ in series if s not in rows[0]]
        if missing:
            sys.exit('CSV 에 없는 신호: %s' % ', '.join(missing))
        out = render_occ(rows, a.time, series, a.label, a.ymax or None)

    if a.out:
        io.open(a.out, 'w', encoding='utf-8', newline='').write(out + '\n')
        sys.stderr.write('wrote %s (%d bytes)\n' % (a.out, len(out)))
    else:
        sys.stdout.write(out + '\n')


if __name__ == '__main__':
    main()
