#!/usr/bin/env python3
import argparse, json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from arabic_word_studio.audit import inspect_docx
p=argparse.ArgumentParser()
p.add_argument('docx');p.add_argument('--type');p.add_argument('--json-out')
a=p.parse_args()
result=inspect_docx(a.docx,expected_type=a.type)
output=json.dumps(result,ensure_ascii=False,indent=2)
print(output)
if a.json_out:Path(a.json_out).write_text(output,encoding='utf-8')
sys.exit(0 if result['passed'] else 1)
