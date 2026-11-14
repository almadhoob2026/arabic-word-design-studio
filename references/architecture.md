# Architecture, dependencies and provenance

- Python `python-docx` composes native Word objects with editable paragraphs, tables, styles, headers and fields.
- `lxml` inspects OOXML for RTL and table properties.
- `LibreOffice` (external executable) converts DOCX to PDF for QA.
- `PyMuPDF` renders PDF pages to PNG for review. `Pillow` is optional for preview sheets.
- No network connection, third-party asset download or font-file redistribution is required.
- The template layouts and code in this repository were independently authored for this skill; linked community projects served as public technical references, not code sources.

## Technical research references
- Anthropic skills (docx) — https://github.com/anthropics/skills/tree/main/skills/docx (technical reference; do not assume redistribution license)
- Arabic Office Skills — https://github.com/asadeisa/arabic-office-skills (RTL implementation ideas; inspect original license before reuse)
- python-docx — https://github.com/python-openxml/python-docx
- docxtpl — https://github.com/elapouya/python-docx-template (future template approaches, not a dependency in v1)

## Document compatibility
Microsoft Word and LibreOffice can render differently when user fonts, field update behavior, paragraph spacing or page layout defaults differ. Always perform final inspection in the intended delivery environment when available. Content-preserving editing of arbitrary uploaded DOCX is not included in the packaged v1 generator.

## Licensing
Project-owned source: MIT License. Third-party dependencies have their own licenses and are not re-licensed by this project. No font binaries are included.
