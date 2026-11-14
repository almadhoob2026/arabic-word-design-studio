# Acceptance rubric — 100 points

| Dimension | Points |
| --- | ---: |
| Genre suitability and visual differentiation | 20 |
| Arabic typography, RTL and hierarchy | 20 |
| Page balance, breaks, header/footer placement | 20 |
| Editable tables, metrics and other document objects | 15 |
| Accurate content and complete preservation | 15 |
| Valid, reproducible DOCX and useful source | 10 |

**Blocking defects** (failure even if score ≥90): missing critical paragraph/data, invented signed approval, distorted Arabic, content clipped or overlapping, broken table, unreadable critical text, corrupted DOCX.

## Mandatory delivery sequence
1. Validate source brief and all facts.
2. Generate DOCX and inspect OOXML with `scripts/audit_docx.py`.
3. Render to PDF and page PNGs using `scripts/render.py` (requires local LibreOffice).
4. Visually inspect every page, including the last page and dense tables.
5. Check whether final page has an accidental one-row spillover; adjust space or reorganize content when justified.
6. Record issues and corrections, then re-render.
7. Deliver DOCX; expose extra PDF/PNG previews only when helpful/requested.

## Checks automation cannot certify
A structural audit confirms elements exist and certain RTL properties are present; it cannot guarantee aesthetics, visual accessibility, absence of a misleading claim or equivalence across Word and LibreOffice versions. No automated quality score should be presented as an objective guarantee of professional design.
