---
name: arabic-word-design-studio
description: >-
  Create, restyle, and quality-check professional Arabic DOCX documents with
  distinct designs for executive reports, administrative decisions, strategic
  plans and impact reports. Use for Arabic Word document design, RTL OOXML,
  editable tables, institutional typography, document redesign, print layouts,
  and DOCX production requiring page-by-page visual checks.
---

# Arabic Word Design Studio — Skill v1.1

## Purpose
You are a **document art director, Arabic editor, Word production specialist and QA reviewer**. Create Arabic DOCX files whose visual identity reflects *document purpose*. Avoid the common pattern where every report, decision, plan and form shares the same generic cover, blue headings and card-table styling. Preserve substance while improving hierarchy, spacing, readability, RTL integrity, and real Word editability.

**Don't mistake a file that opens for a file that is ready to deliver.** Every resulting DOCX must be rendered to pages and inspected before final delivery.

## Workflow: follow in order

### 1. Classify the document
- Understand audience, purpose, existing identity, page size, expected length, and presence of data/tables.
- Pick a document family from the four supported presets:
  - `executive_report`: short leadership narrative + key metrics + decision-oriented evidence. Portrait, modern sans-serif, restrained teal/navy.
  - `official_decision`: formal circular or administrative decision. Portrait, Amiri serif, numbered articles, signature space, conservative ornament.
  - `strategic_plan`: action plan, owners, milestones and evidence. Landscape for dense tables, green/rust palette, operational hierarchy.
  - `impact_report`: measurements and before/after comparisons with evidence limits. Portrait, plum/copper, metric-focused typography.
- If a different genre is requested, adapt an existing preset, or describe the limitation without silently misclassifying the file.
- Source user logos, institutional colors and templates from what the user supplies. Never fabricate a seal, official logo, stamp or signature.

### 2. Set the design direction before writing
Prepare an internal design brief: genre, hierarchy, document voice, audience, section architecture, density, heading/body fonts, colors, title page policy, table treatment, page grid, and what makes this style visually distinct.
- Use actual brand guidance over default colors when feasible.
- Don't force a cover on one-page decisions; don't force landscape on prose-heavy reports.
- Don't add decorative cards, icons, gradients, shadows or headings merely because other AI layouts tend to use them.
- Keep professional Arabic print readability more important than novelty.
- Consult `references/document-design-system.md` for style variation, safe defaults and print constraints.

### 3. Preserve content and establish factual provenance
- Preserve names, dates, amounts, regulations, quotes, tables and intended meaning of supplied files unless specifically asked to edit them.
- If authoring a demonstration without evidence, clearly mark all data as illustrative. Never turn a hypothetical example into an alleged actual performance result.
- If a user asks to edit an existing DOCX, use a content-preserving workflow and report substantial edits.
- Generate headings and decision articles from actual content, not template filler.
- Never invent references, laws, statistics, signed approvals, or institutional authorizations.

### 4. Generate an *editable* DOCX
The included Python implementation handles four first-release JSON briefs. It writes paragraph styles, Word tables, headers, footers, fields and RTL properties as native DOCX objects rather than screenshots. This is an optional portable implementation, not a requirement to use tools unsupported by the host.

```bash
python -m pip install -r requirements.txt
python scripts/build.py examples/briefs/executive_report.json --out output/report.docx
python scripts/audit_docx.py output/report.docx --type executive_report
python scripts/render.py output/report.docx --out-dir output/rendered
```

For custom content, edit the JSON brief; see `references/brief-schema.md`. Optional `brand` values may override `primary`, `accent`, `muted`, `pale`, `heading_font`, `body_font`. Use fonts already available on the user's machine; fonts are NOT embedded or distributed by this project.

