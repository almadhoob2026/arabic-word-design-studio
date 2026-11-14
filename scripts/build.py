#!/usr/bin/env python3
"""Generate editable DOCX from a JSON brief."""
import argparse, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from arabic_word_studio.builder import build_from_json

p=argparse.ArgumentParser(description='Create styled Arabic DOCX')
p.add_argument('brief',help='JSON brief')
p.add_argument('--out',required=True,help='DOCX output path')
a=p.parse_args()
print(build_from_json(a.brief,a.out))
