#!/usr/bin/env python3
"""Render DOCX with LibreOffice and PyMuPDF for visual QA. Does not edit DOCX."""
import argparse, shutil, subprocess, tempfile, sys
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument('docx');p.add_argument('--out-dir',required=True)
p.add_argument('--dpi',type=int,default=130)
a=p.parse_args()
if not shutil.which('libreoffice'):
    sys.exit('LibreOffice is required for rendering (not DOCX generation)')
try:import fitz
except ImportError:sys.exit('Install PyMuPDF: pip install -r requirements.txt')
source=Path(a.docx).resolve(); out=Path(a.out_dir).resolve();out.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory(prefix='awds-lo-') as tmp:
    prof=Path(tmp)/'profile'; prof.mkdir()
    cmd=['libreoffice',f'-env:UserInstallation={prof.as_uri()}', '--headless','--convert-to','pdf','--outdir',str(out),str(source)]
    proc=subprocess.run(cmd,capture_output=True,text=True,timeout=90)
    pdf=out/(source.stem+'.pdf')
    if proc.returncode or not pdf.exists():sys.exit(f'Render error: {proc.stderr} {proc.stdout}')
with fitz.open(pdf) as pages:
    for i,page in enumerate(pages):
        pix=page.get_pixmap(matrix=fitz.Matrix(a.dpi/72,a.dpi/72),alpha=False)
        pix.save(out/f'page-{i+1:02d}.png')
    print(f'{source.name}: {len(pages)} page(s) rendered in {out}')
