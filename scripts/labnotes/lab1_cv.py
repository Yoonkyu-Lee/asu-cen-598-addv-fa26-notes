# -*- coding: utf-8 -*-
"""Lab 1 기록 페이지의 코드 뷰어 스펙. codeview_build.py 가 읽는다."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from codeview_build import N, T  # noqa: E402
from lab1_cv_p1 import GIVEN_FILES, GIVEN_TREES, P1_FILES, P1_TREES, P1TB_FILES, P1TB_TREES  # noqa: E402
from lab1_cv_p2 import (P1FIX, P1BUILD_FILES, P1BUILD_TREES, P2_FILES, P2_TREES,  # noqa: E402
                        P2TB_FILES, P2TB_TREES, P2BUILD_FILES, P2FIX, HISTORY)

LABS = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'asu-cen-598-addv-fa26-labs'))
HEAD = 'c45c13a'

VIEWERS = {
    'given': {'mode': 'file', 'title': T('주어진 코드 · Cummings 논문 원문', 'Given code · the Cummings paper, verbatim'),
              'files': GIVEN_FILES, 'trees': GIVEN_TREES},
    'p1': {'mode': 'diff', 'title': T('Part 1 RTL · 논문 → 제출본', 'Part 1 RTL · paper → submission'),
           'files': P1_FILES, 'trees': P1_TREES},
    'p1tb': {'mode': 'file', 'title': T('Part 1 testbench 전문', 'Part 1 testbench, in full'),
             'files': P1TB_FILES, 'trees': P1TB_TREES},
    'p1fix': {'mode': 'commits', 'title': T('Test 2 를 고친 커밋 둘', 'The two commits that fixed Test 2'), 'commits': P1FIX},
    'p1build': {'mode': 'file', 'title': T('Part 1 Makefile · 환경 파일', 'Part 1 Makefile · environment files'),
                'files': P1BUILD_FILES, 'trees': P1BUILD_TREES},
    'p2': {'mode': 'file', 'title': T('Part 2 RTL 전문', 'Part 2 RTL, in full'), 'files': P2_FILES, 'trees': P2_TREES},
    'p2tb': {'mode': 'file', 'title': T('Part 2 testbench 둘', 'Part 2 testbenches'), 'files': P2TB_FILES,
             'trees': P2TB_TREES, 'start': 'tbe'},
    'p2build': {'mode': 'file', 'title': T('Part 2 Makefile', 'Part 2 Makefile'), 'files': P2BUILD_FILES,
                'trees': [(T('파일', 'files'), [N('part2', kids=[N('Makefile', file='mk2')])])]},
    'p2fix': {'mode': 'commits', 'title': T('재는 쪽을 고친 커밋 셋', 'The three commits that fixed the measuring'),
              'commits': P2FIX},
    'history': {'mode': 'commits', 'title': T('lab1 커밋 전부 · 주석 뺀 diff', 'Every lab1 commit · diffs without comments'),
                'commits': HISTORY},
}
