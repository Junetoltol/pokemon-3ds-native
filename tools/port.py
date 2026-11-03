#!/usr/bin/env python3
"""Private, fail-closed Pokemon Y conversion driver. Never downloads game data."""
import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / 'private'
RECOMP_REV = '73b8f9caf3700991c290dd84bccffb92294d6b15'
ZAKURO_REV = '781b4a816e1001977bb76221feab13c43185cbab'

def inspect_dump(path):
    with path.open('rb') as f:
        header = f.read(512)
        if len(header) < 512:
            raise ValueError('truncated dump')
        if header[256:260] == b'NCSD':
            offset = int.from_bytes(header[288:292], 'little') * 512
            if offset < 512:
                raise ValueError('invalid first NCSD partition')
            f.seek(offset)
            header = f.read(512)
        if len(header) < 512 or header[256:260] != b'NCCH':
            raise ValueError('only NCSD/NCCH dumps are accepted; CIA unsupported')
        # Readable header does not establish decrypted payload or game compatibility.
        program_id = f'{int.from_bytes(header[280:288], "little"):016X}'
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return {'sha256': h.hexdigest(), 'program_id': program_id}

def check_checkout(path, revision):
    got = subprocess.check_output(['git','-C',str(path),'rev-parse','HEAD'], text=True).strip()
    if got != revision:
        raise ValueError(f'upstream revision mismatch: {path}')
    if subprocess.check_output(['git','-C',str(path),'status','--porcelain'],text=True).strip():
        raise ValueError(f'upstream checkout must be clean: {path}')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--rom',type=Path,required=True)
    ap.add_argument('--sha256',required=True,help='expected SHA-256 from your trusted local profile')
    ap.add_argument('--program-id',required=True,help='expected Y program ID for your region')
    ap.add_argument('--version',required=True,help='user-declared version; NOT independently verified')
    ap.add_argument('--recompiler',type=Path,required=True)
    ap.add_argument('--zakuro',type=Path,required=True)
    ap.add_argument('--execute',action='store_true',help='perform port generation and Cargo build')
    args=ap.parse_args()
    rom=args.rom.resolve(strict=True)
    info=inspect_dump(rom)
    if info['sha256'].lower()!=args.sha256.lower(): raise ValueError('SHA-256 mismatch')
    if info['program_id'].lower()!=args.program_id.lower(): raise ValueError('program ID mismatch')
    check_checkout(args.recompiler,RECOMP_REV)
    check_checkout(args.zakuro,ZAKURO_REV)
    out=PRIVATE/'ports'/'y'
    command=[str(args.recompiler.resolve()/'target/release/3dsrecomp'),'port',str(rom),str(out),'--name','pokemon-y-local','--zakuro',str(args.zakuro.resolve())]
    print(json.dumps({'mode':'LOCAL_PORT_PLAN','game':'y','version_declared':args.version,'version_verified':False,'input':info,'command':command},indent=2))
    if not args.execute: return
    if out.exists(): raise ValueError('output exists; preserve it or choose a fresh private workspace')
    out.parent.mkdir(parents=True,exist_ok=True)
    subprocess.run(command,check=True)
    # Bind transitive Git dependencies to the same reviewed local checkouts.
    patch='\n[patch."https://github.com/fearkov/3dsrecomp"]\n'
    for name, path in [('recomp3ds', args.recompiler.resolve()), ('recomp-abi', args.recompiler.resolve()/'abi')]:
        patch += name + ' = { path = ' + json.dumps(str(path)) + ' }\n'
    with (out/'Cargo.toml').open('a') as manifest:
        manifest.write(patch)
    # Seed the reviewed runtime dependency versions before resolving this new root.
    shutil.copyfile(args.zakuro.resolve()/'Cargo.lock', out/'Cargo.lock')
    cargo=PRIVATE/'cargo'/'bin'/('cargo.exe' if sys.platform=='win32' else 'cargo')
    env=os.environ.copy()
    if cargo.exists():
        env.update(CARGO_HOME=str(PRIVATE/'cargo'), RUSTUP_HOME=str(PRIVATE/'rustup'))
        env['PATH']=str(cargo.parent)+os.pathsep+env.get('PATH','')
    subprocess.run([str(cargo) if cargo.exists() else 'cargo','build','--release'],cwd=out,env=env,check=True)
    (out/'local-input.json').write_text(json.dumps(info|{'version_declared':args.version,'version_verified':False},indent=2))

if __name__=='__main__':
    try: main()
    except (ValueError,OSError,subprocess.CalledProcessError) as e:
        print(f'BLOCKED: {e}',file=sys.stderr)
        sys.exit(1)
