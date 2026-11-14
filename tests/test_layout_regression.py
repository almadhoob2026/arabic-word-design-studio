"""Regression checks for structural layout errors that visual snapshots revealed."""
import json
from pathlib import Path
from zipfile import ZipFile
from lxml import etree
import pytest
from docx import Document
from docx.shared import Cm, Pt
from arabic_word_studio.builder import build_document
from arabic_word_studio.rtl import isolate_numeric_ranges, set_cell_margin
from arabic_word_studio.audit import inspect_docx

ROOT=Path(__file__).resolve().parents[1]
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


def _xml(path):
    with ZipFile(path) as z:
        return etree.fromstring(z.read('word/document.xml'))


def _brief(name):
    return json.loads((ROOT/'examples'/'briefs'/f'{name}.json').read_text(encoding='utf-8'))


@pytest.mark.parametrize('name',['executive_report','strategic_plan','impact_report'])
def test_tables_have_native_padding_and_zero_indentation(name,tmp_path):
    docx=tmp_path/'result.docx'
    build_document(_brief(name),docx)
    root=_xml(docx)
    tables=root.xpath('//w:body/w:tbl', namespaces=NS)
    assert tables
    for t in tables:
        assert t.xpath('./w:tblPr/w:bidiVisual[@w:val="1"]',namespaces=NS)
        for cell in t.xpath('./w:tr/w:tc',namespaces=NS):
            tcMar=cell.xpath('./w:tcPr/w:tcMar',namespaces=NS)
            assert len(tcMar)==1
            data={x.tag.split('}')[-1]:int(x.get(W+'w')) for x in tcMar[0]}
            assert min(data[x] for x in ('left','right','start','end'))>=120
            for para in cell.xpath('./w:p',namespaces=NS):
                if not para.xpath('.//w:t',namespaces=NS):continue
                ind=para.xpath('./w:pPr/w:ind',namespaces=NS)
                assert len(ind)==1
                assert all(ind[0].get(W+x)=='0' for x in ('left','right','firstLine'))
                space=para.xpath('./w:pPr/w:spacing',namespaces=NS)
                assert len(space)==1
                assert space[0].get(W+'before')=='0'
                assert space[0].get(W+'after')=='0'
    report=inspect_docx(docx)
    assert report['passed'],report
    assert not report['warnings'],report


@pytest.mark.parametrize('name',['executive_report','strategic_plan','impact_report'])
def test_bullets_have_right_hand_hanging_indents(name,tmp_path):
    docx=tmp_path/'result.docx'
    build_document(_brief(name),docx)
    bullets=[p for p in Document(docx).paragraphs if p.text.strip().startswith('•')]
    assert bullets
    for p in bullets:
        fmt=p.paragraph_format
        assert abs(fmt.right_indent-Cm(.55)) <= Pt(.05)
        assert fmt.left_indent==Pt(0)
        assert abs(fmt.first_line_indent-Cm(-.38)) <= Pt(.05)


def test_numeric_ranges_stay_in_reading_order(tmp_path):
    assert isolate_numeric_ranges('عام 2026–2027')=='عام \u200e2026–2027\u200e'
    assert isolate_numeric_ranges('التاريخ 2026/11/14')=='التاريخ \u200e2026/11/14\u200e'
    assert isolate_numeric_ranges('المادة (1)')=='المادة (1)'
    path=tmp_path/'plan.docx';build_document(_brief('strategic_plan'),path)
    x=_xml(path)
    values=x.xpath('//w:body//w:t/text()',namespaces=NS)
    assert any('\u200e2026–2027\u200e' in val for val in values)


def test_table_headers_are_complex_script_bold(tmp_path):
    path=tmp_path/'plan.docx';build_document(_brief('strategic_plan'),path)
    xml=_xml(path)
    runs=xml.xpath('//w:tbl/w:tr[1]/w:tc/w:p/w:r',namespaces=NS)
    assert runs
    assert all(r.xpath('./w:rPr/w:bCs[@w:val="1"]',namespaces=NS) for r in runs if r.xpath('./w:t',namespaces=NS))


def test_negative_cell_margin_rejected():
    from docx import Document
    cell=Document().add_table(rows=1,cols=1).cell(0,0)
    with pytest.raises(ValueError,match='cannot be negative'):
        set_cell_margin(cell,start=-1)


def test_no_full_height_normal_blank_paragraph_between_table_and_heading(tmp_path):
    d=Document();from arabic_word_studio.design import get_preset
    from arabic_word_studio.builder import _configure,_table
    preset=get_preset('strategic_plan');_configure(d,preset)
    _table(d,preset,{'headers':['البيان'], 'rows':[['نص']]})
    assert d.paragraphs[-1].style.name=='Studio Spacer'
    assert d.paragraphs[-1].paragraph_format.line_spacing==Pt(5)
