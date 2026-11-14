# JSON input contract — v1

The first-release builder supports these `document_type` identifiers:
- `executive_report`
- `official_decision`
- `strategic_plan`
- `impact_report`

## Required
- `document_type`: one of the above
- `title`: nonempty document title
- `decision.articles`: nonempty array, if `official_decision`
- `sections`: nonempty array, otherwise

## Optional top-level
- `organization`, `eyebrow`, `subtitle`, `date`, `prepared_by`, `reference`, `summary`, `footer_note`
- `cover_metrics`: array of `{label, value, note?}` for cover-enabled presets
- `brand`: optional object containing only `primary`, `accent`, `muted`, `pale` (`#RRGGBB` or `RRGGBB`) and `heading_font`, `body_font` font-family names.
- `sample`: boolean; mark demonstration facts as illustrative in copy and footer text.

## Sections
Each section can contain any of:
- `heading`: string
- `paragraphs`: array of strings
- `bullets`: array of strings
- `metrics`: array of `{label, value, note?}`
- `table`: object `{headers:[strings], rows:[[strings]]}`; all rows must match header length
- `steps`: array of `{title, owner, due, evidence}` (rendered as an accountability table)

## Administrative decisions
`decision` object: `{preamble: string, articles:[{title,text}], signature_title?, signature_name?}`.

## Sample
See `examples/briefs/executive_report.json` and the other three briefs. No fictional performance data may be represented as actual results in a delivered document.

## Known v1 constraints
This is deliberately a small, documented schema, not a markdown-to-Word engine; native Word charts, arbitrary imported tables, tracked changes, sections with mixed orientation and live automatic TOC are out of scope.
