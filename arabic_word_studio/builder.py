"""Editable, style-aware Arabic DOCX generator (first release)."""
from __future__ import annotations
import json
import re
from dataclasses import replace
from pathlib import Path
from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.section import WD_ORIENT
from docx.shared import Cm, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from .design import PRESETS, get_preset, LAYOUT
from .rtl import (
    rtl_paragraph, rtl_run, rtl_style, rtl_table, cell_fill, set_cell_border,
    repeat_header, cannot_split, field, paragraph_rule, set_cell_margin, complex_font_size,
    reset_cell_paragraph, complex_bold,
)


def rgb(hexstr):
    return RGBColor.from_string(hexstr.lstrip("#"))


def _p(container, text='', style=None, font=None, bold=False, color=None, align=None):
    p = container.add_paragraph(style=style)
    rtl_paragraph(p, align or WD_ALIGN_PARAGRAPH.RIGHT)
    if text:
        r = rtl_run(p.add_run(str(text)), font)
        if color: r.font.color.rgb = rgb(color)
        if bold: complex_bold(r)
    return p


def _style(doc, name, preset, size, color, bold=False, space_before=0, space_after=5, keep=False):
    st = doc.styles[name] if name in doc.styles else doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
    rtl_style(st, preset.heading_font if name in ("Title","Heading 1","Heading 2","Studio Label","Studio Metric Number") else preset.body_font)
    st.font.size = Pt(size)
    szcs = st._element.rPr.find(qn("w:szCs"))
    if szcs is None:
        szcs = OxmlElement("w:szCs")
        st._element.rPr.append(szcs)
    szcs.set(qn("w:val"), str(round(size*2)))
    st.font.color.rgb = rgb(color)
    st.font.bold = bold
    bc=st._element.rPr.find(qn("w:bCs"))
    if bc is None:
        bc=OxmlElement("w:bCs"); st._element.rPr.append(bc)
    bc.set(qn("w:val"), "1" if bold else "0")
    pf = st.paragraph_format
    if name == "Heading 1": space_before = 12
    if name == "Studio Body": space_after = 4
    pf.space_before, pf.space_after = Pt(space_before), Pt(space_after)
    # Word defaults and imported Normal styles can carry hidden indents.
    pf.left_indent = Pt(0)
    pf.right_indent = Pt(0)
    pf.first_line_indent = Pt(0)
    pf.line_spacing = 1.23 if name in ("Normal", "Studio Body") else 1.13
    if keep: pf.keep_with_next = True
    # Existing default Word styles retain OOXML style inheritance and remain editable.
    return st


def _configure(doc, preset):
    sec = doc.sections[0]
    sec.page_height, sec.page_width = Cm(29.7), Cm(21)
    if preset.orientation == "landscape":
        sec.orientation = WD_ORIENT.LANDSCAPE
        sec.page_height, sec.page_width = Cm(21), Cm(29.7)
    sec.left_margin = sec.right_margin = Cm(preset.margin_cm)
    sec.top_margin, sec.bottom_margin = Cm(2.25), Cm(1.75)
    sec.header_distance, sec.footer_distance = Cm(.95), Cm(.9)
    _style(doc,"Normal",preset,preset.body_size,preset.primary,space_after=6)
    _style(doc,"Title",preset,preset.title_size,preset.primary,bold=True,space_after=13,keep=True)
    _style(doc,"Subtitle",preset,11,preset.muted,space_after=9,keep=True)
    _style(doc,"Heading 1",preset,preset.h1_size,preset.primary,bold=True,space_before=17,space_after=8,keep=True)
    _style(doc,"Heading 2",preset,12.5,preset.primary,bold=True,space_before=9,space_after=5,keep=True)
    _style(doc,"Studio Label",preset,9,preset.accent,bold=True,space_after=6,keep=True)
    _style(doc,"Studio Body",preset,preset.body_size,preset.primary,space_after=7)
    _style(doc,"Studio Small",preset,8,preset.muted,space_after=4)
    _style(doc,"Studio Table",preset,9,preset.primary,space_after=0)
    _style(doc,"Studio Table Header",preset,9,preset.primary,bold=True,space_after=0)
    _style(doc,"Studio Bullet",preset,preset.body_size,preset.primary,space_after=6)
    bullet = doc.styles["Studio Bullet"].paragraph_format
    bullet.right_indent = Cm(LAYOUT.bullet_right_indent_cm)
    bullet.left_indent = Pt(0)
    bullet.first_line_indent = Cm(-LAYOUT.bullet_hanging_cm)
    _style(doc,"Studio Spacer",preset,2,preset.primary,space_after=0)
    _style(doc,"Studio Metric Number",preset,30,preset.accent,bold=True,space_after=0)
    return sec


