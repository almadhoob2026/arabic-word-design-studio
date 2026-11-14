"""Structural/RTL audit, complementary to page-by-page visual checks."""
from pathlib import Path
from zipfile import ZipFile
from lxml import etree
from docx import Document
from .design import PRESETS

NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}


def inspect_docx(path, *, expected_type=None):
    p=Path(path)
    failures=[]; warnings=[]
    if not p.is_file(): return {'passed':False,'failures':['File does not exist'], 'warnings':[]}
    try:
        with ZipFile(p) as z:
            document=etree.fromstring(z.read('word/document.xml'))
            paragraphs=document.xpath('//w:body//w:p[w:r]',namespaces=NS)
            tables=document.xpath('//w:body//w:tbl',namespaces=NS)
            rhs=sum(bool(x.xpath('./w:pPr/w:bidi[@w:val="1"]',namespaces=NS)) for x in paragraphs)
            bad=[i for i,x in enumerate(paragraphs,1) if not x.xpath('./w:pPr/w:bidi[@w:val="1"]',namespaces=NS)]
            if bad: warnings.append(f'{len(bad)} non-RTL body paragraphs (indexes: {bad[:8]})')
            for t in tables:
                if not t.xpath('./w:tblPr/w:bidiVisual',namespaces=NS):
                    failures.append('A table is missing w:bidiVisual')
            for t in tables:
                if not t.xpath('./w:tr[1]/w:trPr/w:tblHeader',namespaces=NS):
                    # Metric mini-tables intentionally have no header row.
                    rows=t.xpath('./w:tr',namespaces=NS)
                    if len(rows)>1: warnings.append('Multi-row table has no repeating header')
            textual=' '.join(document.xpath('//w:body//w:t/text()',namespaces=NS))
            if len(textual.strip())<100: failures.append('Too little document body text')
            styles=etree.fromstring(z.read('word/styles.xml'))
            if not styles.xpath('//w:style[@w:styleId="Heading1"]',namespaces=NS):
                failures.append('Heading 1 style is missing')
            d=Document(p)
            if expected_type in PRESETS:
                expected_landscape=PRESETS[expected_type].orientation=='landscape'
                if (d.sections[0].page_width>d.sections[0].page_height)!=expected_landscape:
                    failures.append('Page orientation does not match preset')
            return {'path':str(p),'passed':not failures,'paragraphs':len(paragraphs),
                    'rtl_paragraphs':rhs,'tables':len(tables), 'body_characters':len(textual),
                    'failures':failures,'warnings':warnings,
                    'note':'Structural checks do not establish visual quality. Inspect rendered page PNGs.'}
    except Exception as exc:
        return {'path':str(p),'passed':False,'failures':[str(exc)],'warnings':warnings}
