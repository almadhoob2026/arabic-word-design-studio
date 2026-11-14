"""Document-native OOXML helpers for Arabic right-to-left Word content."""
from docx.enum.text import WD_ALIGN_PARAGRAPH
import re

# Word/LibreOffice may visually reverse numeric ranges inside RTL text unless
# each LTR segment is isolated. Keep native w:bidi / w:rtl alongside LRM.
_LTR_RANGE = re.compile(r"(?<![A-Za-z0-9])(?:[0-9]{1,4}(?:[./–—\-][0-9]{1,4})+)(?![A-Za-z0-9])")

def isolate_numeric_ranges(value: str) -> str:
    """Preserve reading order for dates/ranges such as 2026–2027 in Arabic runs."""
    def wrap(match):
        if (match.start() > 0 and match.end() < len(match.string)
                and match.string[match.start()-1] == "\u200e"
                and match.string[match.end()] == "\u200e"):
            return match.group()
        return "\u200e" + match.group() + "\u200e"
    return _LTR_RANGE.sub(wrap, value)
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from .design import LAYOUT


def _child(parent, name):
    element = parent.find(qn(name))
    if element is None:
        element = OxmlElement(name)
        parent.append(element)
    return element


def rtl_paragraph(paragraph, alignment=WD_ALIGN_PARAGRAPH.RIGHT):
    paragraph.alignment = alignment
    ppr = paragraph._p.get_or_add_pPr()
    _child(ppr, "w:bidi").set(qn("w:val"), "1")
    return paragraph


def rtl_run(run, font_name=None):
    if run.text:
        run.text = isolate_numeric_ranges(run.text)
    rpr = run._r.get_or_add_rPr()
    _child(rpr, "w:rtl").set(qn("w:val"), "1")
    _child(rpr, "w:cs").set(qn("w:val"), "1")
    if font_name:
        fonts = _child(rpr, "w:rFonts")
        for key in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
            fonts.set(qn(key), font_name)
    lang = _child(rpr, "w:lang")
    lang.set(qn("w:bidi"), "ar-BH")
    return run


def rtl_style(style, font_name):
    style.font.name = font_name
    rpr = style._element.get_or_add_rPr()
    fonts = _child(rpr, "w:rFonts")
    for key in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        fonts.set(qn(key), font_name)
    _child(rpr, "w:rtl").set(qn("w:val"), "1")
    _child(rpr, "w:cs").set(qn("w:val"), "1")
    _child(rpr, "w:lang").set(qn("w:bidi"), "ar-BH")
    ppr = style._element.get_or_add_pPr()
    _child(ppr, "w:bidi").set(qn("w:val"), "1")


def rtl_table(table):
    tblpr = table._tbl.tblPr
    _child(tblpr, "w:bidiVisual").set(qn("w:val"), "1")
    return table


def cell_fill(cell, hex_color):
    tcpr = cell._tc.get_or_add_tcPr()
    _child(tcpr, "w:shd").set(qn("w:fill"), hex_color.lstrip("#"))


def set_cell_border(cell, side, *, color="D5D9DF", size=6):
    tcpr = cell._tc.get_or_add_tcPr()
    borders = _child(tcpr, "w:tcBorders")
    e = _child(borders, f"w:{side}")
    e.set(qn("w:val"), "single")
    e.set(qn("w:sz"), str(size))
    e.set(qn("w:color"), color.lstrip("#"))


def repeat_header(row):
    trpr = row._tr.get_or_add_trPr()
    _child(trpr, "w:tblHeader").set(qn("w:val"), "1")


def cannot_split(row):
    trpr = row._tr.get_or_add_trPr()
    _child(trpr, "w:cantSplit")


def field(paragraph, code):
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    run._r.append(begin)
    run2 = paragraph.add_run()
    instr = OxmlElement("w:instrText")
    instr.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    instr.text = f" {code} "
    run2._r.append(instr)
    run3 = paragraph.add_run()
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    run3._r.append(separate)
    paragraph.add_run("1")
    run4 = paragraph.add_run()
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run4._r.append(end)


def paragraph_rule(paragraph, color="C6CED7", size=10):
    ppr = paragraph._p.get_or_add_pPr()
    pbdr = _child(ppr, "w:pBdr")
    bottom = _child(pbdr, "w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(size))
    bottom.set(qn("w:space"), "4")
    bottom.set(qn("w:color"), color.lstrip("#"))


def keep_with_next(paragraph):
    paragraph.paragraph_format.keep_with_next = True


def set_cell_margin(cell, top=LAYOUT.table_padding_vertical_twips,
                    start=LAYOUT.table_padding_horizontal_twips,
                    bottom=LAYOUT.table_padding_vertical_twips,
                    end=LAYOUT.table_padding_horizontal_twips):
    """Set logical RTL and physical left/right margins for Word/LO compatibility.

    Values are twips (1/20 pt). Equal start/end avoids asymmetric padding
    when an editor ignores bidi-aware logical margins.
    """
    if any(v < 0 for v in (top, start, bottom, end)):
        raise ValueError("Cell margins cannot be negative")
    tcpr = cell._tc.get_or_add_tcPr()
    mar = _child(tcpr, "w:tcMar")
    for side, val in [("top", top), ("start", start), ("bottom", bottom),
                      ("left", end), ("right", start)]:
        x = _child(mar, f"w:{side}")
        x.set(qn("w:w"), str(val))
        x.set(qn("w:type"), "dxa")
    # A large share of viewers still honor only the older physical sides.
    for side, val in (("start", start), ("end", end)):
        x = _child(mar, f"w:{side}")
        x.set(qn("w:w"), str(val))
        x.set(qn("w:type"), "dxa")


def reset_cell_paragraph(paragraph):
    """Override inherited indentation and spacing within every table cell."""
    from docx.shared import Pt
    rtl_paragraph(paragraph)
    pf = paragraph.paragraph_format
    pf.left_indent = Pt(0)
    pf.right_indent = Pt(0)
    pf.first_line_indent = Pt(0)
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = LAYOUT.table_line_spacing
    return paragraph


def complex_bold(run, enabled=True):
    """Set Arabic complex-script bold alongside the ordinary run bold flag."""
    run.bold = enabled
    _child(run._r.get_or_add_rPr(), "w:bCs").set(qn("w:val"), "1" if enabled else "0")
    return run


def complex_font_size(run, point_size):
    """Set ordinary and complex-script font sizes (Word stores half-points)."""
    from docx.shared import Pt
    run.font.size = Pt(point_size)
    rpr=run._r.get_or_add_rPr()
    _child(rpr, "w:szCs").set(qn("w:val"), str(round(point_size*2)))
    return run