def _header_footer(doc,preset,brief):
    sec=doc.sections[0]
    h=sec.header
    h.is_linked_to_previous=False
    p=h.paragraphs[0]
    rtl_paragraph(p)
    p.paragraph_format.space_before=Pt(0)
    p.paragraph_format.space_after=Pt(0)
    r=rtl_run(p.add_run(brief.get("organization", "")),preset.body_font)
    r.bold=True
    r.font.size=Pt(8.5)
    r.font.color.rgb=rgb(preset.muted)
    paragraph_rule(p,preset.accent,6 if preset.name != 'official_decision' else 10)
    f=sec.footer
    p=f.paragraphs[0]
    rtl_paragraph(p)
    p.paragraph_format.space_before=Pt(0)
    p.paragraph_format.space_after=Pt(0)
    r=rtl_run(p.add_run(brief.get("footer_note", "نموذج توضيحي") + "   •   "),preset.body_font)
    r.font.size=Pt(8)
    r.font.color.rgb=rgb(preset.muted)
    field(p, "PAGE")


def _title_block(doc,preset,brief):
    if preset.cover:
        doc.add_paragraph('')
        doc.add_paragraph('')
        _p(doc,brief.get("eyebrow","تقرير توضيحي"),"Studio Label",preset.heading_font)
        p=_p(doc,brief["title"],"Title",preset.heading_font)
        p.paragraph_format.space_before=Pt(12)
        paragraph_rule(p,preset.accent,20)
        _p(doc,brief.get("subtitle",""),"Subtitle",preset.body_font)
        _p(doc,f"{brief.get('date','')}  |  {brief.get('prepared_by','')}","Studio Small",preset.body_font)
        if brief.get("summary"):
            doc.add_paragraph('')
            _p(doc,"الرسالة الأساسية", "Heading 2",preset.heading_font)
            _p(doc,brief["summary"],"Studio Body",preset.body_font)
        if brief.get("cover_metrics"):
            if preset.name == "impact_report":
                _impact_snapshot(doc,preset,brief["cover_metrics"])
            else:
                _metrics(doc,preset,brief["cover_metrics"])
        p = doc.add_paragraph()
        rtl_paragraph(p)
        p.add_run().add_break(WD_BREAK.PAGE)
    elif preset.name == "official_decision":
        _p(doc,"المملكة / المؤسسة النموذجية", "Studio Small",preset.body_font)
        p=_p(doc,brief.get("eyebrow","قرار إداري"),"Studio Label",preset.heading_font)
        p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        p=_p(doc,brief["title"],"Title",preset.heading_font,align=WD_ALIGN_PARAGRAPH.CENTER)
        paragraph_rule(p,preset.accent,10)
        _p(doc,f"رقم القرار: {brief.get('reference','—')}     |     التاريخ: {brief.get('date','—')}","Studio Small",preset.body_font,align=WD_ALIGN_PARAGRAPH.CENTER)
    else:
        _p(doc,brief.get("eyebrow","خطة تنفيذية"),"Studio Label",preset.heading_font)
        p=_p(doc,brief["title"],"Title",preset.heading_font)
        paragraph_rule(p,preset.accent,13)
        _p(doc,f"{brief.get('subtitle','')}  ·  {brief.get('date','')}","Subtitle",preset.body_font)


