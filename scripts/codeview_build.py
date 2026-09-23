# -*- coding: utf-8 -*-
"""codeview.js 가 읽는 JSON 을 Lab 저장소의 git 히스토리에서 굽는다.

사용법:
  python scripts/codeview_build.py scripts/labnotes/lab1_cv.py > out.json

스펙 파일은 VIEWERS 사전을 만든다. 여기 있는 F / C / N / T 도우미로 쓴다.
  T(ko, en)                    이중 언어 문자열
  F(path, rev=..., base=..., ...)  파일 하나. base 가 있으면 diff, 없으면 원문
  C(hash, note=..., notes=...) 커밋 하나. 그 커밋이 바꾼 코드 파일의 diff.
                               subject= 로 보이는 제목을 바꿀 수 있다 (역할 분담 같은 말을 빼야 할 때)
  N(label, file=..., at=..., kids=[...])  트리 노드

설명 카드(notes)는 줄 번호가 아니라 **그 줄에 들어 있는 글자**로 붙인다.
  ('always_ff @(posedge wclk', ko, en)
앞에서부터 차례로 찾으므로 같은 글자가 여러 번 나와도 순서대로 걸린다.
삭제된 줄에 붙이려면 앞에 '-' 를 붙인다. 못 찾으면 멈춘다. 조용히 틀리지 않게.

비교(diff)할 때는 양쪽 다 주석을 벗긴다. 랩 코드는 주석을 두지 않는 게 규칙이고,
주석까지 비교하면 코드 변화가 주석 변화에 묻힌다. 원문 보기(base 없음)는 strip=False 로
주석을 살릴 수 있다. 주어진 논문 코드를 원문 그대로 보여줄 때 쓴다.
"""
import difflib
import importlib.util
import json
import os
import subprocess
import sys


def T(ko, en):
    return {'ko': ko, 'en': en}


class F:
    def __init__(self, path, rev=None, base=None, base_path=None, strip=True, role='d',
                 prov=None, sum=None, notes=(), key=None, label=None):
        self.path, self.rev, self.base, self.base_path = path, rev, base, base_path
        self.strip, self.role, self.prov, self.sum = strip, role, prov, sum
        self.notes, self.key, self.label = list(notes), key or path, label


class C:
    def __init__(self, hash, note=None, notes=None, renames=None, only=None, subject=None):
        self.hash, self.note, self.subject = hash, note, subject
        self.notes = notes or {}
        self.renames = renames or {}
        self.only = only


class N:
    def __init__(self, label, file=None, at=None, kids=None, open=True, badge=None):
        self.label, self.file, self.at, self.kids = label, file, at, kids
        self.open, self.badge = open, badge


# ---------------------------------------------------------------- 주석 벗기기

def strip_sv(text):
    out, i, n = [], 0, len(text)
    in_str = in_line = in_block = False
    while i < n:
        c, nx = text[i], text[i + 1] if i + 1 < n else ''
        if in_line:
            if c == '\n':
                in_line = False
                out.append(c)
            i += 1
            continue
        if in_block:
            if c == '*' and nx == '/':
                in_block = False
                i += 2
                continue
            if c == '\n':
                out.append(c)
            i += 1
            continue
        if in_str:
            out.append(c)
            if c == '\\' and nx:
                out.append(nx)
                i += 2
                continue
            if c == '"':
                in_str = False
            i += 1
            continue
        if c == '"':
            in_str = True
        elif c == '/' and nx == '/':
            in_line = True
            i += 2
            continue
        elif c == '/' and nx == '*':
            in_block = True
            i += 2
            continue
        out.append(c)
        i += 1
    return ''.join(out)


def strip_comments(path, text):
    if path.endswith(('.sv', '.v', '.svh')):
        s = strip_sv(text)
    elif os.path.basename(path) in ('Makefile', 'env.sh', 'env.cshrc'):
        s = '\n'.join('' if l.lstrip().startswith('#') else l for l in text.split('\n'))
    else:
        return text
    o, t = text.split('\n'), s.split('\n')
    kept = [b.rstrip() for a, b in zip(o, t) if not (b.strip() == '' and a.strip() != '')]
    res, blank = [], 0
    for l in kept:
        blank = blank + 1 if l.strip() == '' else 0
        if blank <= 2:
            res.append(l)
    while res and not res[0].strip():
        res.pop(0)
    while res and not res[-1].strip():
        res.pop()
    return '\n'.join(res) + '\n'


