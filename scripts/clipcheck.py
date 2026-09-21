# PPTX 원문과 변환된 PDF 를 대조해서 LibreOffice 가 글자를 잘라먹은 쪽을 찾는다.
#
# 왜 필요한가: PowerPoint 는 텍스트 상자를 넘친 글자를 상자 밖으로 그려주는데
# LibreOffice 는 상자에서 잘라버린다. 폰트가 대체되면 폭이 달라져서 이 일이 생긴다.
# 실제로 L01 에서 "primary inputs and outputs" 가 "primary inputs" 로 잘렸다.
# 의미가 바뀌는 잘림이라 노트에 그대로 옮기면 틀린 노트가 된다.
#
# 쪽 번호가 어긋나는 것은 pagecount.mjs 가 잡는다. 이 스크립트는 쪽 수가 같은데
# 내용이 빠진 경우를 잡는다.
#
# 사용법: python scripts/clipcheck.py "lecture/07_Pipelined CPU Design.pptx" slides/L06-pipelined-cpu-design.pdf

import json
import os
import re
import subprocess
import sys
import zipfile
from xml.etree import ElementTree as ET

NODE_SNIPPET = r"""
import { readFileSync } from 'node:fs';
const { getDocument } = await import('pdfjs-dist/legacy/build/pdf.mjs');
const d = await getDocument({ data: new Uint8Array(readFileSync(process.argv[1])) }).promise;
const out = [];
for (let i = 1; i <= d.numPages; i++) {
  const tc = await (await d.getPage(i)).getTextContent();
  out.push(tc.items.map(it => it.str).join(' '));
}
process.stdout.write(JSON.stringify(out));
"""


def pptx_slides(path):
    """슬라이드별 본문 텍스트. 발표자 노트는 뺀다 (PDF 에 안 들어가므로)."""
    z = zipfile.ZipFile(path)
    names = sorted(
        (n for n in z.namelist() if re.match(r'ppt/slides/slide\d+\.xml$', n)),
        key=lambda n: int(re.search(r'(\d+)', n.split('/')[-1]).group(1)),
    )
    out = []
    for n in names:
        root = ET.fromstring(z.read(n))
        out.append(' '.join(
            t.text for t in root.iter() if t.tag.endswith('}t') and t.text
        ))
    return out


def pdf_pages(path):
    node = os.environ.get('NODE', 'node')
    r = subprocess.run(
        [node, '--input-type=module', '-e', NODE_SNIPPET, os.path.abspath(path)],
        capture_output=True, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    )
    if r.returncode != 0:
        sys.exit('node 실패:\n' + r.stderr.decode('utf-8', 'replace'))
    return json.loads(r.stdout.decode('utf-8'))


def words(s):
    """PPTX 쪽에서 찾을 낱말. 짧은 낱말은 우연히 맞아버려서 뺀다."""
    return [w for w in re.findall(r'[A-Za-z0-9]+', s.lower()) if len(w) > 2]


def haystack(s):
    """PDF 쪽 텍스트를 기호 없는 한 덩어리로 만든다.

    낱말 단위로 비교하면 안 된다. 자간이 넓은 텍스트를 pdf.js 가 글자 하나씩
    쪼개서 내놓기 때문에 "S l i d e s" 가 되어 멀쩡한 쪽이 전부 걸린다.
    실제로 L06 1쪽의 부제가 이렇게 오탐이 났다. 붙여서 부분 문자열로 찾는다.
    """
    return re.sub(r'[^a-z0-9]', '', s.lower())


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__ or '사용법: clipcheck.py <pptx> <pdf>')
    pptx, pdf = sys.argv[1], sys.argv[2]
    slides, pages = pptx_slides(pptx), pdf_pages(pdf)

    print(f'PPTX {len(slides)} 장  /  PDF {len(pages)} 쪽')
    if len(slides) != len(pages):
        print('쪽 수가 다르다. 숨김 슬라이드 변환을 먼저 고칠 것 (pagecount.mjs 참조)')

    flagged = 0
    for i in range(min(len(slides), len(pages))):
        hay = haystack(pages[i])
        missing = [w for w in words(slides[i]) if w not in hay]
        if missing:
            flagged += 1
            print(f'\np{i + 1}  PDF 에서 빠진 낱말 {len(missing)} 개')
            print('   ' + ' '.join(missing[:25]) + (' ...' if len(missing) > 25 else ''))

    print(f'\n{flagged} 쪽에서 잘림 의심. 0 이면 통과.')
    if flagged:
        print('해당 쪽은 렌더해서 눈으로 볼 것:  node scripts/render-slides.mjs <pdf> <쪽>')


main()
