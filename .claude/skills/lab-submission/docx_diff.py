#!/usr/bin/env python3
"""Structural diff of two .docx files: every block of the body, in order.

Usage: python docx_diff.py ORIGINAL.docx RESULT.docx
       python docx_diff.py --dump FILE.docx      (every block, for the conventions inventory)
       python docx_diff.py --style ORIGINAL.docx RESULT.docx
                                                 (blocks of RESULT whose style, run format or drawing kind
                                                  never occurs in ORIGINAL: new content breaking convention)

A block is a paragraph or a table at the top of the body. For each block it compares
  text (outside text boxes), paragraph style and alignment, the formatting of every run,
  inline images (bytes and size), anchored drawings (position, size, wrap, text-box text,
  image bytes), page and section breaks, and table cell text.
Then it lists the other parts of the package (styles, numbering, headers, media) whose bytes differ.

Exit code 0 when the bodies are identical, 1 otherwise. Every reported difference must be
explained by a ledger line; see SKILL.md.
"""
import difflib
import hashlib
import posixpath
import sys
import zipfile
import xml.etree.ElementTree as ET

NS = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
    'wps': 'http://schemas.microsoft.com/office/word/2010/wordprocessingShape',
    'pr': 'http://schemas.openxmlformats.org/package/2006/relationships',
}
W = '{%s}' % NS['w']


def q(tag):
    p, t = tag.split(':')
    return '{%s}%s' % (NS[p], t)


class Doc:
    def __init__(self, path):
        self.z = zipfile.ZipFile(path)
        self.root = ET.fromstring(self.z.read('word/document.xml'))
        rels = ET.fromstring(self.z.read('word/_rels/document.xml.rels'))
        self.rels = {r.get('Id'): r.get('Target') for r in rels}

    def media_hash(self, rid):
        target = self.rels.get(rid)
        if not target:
            return 'missing-rel:' + rid
        name = posixpath.normpath(posixpath.join('word', target))
        try:
            return hashlib.sha1(self.z.read(name)).hexdigest()[:10]
        except KeyError:
            return 'missing-part:' + name


def strip_fallback(el):
    """Drops mc:Fallback copies (VML duplicates of text boxes) in place."""
    for ac in el.iter(q('mc:AlternateContent')):
        for fb in list(ac.findall(q('mc:Fallback'))):
            ac.remove(fb)


def text_of(el, skip_txbx=True):
    out = []
    def walk(e):
        if skip_txbx and e.tag in (q('w:txbxContent'),):
            return
        if e.tag == q('w:t'):
            out.append(e.text or '')
        elif e.tag == q('w:tab'):
            out.append('\t')
        elif e.tag == q('w:br') and e.get(q('w:type')) not in ('page',):
            out.append('\n')
        for c in e:
            walk(c)
    walk(el)
    return ''.join(out)


def props(el):
    """Canonical string for a pPr or rPr element."""
    if el is None:
        return ''
    parts = []
    for c in el:
        if c.tag == q('w:rPr'):
            continue
        tag = c.tag.split('}')[1]
        attrs = ','.join(f"{k.split('}')[-1]}={v}" for k, v in sorted(c.attrib.items()))
        parts.append(f'{tag}({attrs})' if attrs else tag)
    return ' '.join(sorted(parts))


def drawing_desc(doc, d):
    anchor = d.find(q('wp:anchor'))
    inline = d.find(q('wp:inline'))
    node = anchor if anchor is not None else inline
    if node is None:
        return 'drawing(?)'
    ext = node.find(q('wp:extent'))
    size = f"{ext.get('cx')}x{ext.get('cy')}" if ext is not None else '?'
    blips = [doc.media_hash(b.get(q('r:embed'))) for b in node.iter(q('a:blip'))]
    boxes = [text_of(t, skip_txbx=False).strip() for t in node.iter(q('w:txbxContent'))]
    geom = [g.get('prst') for g in node.iter(q('a:prstGeom'))]
    if anchor is not None:
        ph, pv = anchor.find(q('wp:positionH')), anchor.find(q('wp:positionV'))
        def pos(p):
            if p is None:
                return '?'
            off = p.find(q('wp:posOffset'))
            al = p.find(q('wp:align'))
            return f"{p.get('relativeFrom')}:{off.text if off is not None else (al.text if al is not None else '?')}"
        wrap = next((c.tag.split('}')[1] for c in anchor if c.tag.startswith('{%s}wrap' % NS['wp'])), 'none')
        head = f'anchor[{pos(ph)},{pos(pv)} size={size} wrap={wrap}]'
    else:
        head = f'inline[size={size}]'
    bits = [head]
    if geom:
        bits.append('shape=' + '/'.join(geom))
    if blips:
        bits.append('img=' + '/'.join(blips))
    if boxes:
        bits.append('textbox=' + ' | '.join(repr(b) for b in boxes))
    return ' '.join(bits)


