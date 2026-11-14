import json
from pathlib import Path
import pytest
from docx import Document
from docx.oxml.ns import qn
from arabic_word_studio.builder import build_document, validate_brief
from arabic_word_studio.audit import inspect_docx
from arabic_word_studio.design import PRESETS

BRIEFS=Path(__file__).resolve().parents[1]/'examples'/'briefs'


@pytest.mark.parametrize('name', list(PRESETS))
def test_samples_build_and_pass_rtl_audit(name,tmp_path):
    brief=json.loads((BRIEFS/f'{name}.json').read_text(encoding='utf-8'))
    output=tmp_path/f'{name}.docx'
    build_document(brief,output)
    report=inspect_docx(output,expected_type=name)
    assert report['passed'],report
    assert report['rtl_paragraphs']>=report['paragraphs']-1
    assert report['body_characters']>300
    d=Document(output)
    assert d.core_properties.title==brief['title']
    assert (d.sections[0].page_width>d.sections[0].page_height)==(name=='strategic_plan')


@pytest.mark.parametrize('name', ['executive_report','strategic_plan','impact_report'])
def test_editable_table_and_rtl_ordering(name,tmp_path):
    brief=json.loads((BRIEFS/f'{name}.json').read_text(encoding='utf-8'))
    output=tmp_path/'out.docx';build_document(brief,output)
    tables=Document(output).tables
    assert tables
    assert all(t._tbl.tblPr.find(qn('w:bidiVisual')) is not None for t in tables)
    assert any(len(t.rows)>1 for t in tables)
    assert any(t.cell(0,0).text for t in tables)


def test_true_heading_styles(tmp_path):
    brief=json.loads((BRIEFS/'strategic_plan.json').read_text(encoding='utf-8'))
    path=tmp_path/'x.docx';build_document(brief,path)
    assert any(p.style.name=='Heading 1' for p in Document(path).paragraphs)


def test_invalid_brief_rejected():
    with pytest.raises(ValueError,match='Missing required'):
        validate_brief({'document_type':'impact_report'})
    with pytest.raises(ValueError,match='Unknown document type'):
        validate_brief({'document_type':'foo','title':'x','sections':[{'heading':'x'}]})


def test_invalid_table_shape_rejected(tmp_path):
    brief={'document_type':'strategic_plan','title':'x','sections':[{'table':{'headers':['a','b'],'rows':[['a']]}}]}
    with pytest.raises(ValueError,match='Table row'):
        build_document(brief,tmp_path/'x.docx')


def test_custom_brand_override(tmp_path):
    brief={'document_type':'executive_report','title':'x','sections':[{'heading':'السلام عليكم','paragraphs':['نص اختبار عربي متكامل.']*8}], 'brand':{'primary':'#654321','accent':'ABCDEF'}}
    out=tmp_path/'brand.docx';build_document(brief,out)
    assert out.exists()
    with pytest.raises(ValueError,match='six hex digits'):
        build_document({**brief,'brand':{'primary':'notacolor'}},tmp_path/'invalid.docx')
    with pytest.raises(ValueError,match='Unsupported brand'):
        build_document({**brief,'brand':{'unsafe':'value'}},tmp_path/'invalid2.docx')


def test_decision_articles_are_word_paragraphs(tmp_path):
    brief=json.loads((BRIEFS/'official_decision.json').read_text(encoding='utf-8'))
    out=tmp_path/'decision.docx';build_document(brief,out)
    paragraphs=[p.text for p in Document(out).paragraphs]
    assert any('المادة (1)' in p for p in paragraphs)
    assert any('التوقيع' in p for p in paragraphs)
