# 슬라이드 본문과 발표자 노트를 뽑는다.
#
# 발표자 노트에는 강사가 수업에서 할 말이 들어 있고, 슬라이드 본문에 없는 정보가 있다.
# 그래서 본문만 뽑으면 안 된다. 다만 노트는 초안이라 슬라이드와 어긋나는 일이 있으니
# 그대로 믿지 않는다.
#
# 사용법: python scripts/pptx-text.py "<pptx 경로>"
#   Windows 콘솔에서 UnicodeEncodeError가 나면 PYTHONIOENCODING=utf-8 을 앞에 붙인다.

import os
import re
import sys
import zipfile
from xml.etree import ElementTree as ET


def paragraphs(xml_bytes):
    """한 XML 안의 <a:p> 문단을 텍스트 줄로 편다."""
    root = ET.fromstring(xml_bytes)
    out = []
    for node in root.iter():
        if node.tag.endswith('}p'):
            text = ''.join(t.text or '' for t in node.iter() if t.tag.endswith('}t'))
            if text.strip():
                out.append(text.strip())
    return out


def slide_index(name):
    return int(re.search(r'(\d+)', name.split('/')[-1]).group(1))


def dump(path):
    z = zipfile.ZipFile(path)
    slides = sorted(
        (n for n in z.namelist() if re.match(r'ppt/slides/slide\d+\.xml$', n)),
        key=slide_index,
    )
    print('=' * 70)
    print('FILE:', os.path.basename(path))
    print('=' * 70)
    for i, name in enumerate(slides, 1):
        root = ET.fromstring(z.read(name))
        hidden = root.get('show') == '0'
        print(f'\n--- slide {i}{"  [HIDDEN]" if hidden else ""} ---')
        for line in paragraphs(z.read(name)):
            print(' ', line)
        notes = f'ppt/notesSlides/notesSlide{i}.xml'
        if notes in z.namelist():
            lines = paragraphs(z.read(notes))
            # 노트 XML 끝에는 슬라이드 번호 자리표시자가 딸려 온다. 숫자만 있는 줄은 버린다.
            lines = [l for l in lines if not l.isdigit()]
            if lines:
                print('  [NOTES]')
                for line in lines:
                    print('   ', line)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('사용법: python scripts/pptx-text.py "<pptx 경로>" [...]')
    for p in sys.argv[1:]:
        dump(p)
