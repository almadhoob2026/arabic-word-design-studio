# Repository publishing and releases

**Official repository:** https://github.com/almadhoob2026/arabic-word-design-studio

The public GitHub repository was created for this project. Future releases should be committed to `main` only after local tests and sample-document review pass.

## Release checklist

1. Run `python -m pytest -q` and verify the DOCX/OOXML checks succeed.
2. Rebuild the four examples with `python scripts/build.py ...` and render each file for page-level review.
3. Check RTL alignment, mixed Arabic/Latin runs, tables, headers/footers, and unexpected page splits in the rendered outputs.
4. Update `CHANGELOG.md` and both README files for behavior changes. Include only fictitious example data.
5. Commit source, references, tests, sample JSON, optional generated DOCX examples, and `assets/preview.png`.
6. Exclude `__pycache__`, `.pytest_cache`, virtual environments, intermediate PDF/PNG render output, and secrets.
7. Verify the published repository tree and the GitHub Actions checks.

## Suggested short GitHub description

Claude-compatible Arabic Word design skill: four distinct editable DOCX layouts, native RTL typography, brand-aware templates, and visual QA.

## Git workflow (for future updates)

```bash
git clone https://github.com/almadhoob2026/arabic-word-design-studio.git
cd arabic-word-design-studio
# update source and tests
git add .
git commit -m "feat: improve Arabic Word design workflow"
git push origin main
```