def is_code(path):
    return path.endswith(('.sv', '.v', '.svh')) or os.path.basename(path) in ('Makefile', 'env.sh', 'env.cshrc')


# ---------------------------------------------------------------- git

class Repo:
    def __init__(self, root):
        self.root = root

    def git(self, *args):
        r = subprocess.run(['git', '-C', self.root] + list(args), capture_output=True)
        if r.returncode:
            raise SystemExit('git %s: %s' % (' '.join(args), r.stderr.decode('utf-8', 'replace')))
        return r.stdout.decode('utf-8').replace('\r\n', '\n')

    def show(self, rev, path):
        return self.git('show', '%s:%s' % (rev, path))

    def exists(self, rev, path):
        r = subprocess.run(['git', '-C', self.root, 'cat-file', '-e', '%s:%s' % (rev, path)], capture_output=True)
        return r.returncode == 0

    def meta(self, h):
        out = self.git('show', '-s', '--format=%h%x00%ad%x00%s%x00%P', '--date=short', h).rstrip('\n')
        hh, date, subj, parents = out.split('\x00')
        return hh, date, subj, parents.split()

    def changed(self, parent, h):
        return [l for l in self.git('diff', '--name-only', parent, h).split('\n') if l]


# ---------------------------------------------------------------- 행 만들기

def rows_file(text):
    lines = text.rstrip('\n').split('\n')
    return [[' ', None, i + 1, l] for i, l in enumerate(lines)]


JUNK_LINES = ('', ')', ');', ')(', 'end', 'begin', 'endmodule', 'endtask', 'endfunction', 'end else begin')


def JUNK(line):
    return line.strip() in JUNK_LINES


def rows_diff(a, b):
    al = a.rstrip('\n').split('\n') if a else []
    bl = b.rstrip('\n').split('\n') if b else []
    # 빈 줄이나 end 같은 흔한 줄 하나로 두 판을 이어 붙이면, 통째로 다시 쓴 파일이
    # 옛 줄과 새 줄이 번갈아 끼는 읽을 수 없는 diff 가 된다. 그런 줄은 닻으로 쓰지 않는다.
    sm = difflib.SequenceMatcher(JUNK, al, bl, autojunk=False)
    rows = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'equal':
            for k in range(i2 - i1):
                rows.append([' ', i1 + k + 1, j1 + k + 1, bl[j1 + k]])
        else:
            for k in range(i1, i2):
                rows.append(['-', k + 1, None, al[k]])
            for k in range(j1, j2):
                rows.append(['+', None, k + 1, bl[k]])
    return rows


def attach(rows, notes, where):
    out, start = {}, 0
    for spec in notes:
        anchor, ko, en = spec
        want = '-' if anchor.startswith('-') else None
        a = anchor[1:] if want else anchor
        hit = None
        for i in range(start, len(rows)):
            r = rows[i]
            if (r[0] == '-') != bool(want):
                continue
            if a in r[3]:
                hit = i
                break
        if hit is None:
            raise SystemExit('%s: 설명 기준 글자를 못 찾았다: %r' % (where, anchor))
        if str(hit) in out:
            raise SystemExit('%s: 같은 줄에 설명이 둘: %r' % (where, anchor))
        out[str(hit)] = T(ko, en)
        start = hit + 1
    return out


def find_row(rows, anchor, where):
    for i, r in enumerate(rows):
        if r[0] != '-' and anchor in r[3]:
            return i
    raise SystemExit('%s: 트리 기준 글자를 못 찾았다: %r' % (where, anchor))


# ---------------------------------------------------------------- 조립

def build_file(repo, f, head):
    rev = f.rev or head
    text = repo.show(rev, f.path) if f.path else ''
    if f.strip:
        text = strip_comments(f.path, text)
    d = {'path': f.label or f.path, 'role': f.role}
    if f.base is not None:
        bp = f.base_path or f.path
        old = repo.show(f.base, bp) if repo.exists(f.base, bp) else ''
        old = strip_comments(bp, old)
        rows = rows_diff(old, text)
        if old and bp != f.path:
            d['from'] = bp
        if not old:
            d['isnew'] = True
    else:
        rows = rows_file(text)
    d['rows'] = rows
    if f.prov:
        d['prov'] = f.prov
    if f.sum:
        d['sum'] = f.sum
    if f.notes:
        d['notes'] = attach(rows, f.notes, f.key)
    return d


