"""Structural/RTL audit, complementary to page-by-page visual checks."""
from pathlib import Path
import re
from zipfile import ZipFile
from lxml import etree
from docx import Document
from .design import PRESETS

NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
LTR_RANGE = re.compile(r'(?<![A-Za-z0-9])[0-9]{1,4}(?:[./–—\-][0-9]{1,4})+(?![A-Za-z0-9])')


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
            # Layout regressions: a table can be RTL yet inherit hidden indents
            # or be rendered with zero padding in older Office/LibreOffice.
            checked_cells=0
            for table_index, table in enumerate(tables,1):
                for cell_index, cell in enumerate(table.xpath('./w:tr/w:tc',namespaces=NS),1):
                    checked_cells += 1
                    margins = cell.xpath('./w:tcPr/w:tcMar',namespaces=NS)
                    if not margins:
                        failures.append(f'Table {table_index}, cell {cell_index}: missing cell padding')
                    else:
                        sides={x.tag.split('}')[-1]:int(x.get(W+'w','0')) for x in margins[0]}
                        if any(sides.get(side,0)<120 for side in ('left','right','start','end')):
                            failures.append(f'Table {table_index}, cell {cell_index}: horizontal padding too small or missing')
                    for paragraph in cell.xpath('./w:p',namespaces=NS):
                        if not ''.join(paragraph.xpath('.//w:t/text()',namespaces=NS)).strip():
                            continue
                        inds=paragraph.xpath('./w:pPr/w:ind',namespaces=NS)
                        if not inds or any(inds[0].get(W+side) != '0' for side in ('left','right','firstLine')):
                            failures.append(f'Table {table_index}, cell {cell_index}: inherited/nonzero text indent')
                        spacing=paragraph.xpath('./w:pPr/w:spacing',namespaces=NS)
                        if not spacing or any(spacing[0].get(W+side) != '0' for side in ('before','after')):
                            failures.append(f'Table {table_index}, cell {cell_index}: nonzero paragraph spacing')
            bullet_count=0
            for para in paragraphs:
                text=''.join(para.xpath('.//w:t/text()',namespaces=NS))
                if text.lstrip().startswith('•'):
                    bullet_count+=1
                    inds=para.xpath('./w:pPr/w:ind',namespaces=NS)
                    if not inds:
                        failures.append('RTL bullet missing indentation')
                    else:
                        right=int(inds[0].get(W+'right','0'))
                        left=int(inds[0].get(W+'left','0'))
                        hanging=int(inds[0].get(W+'hanging','0'))
                        if right<=0 or left != 0 or hanging<=0:
                            failures.append('RTL bullet indentation is not right-hand hanging indent')
                if LTR_RANGE.search(text):
                    for m in LTR_RANGE.finditer(text):
                        if m.start()==0 or m.end()==len(text) or text[m.start()-1]!='\u200e' or text[m.end()]!='\u200e':
                            warnings.append('Numeric date/range might display in reverse RTL order')
                            break
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
                    'rtl_paragraphs':rhs,'tables':len(tables), 'table_cells_checked':checked_cells,
                    'rtl_bullets_checked':bullet_count, 'body_characters':len(textual),
                    'failures':failures,'warnings':warnings,
                    'note':'Structural checks do not establish visual quality. Inspect rendered page PNGs.'}
    except Exception as exc:
        return {'path':str(p),'passed':False,'failures':[str(exc)],'warnings':warnings}