def para_desc(doc, p):
    lines = []
    ppr = p.find(q('w:pPr'))
    style = ''
    if ppr is not None:
        st = ppr.find(q('w:pStyle'))
        style = st.get(q('w:val')) if st is not None else ''
    lines.append(f'P style={style or "-"} pPr=[{props(ppr)}]')
    lines.append('  text=' + repr(text_of(p)))
    pending = None                      # consecutive runs with the same formatting count as one
    def flush():
        if pending and pending[0].strip():
            lines.append(f'  run {pending[0]!r} rPr=[{pending[1]}]')
    for r in p.iter(q('w:r')):
        t = text_of(r)
        rpr = props(r.find(q('w:rPr')))
        if pending and pending[1] == rpr:
            pending[0] += t
        else:
            flush()
            pending = [t, rpr]
        for br in r.findall(q('w:br')):
            if br.get(q('w:type')) == 'page':
                lines.append('  PAGE BREAK')
        for d in r.findall(q('w:drawing')):
            lines.append('  ' + drawing_desc(doc, d))
        for ac in r.findall(q('mc:AlternateContent')):
            for d in ac.iter(q('w:drawing')):
                lines.append('  ' + drawing_desc(doc, d))
    flush()
    if ppr is not None and ppr.find(q('w:sectPr')) is not None:
        lines.append('  SECTION BREAK')
    return lines


def table_desc(t):
    rows = []
    for tr in t.findall(q('w:tr')):
        rows.append(' | '.join(text_of(tc).strip() for tc in tr.findall(q('w:tc'))))
    return ['TABLE'] + ['  row ' + repr(r) for r in rows]


def blocks(doc):
    body = doc.root.find(q('w:body'))
    strip_fallback(body)
    out = []
    for el in body:
        if el.tag == q('w:p'):
            out.append(para_desc(doc, el))
        elif el.tag == q('w:tbl'):
            out.append(table_desc(el))
        elif el.tag == q('w:sectPr'):
            out.append(['FINAL sectPr ' + props(el)])
        else:
            out.append([el.tag.split('}')[1] + ' ' + repr(text_of(el).strip())])
    return out


def features(blk):
    """The convention-bearing features of one block: style, run formats, drawing kinds."""
    out = set()
    for line in blk:
        s = line.strip()
        if s.startswith('P style='):
            out.add('para ' + s.split(' pPr=')[0][2:] + ' pPr=' + s.split(' pPr=')[1])
        elif s.startswith('run '):
            out.add('run rPr=' + s.rsplit(' rPr=', 1)[1])
        elif s.startswith(('anchor[', 'inline[')):
            kind = s.split('[')[0]
            wrap = s.split('wrap=')[1].split(']')[0] if 'wrap=' in s else '-'
            shape = s.split('shape=')[1].split(' ')[0] if 'shape=' in s else '-'
            what = 'textbox' if 'textbox=' in s else ('image' if 'img=' in s else 'shape')
            out.add(f'drawing {kind} wrap={wrap} shape={shape} {what}')
        elif s.startswith('TABLE'):
            out.add('table')
    return out


def style_check(a, b):
    """Blocks of RESULT that use a feature the ORIGINAL never uses."""
    known = set().union(*(features(x) for x in blocks(a)))
    bad = 0
    for i, blk in enumerate(blocks(b)):
        new = sorted(features(blk) - known)
        if new:
            bad += 1
            text = next((l.strip()[6:] for l in blk if l.strip().startswith('text=')), '')
            print(f'[{i}] {text[:90]}')
            for f in new:
                print('     new: ' + f)
    print(f'\n{bad} block(s) use formatting or drawing kinds that the original does not use')
    return bad


def main():
    if sys.argv[1] == '--style':
        sys.exit(1 if style_check(Doc(sys.argv[2]), Doc(sys.argv[3])) else 0)
    if sys.argv[1] == '--dump':
        for i, blk in enumerate(blocks(Doc(sys.argv[2]))):
            print(f'[{i}] ' + '\n'.join(blk))
        return
    a, b = Doc(sys.argv[1]), Doc(sys.argv[2])
    ba, bb = blocks(a), blocks(b)
    ka, kb = ['\n'.join(x) for x in ba], ['\n'.join(x) for x in bb]
    sm = difflib.SequenceMatcher(None, ka, kb, autojunk=False)
    n = 0
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'equal':
            continue
        n += 1
        print(f'=== {op} original blocks {i1}-{i2 - 1} -> result blocks {j1}-{j2 - 1}')
        if op == 'replace' and i2 - i1 == j2 - j1:
            for x, y in zip(ka[i1:i2], kb[j1:j2]):
                for line in difflib.unified_diff(x.split('\n'), y.split('\n'), lineterm='', n=0):
                    if not line.startswith(('---', '+++', '@@')):
                        print('   ' + line)
                print('   ...')
        else:
            for x in ka[i1:i2]:
                print('\n'.join('   - ' + s for s in x.split('\n')))
            for y in kb[j1:j2]:
                print('\n'.join('   + ' + s for s in y.split('\n')))
    other = []
    names = set(a.z.namelist()) | set(b.z.namelist())
    for name in sorted(names):
        if name in ('word/document.xml', 'word/_rels/document.xml.rels') or name.startswith('word/media/'):
            continue
        da = a.z.read(name) if name in a.z.namelist() else None
        db = b.z.read(name) if name in b.z.namelist() else None
        if da != db:
            other.append(name + ('' if da and db else ' (only in one file)'))
    print(f'\n{n} changed region(s) in the body, {len(ka)} -> {len(kb)} blocks')
    if other:
        print('other parts that differ: ' + ', '.join(other))
    sys.exit(1 if n or other else 0)


if __name__ == '__main__':
    main()