def _cell_text(cell,value,preset,header=False):
    cell.text=''
    p=cell.paragraphs[0]
    p.style='Studio Table Header' if header else 'Studio Table'
    reset_cell_paragraph(p)
    r=rtl_run(p.add_run(str(value)),preset.body_font)
    if header: complex_bold(r)
    set_cell_margin(cell)
    cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER


def _spacer(doc, height=LAYOUT.table_spacer_pt):
    """A controlled spacer, not an inherited full-height blank Normal line."""
    p=doc.add_paragraph(style="Studio Spacer")
    p.paragraph_format.line_spacing=Pt(height)
    p.paragraph_format.space_before=Pt(0)
    p.paragraph_format.space_after=Pt(0)
    return p


def _table(doc,preset,data):
    headers=data.get('headers') or []
    rows=data.get('rows') or []
    if not headers or not rows: return
    for idx,row in enumerate(rows):
        if len(row)!=len(headers):
            raise ValueError(f"Table row {idx} has {len(row)} cells but expected {len(headers)}")
    t=doc.add_table(rows=1, cols=len(headers))
    t.autofit=True
    t.alignment=WD_TABLE_ALIGNMENT.CENTER
    rtl_table(t)
    for j,v in enumerate(headers):
        c=t.rows[0].cells[j]
        _cell_text(c,v,preset,True)
        cell_fill(c,preset.primary)
        for run in c.paragraphs[0].runs:
            run.font.color.rgb=RGBColor(255,255,255)
            complex_bold(run)
    repeat_header(t.rows[0])
    for i,row in enumerate(rows):
        cells=t.add_row().cells
        for j,v in enumerate(row):
            _cell_text(cells[j],v,preset)
            if i % 2 == 0: cell_fill(cells[j],preset.pale)
            set_cell_border(cells[j],"bottom",color="E2E6E9",size=5)
        cannot_split(t.rows[i+1])
    _spacer(doc)


def _impact_snapshot(doc,preset,items):
    """An analytical before/after spread, deliberately unlike executive KPI tiles."""
    if len(items)<2:
        _metrics(doc,preset,items)
        return
    t=doc.add_table(rows=1,cols=2)
    rtl_table(t)
    for idx,it in enumerate(items[:2]):
        c=t.cell(0,idx)
        cell_fill(c,preset.pale if idx==0 else preset.primary)
        c.text=''
        set_cell_margin(c,220,200,180,200)
        p=c.paragraphs[0]
        reset_cell_paragraph(p)
        r=rtl_run(p.add_run(it['label']),preset.body_font)
        complex_bold(r)
        complex_font_size(r,10)
        r.font.color.rgb=rgb(preset.primary if idx==0 else 'FFFFFF')
        p2=_p(c,str(it['value']),"Studio Metric Number",preset.heading_font)
        reset_cell_paragraph(p2)
        for r in p2.runs:
            complex_font_size(r,30)
            r.font.color.rgb=rgb(preset.accent if idx==0 else 'FFFFFF')
    if len(items)>2:
        change=items[2]
        p=_p(doc,f"{change['label']}:  {change['value']}  {change.get('note','')}","Heading 2",preset.heading_font)
        p.paragraph_format.space_before=Pt(14)
        paragraph_rule(p,preset.accent,7)


def _metrics(doc,preset,items):
    if not items:return
    for begin in range(0,len(items),3):
        part=items[begin:begin+3]
        t=doc.add_table(rows=1,cols=len(part))
        rtl_table(t)
        for i,it in enumerate(part):
            c=t.cell(0,i)
            cell_fill(c,preset.pale)
            c.text=''
            set_cell_margin(c,160,160,160,160)
            p=c.paragraphs[0]
            reset_cell_paragraph(p)
            r=rtl_run(p.add_run(str(it['value'])),preset.heading_font)
            complex_font_size(r,23)
            complex_bold(r)
            r.font.color.rgb=rgb(preset.accent)
            p2=_p(c,it['label'],"Studio Table",preset.body_font)
            reset_cell_paragraph(p2)
            if it.get('note'):
                note=_p(c,it['note'],"Studio Small",preset.body_font)
                reset_cell_paragraph(note)
        _spacer(doc)


