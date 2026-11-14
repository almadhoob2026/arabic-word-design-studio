# Document design system — intentionally distinct genres

## Genre before style
The document's function selects its architecture. A leadership report needs a strong synthesis and evidence; a formal decision needs articles and signatures; a plan needs accountability; an impact report needs precise comparison and cautious attribution. Simply recoloring the same template is not differentiation.

## Preset comparison

| Genre | Format | Typeface | Palette | Priority | Avoid |
| --- | --- | --- | --- | --- | --- |
| Executive report | A4 portrait; cover + evidence | Noto Kufi Arabic / Noto Sans Arabic | navy + teal | summary, three key metrics, decisions | long prose cover |
| Official decision | A4 portrait; no cover | Amiri | charcoal + muted gold | articles, reference number, approval space | decorative KPI cards |
| Strategic plan | A4 landscape | Noto Kufi Arabic / Noto Sans Arabic | green + rust | readable roadmap and responsibility tables | dense prose blocks |
| Impact report | A4 portrait; analytical cover | Noto Kufi Arabic / Noto Sans Arabic | plum + copper | baseline, follow-up, differences, limitations | equating association with causation |

## Typography
- Heading levels are genuine Word paragraph styles, not simply bigger bold runs.
- For Arabic, plan line breaks by linguistic units; avoid isolated prepositions at the end of lines.
- Word's complex-script font is set separately from the Latin font properties; test Arabic glyph joining and mixed Arabic/English codes after rendering.
- Decorative typography must not make body text difficult to read on A4 paper.
- No downloadable font file is packaged. Fallback fonts may cause pagination changes on systems where the intended font is missing.

## Tables
- Use native DOCX tables, not embedded table screenshots.
- RTL ordering is set in OOXML. Header row repeats across pages.
- Use subtle alternating fill in data-heavy genres; formal decisions need simple prose rather than table grids by default.
- Avoid detached lone rows on a final page when the content can be reorganized without omissions.

## Spacing and page flow
- Respect A4 paper margins; clear headers and footers.
- Keep each heading with its first text block.
- Avoid orphan last pages and uncontrolled blank pages.
- Preserve logical reading order with Word's own styles and paragraphs.
- An extra page is preferable to shrinking body text below a readable point size.

## Brand adaptation
Accept `brand` overrides for primary/accent/muted/pale colors and body/heading fonts. If the user supplies a detailed template, match it; a brand override changes style tokens, not the nature of the genre. Official documents should never invent seals, signatures or ministry logos.
