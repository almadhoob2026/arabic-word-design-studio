# Changelog

## v1.1.0 — 2026-11-14
- Correct right-hand hanging indents for Arabic bullet paragraphs.
- Explicitly reset first-line/left/right indents and before/after spacing in all table text.
- Add compatible start/end + physical left/right cell padding and centralize dimensions in `LAYOUT`.
- Preserve display order of mixed RTL numeric ranges, including 2026–2027.
- Apply complex-script bold to Arabic headers and control after-table spacing.
- Extend structural audits and add 10 new layout-regression tests (23 total).
- Re-render and visually review all 7 pages of the four sample documents.

## v1.0.1 — 2026-11-14
- Fix CLI script naming that shadowed Python’s built-in `inspect` module on GitHub Actions.
- Add a fresh-process CLI smoke test and repair example generation in CI.

## v1.0.0 — 2026-11-14
- Introduce four differentiated Arabic Word design presets: leadership report, formal decision, action plan and impact report.
- Generate editable DOCX content, native tables, heading styles, header/footer, and page number fields.
- Add OOXML-level RTL paragraph/run/table direction and complex-script font handling.
- Provide JSON input schema, style profiles, Arabic/English README and Claude skill instructions.
- Include four clearly labelled fictional samples, a structural audit, rendered-page workflow and automated tests.
- Note limitations: arbitrary existing DOCX restyling, live Word charts and dynamic TOC are not included yet.
