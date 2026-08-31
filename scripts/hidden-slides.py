# 숨김 슬라이드 번호를 찍는다.
#
# PowerPoint 기본 PDF 변환은 숨김 슬라이드를 빼버려서 PDF 쪽 번호가 슬라이드 번호와
# 어긋난다. 이 저장소는 숨김을 되살려서 변환하므로 (scripts/pptx2pdf.ps1) 어긋나지
# 않지만, 어느 장이 수업에서 안 넘어갔는지는 노트에 적어야 하므로 목록이 필요하다.
#
# 사용법: python scripts/hidden-slides.py "<pptx 경로>"

import os
import re
import sys
import zipfile
from xml.etree import ElementTree as ET

if len(sys.argv) < 2:
    sys.exit('사용법: python scripts/hidden-slides.py "<pptx 경로>" [...]')

for path in sys.argv[1:]:
    z = zipfile.ZipFile(path)
    names = sorted(
        (n for n in z.namelist() if re.match(r'ppt/slides/slide\d+\.xml$', n)),
        key=lambda n: int(re.search(r'(\d+)', n.split('/')[-1]).group(1)),
    )
    hidden = [
        i for i, n in enumerate(names, 1)
        if ET.fromstring(z.read(n)).get('show') == '0'
    ]
    print(f'{os.path.basename(path)}  총 {len(names)}장  숨김 {hidden or "없음"}')