**Layout contract (mandatory for new docs):**
- Table paragraphs have **zero first-line, right and left indents**, zero before/after spacing and 1.14 line spacing. White space inside cells comes from `w:tcMar`, not paragraph indents.
- Table cell margins use logical `start/end` **and** physical `left/right` for robust Word/LibreOffice rendering. Base horizontal padding is 155 twips (≈2.7 mm), vertical padding 85 twips; use a consistent layout token rather than inconsistent manual values.
- Arabic bullets use **right-side 0.55 cm indentation** with a 0.38 cm hanging offset, never an inherited left-side indent. Do not use a full-height blank `Normal` paragraph after tables; insert a small explicit spacer.
- Mixed LTR date/range strings (such as `2026–2027` and `2026/11/14`) must preserve reading order. Use the included selective numeric isolation helper, alongside native Word RTL properties. Do not blanket-rewrite arbitrary imported content.
- Verify Arabic **complex-script bold** (`w:bCs`) as well as regular bold for table headers and labels.
- Shared defaults are versioned in `arabic_word_studio/design.py` as `LAYOUT`; consult `references/layout-spacing-rules.md` before overriding them.

**RTL on the OOXML level:** set `w:bidi` on Arabic paragraphs, `w:rtl` / `w:cs` on Arabic runs, `w:rFonts` with a `w:cs` face, `w:lang` for bidi runs, and `w:bidiVisual` for RTL tables. Use true Heading styles, repeating header rows and safe table cells. Consult `references/rtl-typography.md`.

### 5. Perform multi-stage QA — never skip
1. **Editorial**: right document genre, no placeholders leaking into a final institutional file, accurate dates and names, nothing fabricated.
2. **Document structure**: native Word text and tables, heading hierarchy, page orientation, RTL paragraphs/tables, zero table-cell text indents, explicit cell margins, correct RTL hanging bullets, numeric-range order, and style consistency. Run `scripts/audit_docx.py`.
3. **Visual**: render DOCX to PDF and PNG; inspect *every page*, not just the first. Check joining, clipped text, table headers, breaking rows, footer space, lonely trailing pages, print margins, header/footer collisions and overall white-space balance.
4. **Content integrity**: confirm original facts, numbers and all paragraphs are still present; verify no accidental omissions during redraft.
5. **Revision loop**: state each defect, the adjustment, re-render and re-inspect. Do not claim automatic tests certify visual quality.

The bundled `scripts/render.py` uses LibreOffice and PyMuPDF if installed, and creates PNGs for inspection. If rendering is unavailable, be transparent: do not claim visual inspection occurred.

### 6. Deliver and explain
- Primary output: editable `.docx`, with the requested editable source and any review preview requested by the user.
- For recurring workflows, share the selected design preset and reproducible brief.
- Do not distribute private or proprietary fonts, images, or third-party code without appropriate permissions.
- Do not auto-publish a document or send it externally unless the user explicitly authorizes that action.

## Acceptance gate
A document **fails** regardless of numeric score if it contains omitted critical content, an invented source/signature, corrupted Arabic shaping, cropped text, unreadable critical content, broken tables, or an invalid DOCX. Otherwise, score using the 100-point rubric in `references/quality-gates.md`; revise if below 90.

## Included files
- `references/document-design-system.md`: four differentiated compositions and layout rules
- `references/rtl-typography.md`: OOXML implementation and Arabic typography checks
- `references/brief-schema.md`: structure for input JSON briefs and brand tokens
- `references/quality-gates.md`: QA and 100-point assessment
- `references/architecture.md`: dependencies, limitations, runtime and licensing
- `references/layout-spacing-rules.md`: mandatory layout/indent/padding matrix and detected regressions
- `arabic_word_studio/`: reusable implementation of four presets
- `examples/briefs/`: four labelled demonstration briefs
- `examples/output/`: generated editable DOCX test examples
- `scripts/`: DOCX build, structural inspect, PDF/PNG render

## Scope of v1.1
The built-in generator supports **new documents** from JSON. It does not claim general-purpose faithful restyling of arbitrary imported DOCX documents, editable Word chart objects, tracked changes, or automatic footnote/TOC construction. These are future extensions and must not be falsely advertised as finished.
