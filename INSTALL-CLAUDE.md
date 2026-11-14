# Installation in Claude — Arabic Word Design Studio v1

## Claude.ai (where custom Skills uploads are available)

1. Open Claude settings / skills management.
2. Upload `arabic-word-design-studio-claude-skill.zip` using the product's supported skill installation flow.
3. Enable the skill and use a prompt like: "أنشئ ملف Word عربي بتصميم تقرير قيادي عن الموضوع التالي...".
4. The instructions are portable. Generation of real DOCX files and visual checks still depend on whether the environment provides Python/file creation and a document renderer.

## Claude Code

Clone the repository and either keep it under your project as `.claude/skills/arabic-word-design-studio/` or link/copy it there. Ensure `SKILL.md` is at the root of that folder.

```bash
mkdir -p .claude/skills/arabic-word-design-studio
cp -r /path/to/arabic-word-design-studio/{SKILL.md,arabic_word_studio,scripts,references,examples,requirements.txt} \
  .claude/skills/arabic-word-design-studio/
```

Install prerequisites in the environment in which you intend to run the bundled scripts:

```bash
python -m pip install -r .claude/skills/arabic-word-design-studio/requirements.txt
```

For page PNG rendering also install a working LibreOffice executable on PATH and Arabic fonts on the host machine. This project does **not** bundle font files.

## Example prompts

- "حوّل النص التالي إلى تقرير قيادي Word احترافي، مع المحافظة على كل الأرقام دون زيادة."
- "صمم قرارًا إداريًا رسميًا من المواد المرفقة، مع رقم القرار والتاريخ ومكان التوقيع دون إنشاء شعار أو ختم."
- "حوّل قائمة الإجراءات إلى خطة تنفيذية Word أفقية تتضمن المسؤول وموعد القياس والدليل."
- "أنشئ تقرير أثر Word يوضح الفرق بين القبلي والبعدي ويمنع استنتاج أثر سببي غير مدعوم."

## Important scope restriction

The script does **not** yet offer a drop-in preservation-safe rewrite of arbitrary existing `.docx` files. Editing an existing document requires appropriate tools and must follow a content-preserving review process.