def _section(doc,preset,item):
    heading=item.get('heading')
    if heading:
        p=_p(doc,heading,"Heading 1",preset.heading_font)
        paragraph_rule(p,preset.accent,5 if preset.name!='official_decision' else 8)
    for line in item.get('paragraphs',[]):
        _p(doc,line,"Studio Body",preset.body_font)
    for bullet in item.get('bullets',[]):
        p=_p(doc,f"•  {bullet}","Studio Bullet",preset.body_font)
        p.paragraph_format.left_indent=Pt(0)
        p.paragraph_format.right_indent=Cm(LAYOUT.bullet_right_indent_cm)
        p.paragraph_format.first_line_indent=Cm(-LAYOUT.bullet_hanging_cm)
    if item.get('metrics'):_metrics(doc,preset,item['metrics'])
    if item.get('table'):_table(doc,preset,item['table'])
    if item.get('steps'):
        _table(doc,preset,{"headers":["المرحلة","المسؤول","موعد الإنجاز","دليل التحقق"],"rows":[[s.get('title',''),s.get('owner',''),s.get('due',''),s.get('evidence','')] for s in item['steps']]})


def _decision_articles(doc,preset,brief):
    d=brief['decision']
    _p(doc,d.get('preamble',''),"Studio Body",preset.body_font)
    _p(doc,"تقرر ما يأتي:","Heading 2",preset.heading_font)
    for idx,article in enumerate(d['articles'],1):
        p=_p(doc,f"المادة ({idx}): {article['title']}","Heading 2",preset.heading_font)
        p.paragraph_format.keep_with_next=True
        _p(doc,article['text'],"Studio Body",preset.body_font)
    doc.add_paragraph('')
    p=_p(doc,d.get('signature_title','المدير العام'),"Studio Small",preset.body_font)
    p.paragraph_format.keep_with_next=True
    _p(doc,d.get('signature_name','الاسم / التوقيع'),"Heading 2",preset.heading_font)


def validate_brief(brief):
    if not isinstance(brief,dict): raise ValueError('Brief must be JSON object')
    for key in ('document_type','title'):
        if not brief.get(key): raise ValueError(f'Missing required field: {key}')
    get_preset(brief['document_type'])
    if brief['document_type']=='official_decision' and not brief.get('decision',{}).get('articles'):
        raise ValueError('Official decision must include decision.articles')
    if brief['document_type']!='official_decision' and not brief.get('sections'):
        raise ValueError('This document type requires sections')


def build_document(brief,out_path):
    validate_brief(brief)
    preset=get_preset(brief['document_type'])
    brand=brief.get("brand", {})
    allowed={"heading_font", "body_font", "primary", "accent", "muted", "pale"}
    unknown=set(brand)-allowed
    if unknown: raise ValueError(f"Unsupported brand overrides: {sorted(unknown)}")
    for key in ("primary", "accent", "muted", "pale"):
        if key in brand and not re.fullmatch(r"#?[0-9a-fA-F]{6}", brand[key]):
            raise ValueError(f"Color {key} must be six hex digits")
    brand={k: (v.lstrip("#").upper() if k in ("primary", "accent", "muted", "pale") else v) for k,v in brand.items()}
    preset=replace(preset, **brand)
    doc=Document()
    _configure(doc,preset)
    _header_footer(doc,preset,brief)
    _title_block(doc,preset,brief)
    if preset.name=='official_decision':
        _decision_articles(doc,preset,brief)
    else:
        for item in brief.get('sections',[]): _section(doc,preset,item)
    doc.core_properties.title=brief['title']
    doc.core_properties.subject='Arabic Word Design Studio sample' if brief.get('sample') else 'Arabic Word Design Studio'
    doc.core_properties.author=brief.get('prepared_by','Arabic Word Design Studio')
    output=Path(out_path)
    output.parent.mkdir(parents=True,exist_ok=True)
    doc.save(output)
    return output


def build_from_json(path,out_path):
    with open(path,encoding='utf-8') as f: brief=json.load(f)
    return build_document(brief,out_path)
