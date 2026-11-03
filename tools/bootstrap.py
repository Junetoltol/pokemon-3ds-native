#!/usr/bin/env python3
"""Fetch pinned public sources only. Rust/Cargo must be available in PATH."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
SOURCES={
 '3dsrecomp':('https://github.com/fearkov/3dsrecomp','73b8f9caf3700991c290dd84bccffb92294d6b15'),
 'zakuro':('https://github.com/fearkov/zakuro','781b4a816e1001977bb76221feab13c43185cbab')}
for name,(url,rev) in SOURCES.items():
    dest=ROOT/'private/upstream'/name
    if not dest.exists():
        dest.parent.mkdir(parents=True,exist_ok=True)
        subprocess.run(['git','clone','--no-checkout',url,str(dest)],check=True)
        subprocess.run(['git','-C',str(dest),'checkout','--detach',rev],check=True)
    actual=subprocess.check_output(['git','-C',str(dest),'rev-parse','HEAD'],text=True).strip()
    if actual!=rev: raise SystemExit(f'{name}: unexpected checkout; refusing to replace it')
subprocess.run(['cargo','build','--release','--locked','--manifest-path',str(ROOT/'private/upstream/3dsrecomp/Cargo.toml')],check=True)