def build_commit(repo, c, files):
    h, date, subj, parents = repo.meta(c.hash)
    subj = c.subject or subj
    key = 'c:' + h
    parent = parents[0] if parents else None
    links = []
    paths = repo.changed(parent, h) if parent else repo.git('ls-tree', '-r', '--name-only', h).split()
    for p in paths:
        if not is_code(p) or not repo.exists(h, p):
            continue
        if c.only is not None and p not in c.only:
            continue
        bp = c.renames.get(p, p)
        new = strip_comments(p, repo.show(h, p))
        old = strip_comments(bp, repo.show(parent, bp)) if parent and repo.exists(parent, bp) else ''
        rows = rows_diff(old, new)
        if not any(r[0] != ' ' for r in rows):
            continue
        fk = key + ':' + p
        d = {'path': p, 'role': 'v' if '/tb' in p or os.path.basename(p).startswith('tb_') else
             ('t' if not p.endswith(('.sv', '.v')) else 'd'), 'rows': rows}
        if old and bp != p:
            d['from'] = bp
        d['ck'] = key
        if not old:
            d['isnew'] = True
        if p in c.notes:
            d['notes'] = attach(rows, c.notes[p], fk)
        files[fk] = d
        links.append(fk)
    files[key] = {'kind': 'commit', 'meta': {'hash': h, 'date': date, 'subject': subj},
                  'role': 'd', 'sum': c.note, 'links': links, 'rows': None}
    return key, links, h, subj


def build_nodes(nodes, files, where):
    out = []
    for n in nodes:
        d = {'label': n.label}
        if n.file:
            if n.file not in files:
                raise SystemExit('%s: 트리가 없는 파일을 가리킨다: %s' % (where, n.file))
            d['file'] = n.file
            if n.at is not None:
                d['at'] = find_row(files[n.file]['rows'], n.at, where) if isinstance(n.at, str) else n.at
        if n.kids:
            d['kids'] = build_nodes(n.kids, files, where)
        if not n.open:
            d['open'] = False
        if n.badge:
            d['badge'] = n.badge
        out.append(d)
    return out


def build(spec):
    repo = Repo(spec.LABS)
    out = {}
    for vid, v in spec.VIEWERS.items():
        files = {}
        trees = []
        if v['mode'] == 'commits':
            nodes = []
            for c in v['commits']:
                key, links, h, subj = build_commit(repo, c, files)
                kids = [{'label': files[k]['path'].split('/')[-1], 'file': k} for k in links]
                node = {'label': h + '  ' + subj.replace('Lab 1 Part 1: ', '').replace('Lab 1 Part 2: ', '').replace('Lab 1: ', ''), 'file': key}
                if kids:
                    node['kids'] = kids
                    node['open'] = False
                nodes.append(node)
            trees.append({'name': T('커밋', 'commits'), 'nodes': nodes})
            start = v.get('start')
            start = ('c:' + start) if start else nodes[0]['file']
        else:
            for f in v['files']:
                files[f.key] = build_file(repo, f, spec.HEAD)
            for t in v['trees']:
                trees.append({'name': t[0], 'nodes': build_nodes(t[1], files, vid)})
            start = v.get('start') or v['files'][0].key
        out[vid] = {'mode': 'diff' if v['mode'] == 'commits' else v['mode'], 'title': v['title'],
                    'trees': trees, 'files': files, 'start': start}
    return out


def main():
    p = sys.argv[1]
    sp = importlib.util.spec_from_file_location('cvspec', p)
    mod = importlib.util.module_from_spec(sp)
    sys.modules['codeview_build'] = sys.modules[__name__]
    sp.loader.exec_module(mod)
    data = build(mod)
    sys.stdout.reconfigure(encoding='utf-8')
    json.dump(data, sys.stdout, ensure_ascii=False, separators=(',', ':'))


if __name__ == '__main__':
    main()
