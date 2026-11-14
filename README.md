# Arabic Word Design Studio

**An open-source Claude-compatible skill for designing professional, editable, right-to-left Arabic Word documents.**

[الشرح بالعربية](README.ar.md) · [Skill instructions](SKILL.md) · [Examples](examples/briefs/) · [Quality rubric](references/quality-gates.md)

> **Version 1.0 — first tested release.** Four differentiated document presets, native Word typography and tables, OOXML RTL checks, and rendered-page review. Designed for *different document purposes*, not one generic visual template.

## What it does

| Genre | Layout | Default face | Content priorities |
| --- | --- | --- | --- |
| Executive report | A4 portrait + intro cover | Noto Kufi Arabic / Noto Sans Arabic | KPIs, synthesis, decisions |
| Official decision | A4 portrait, one-column official letter | Amiri | Articles, reference, signature |
| Strategic plan | A4 landscape | Noto Kufi Arabic / Noto Sans Arabic | Roadmap, owners, evidence |
| Impact report | A4 portrait + analytical cover | Noto Kufi Arabic / Noto Sans Arabic | Before/after, limitations, next steps |

- Real Heading paragraph styles, editable tables, header/footer and page number fields.
- Bidirectional paragraphs, complex-script run fonts, RTL table visual ordering and repeating table headings.
- Reproducible JSON brief with optional custom brand colors and fonts.
- Structural DOCX audit plus LibreOffice/PyMuPDF render-to-PNG QA workflow.
- Four **explicitly fictional** Arabic examples; no template data is asserted as factual.

## Preview

![Four sample document designs side by side](assets/preview.png)

## Quick start

**Prerequisites:** Python 3.10+, and LibreOffice for rendering. The generator can build DOCX without LibreOffice; visual QA cannot.

```bash
python -m pip install -r requirements.txt
python scripts/build.py examples/briefs/executive_report.json --out output/my-report.docx
python scripts/audit_docx.py output/my-report.docx --type executive_report
python scripts/render.py output/my-report.docx --out-dir output/preview
```

Customizing your organization, content and branding is done by editing the input JSON. For example:

```json
{
  "document_type": "executive_report",
  "title": "تقرير أداء",
  "organization": "المؤسسة النموذجية",
  "brand": { "primary": "20324B", "accent": "178F79", "heading_font": "Noto Kufi Arabic" },
  "sections": [
    { "heading": "الملخص", "paragraphs": ["اكتب هنا بياناتك الحقيقية أو النص المقدم من المستخدم."] }
  ]
}
```

**Testing**:

```bash
pytest -q
```

## Install as a Claude skill

- **Claude.ai:** package the skill folder as a ZIP (provided in release bundles); upload through the product's supported skill management interface where available.
- **Claude Code:** place this directory in `.claude/skills/arabic-word-design-studio/` (or the user's supported skills directory). Claude reads the root `SKILL.md` and can reference files relative to it.

> Skills provide instructions and local scripts. Availability of file creation, Python execution or browser/LibreOffice rendering depends on your Claude environment. A skill does not bypass unavailable tools.

## Limitations

This first release generates **new DOCX documents from structured JSON**. It does not yet faithfully restyle arbitrary imported Word files, provide live Word charts/TOC/footnotes, handle tracked changes, or fully evaluate aesthetic quality without human review. Exported fonts are references; no proprietary or font files are distributed. Differences in installed fonts can change pagination across systems.

## Repo layout

```text
arabic-word-design-studio/
├── SKILL.md                     # The Claude skill
├── arabic_word_studio/          # Python composition and OOXML audit
├── examples/briefs/            # Four demonstration inputs
├── examples/output/            # Four generated editable DOCX examples
├── scripts/                    # Build / inspect / render CLIs
├── references/                 # Design, RTL, schema, QA, architecture
├── tests/                      # Automated structural tests
└── .github/workflows/          # CI checks
```

## Provenance

The implementation is independently authored and was informed by public documentation and community discussions around `python-docx`, Anthropic's DOCX skill, Arabic Word RTL conventions, and OOXML. No third-party skill source code is copied. See [architecture and research references](references/architecture.md). Project code is MIT licensed; dependencies retain their own licenses.

## Roadmap

Next priorities are content-preserving restyling of user-provided DOCX, refined template packs, chart objects, Arabic TOC and footnotes, Word-vs-LibreOffice rendering comparisons and in-editor design customization.


## Layout corrections in v1.1

This release addresses RTL list indentation, unintended inherited paragraph indents in table cells, inconsistent cell padding/paragraph spacing, Word complex-script header bold, compound numeric ranges rendered backwards in Arabic (e.g. `2026–2027`), and oversized blank paragraphs following tables.

The shared `LAYOUT` tokens live in `arabic_word_studio/design.py`. `scripts/audit_docx.py` now checks table-cell margins, paragraph indents and spacing, RTL hanging bullets, and warns about potentially reversed compound numbers. The new `tests/test_layout_regression.py` provides repeatable regression checks. See [layout and spacing contract](references/layout-spacing-rules.md). Run the structural tests **and** inspect every rendered page; automated inspection is not a substitute for visual QA.
