# Arabic RTL and Word-native rendering

## Core OOXML
- Paragraph direction: `<w:pPr><w:bidi w:val="1"/></w:pPr>`.
- Run direction: `<w:rPr><w:rtl w:val="1"/></w:rPr>`.
- Complex script support: `w:cs`, `w:rFonts @w:cs`, `w:lang @w:bidi`.
- Table visual direction: `<w:tblPr><w:bidiVisual w:val="1"/></w:tblPr>`.
- Repeat table headings: `w:tblHeader` on header rows.
- Keep all cell content editable; avoid using RTL Unicode markers as a substitute for Word properties.

## QA cases
1. Arabic words with dots, hamza, shadda and tanween.
2. Mixed Arabic and dates (2026/11/14), percentages, and English abbreviations.
3. Arabic headings at all levels and bold text in tables.
4. Parentheses, ordered articles and nested clauses.
5. Text that wraps around table-cell boundaries.
6. Font substitution when viewed in Word rather than LibreOffice.

## Common failure modes
- A right-aligned paragraph is not necessarily RTL.
- A table visually right-aligned does not necessarily have RTL cell order.
- Setting only `style.font.name` may leave Arabic glyphs in a different `w:cs` fallback.
- Empty-cell or page-break paragraphs may be harmless but should not be confused with missing RTL on meaningful text.

## Editing existing documents
For complex arbitrary DOCX files, a single global `w:rtl` operation can corrupt mixed English fields, equations and special content. Handle by paragraph language and verify the actual appearance. First-release scripts generate new documents and do not offer an arbitrary-DOCX bulk rewrite.


## Mixed-direction numbers and horizontal spacing (v1.1)
- A paragraph marked RTL can still **visually reverse** a compound range such as `2026–2027` in some renderers. Reproducible visual testing demonstrated this issue in the strategic-plan subtitle.
- The implementation preserves native bidi properties and **selectively wraps numeric ranges** with Unicode LRM (`U+200E`) to preserve LTR date/range reading order. This is not a substitute for OOXML paragraph/run direction. The helper is idempotent; use it only for Arabic authoring, not arbitrary English passages.
- Table-cell paragraph indents must be zero. Table padding belongs in `w:tcMar`; use logical start/end and physical left/right properties to support multiple Word implementations.
- For Arabic list bullets use `w:ind @right` and `@hanging` rather than `@left`.
- Arabic table headers use both `w:b` and `w:bCs`, because complex-script glyphs may ignore Latin bold instructions.
