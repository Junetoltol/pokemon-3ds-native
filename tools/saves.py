#!/usr/bin/env python3
"""Import a user-selected save without replacing any existing save."""
import argparse
import hashlib
from pathlib import Path
import shutil
import tempfile
from datetime import datetime, timezone

GAMES={'x','y','omega-ruby','alpha-sapphire','sun','moon','ultra-sun','ultra-moon'}
def import_save(source, game, root):
    if game not in GAMES: raise ValueError('unknown game')
    source=Path(source).resolve(strict=True)
    if not source.is_file() or source.stat().st_size==0: raise ValueError('empty or invalid save')
    directory=Path(root)/game
    directory.mkdir(parents=True,exist_ok=True)
    # Each import gets a unique backup directory. No overwrite, even in same second.
    dest=Path(tempfile.mkdtemp(prefix=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-'),dir=directory))
    copied=dest/'main'
    shutil.copyfile(source,copied)
    def digest(p):
        h=hashlib.sha256()
        with p.open('rb') as f:
            for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
        return h.hexdigest()
    if digest(source)!=digest(copied): raise ValueError('backup hash mismatch')
    (dest/'sha256.txt').write_text(digest(copied)+'\n')
    return copied
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path);p.add_argument('--game',choices=sorted(GAMES),required=True)
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]/'private/saves')
    a=p.parse_args();print(import_save(a.source,a.game,a.root))
