#!/usr/bin/env python3
"""Run a privately generated port with bounded diagnostics; not the mock launcher."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from port import ROOT, PRIVATE, PROFILES, inspect_dump, validate_profile


def headless_passed(output, frames, returncode):
    return (returncode == 0 and re.search(rf'\bCompleted after {frames} frames\b', output) is not None
            and 'fatal errors:' not in output and 'panicked at' not in output)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--game',choices=sorted(PROFILES),required=True)
    p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--frames',type=int,default=120)
    p.add_argument('--timeout',type=float,default=120)
    p.add_argument('--window',action='store_true')
    p.add_argument('--renderer',choices=['software','gl','vulkan'],default='gl')
    p.add_argument('--rasterizer',choices=['software','hardware'],default='software')
    a=p.parse_args()
    if a.frames<=0 or a.timeout<=0: raise ValueError('frames and timeout must be positive')
    port=PRIVATE/'ports'/a.game
    manifest=json.loads((port/'local-input.json').read_text())
    info=inspect_dump(a.rom.resolve(strict=True));validate_profile(info,a.game)
    if info['sha256'] != manifest['sha256']: raise ValueError('input differs from compiled port')
    name=f'pokemon-{a.game}-local'+('.exe' if sys.platform=='win32' else '')
    exe=port/'bin'/name
    if not exe.is_file(): raise ValueError('compiled port binary missing')
    data=PRIVATE/'runtime-data'/a.game
    data.mkdir(parents=True,exist_ok=True)
    logs=PRIVATE/'runs'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    logs.mkdir(parents=True)
    command=[str(exe),str(a.rom.resolve()),'--data',str(data),'--mute','--rasterizer',a.rasterizer]
    if a.window:command+=['--renderer',a.renderer]
    else:command+=['--headless',str(a.frames)]
    record={'mode':'REAL_LOCAL_PORT','game':a.game,'mock':False,'frames_requested':None if a.window else a.frames,'rasterizer_requested':a.rasterizer,'visual_boot_verified':False,'log_dir':str(logs)}
    start=time.monotonic()
    env=os.environ.copy()
    env['RUST_LOG']='info,cranelift_jit=warn'
    print(json.dumps(record),flush=True)
    with (logs/'runtime.log').open('w') as out:
        try:
            result=subprocess.run(command,cwd=ROOT,env=env,stdout=out,stderr=subprocess.STDOUT,timeout=a.timeout)
            record['returncode']=result.returncode
        except subprocess.TimeoutExpired:
            record.update(returncode=None,timed_out=True)
    output=(logs/'runtime.log').read_text(errors='replace')
    record['wall_seconds']=time.monotonic()-start
    record['linked_code_reported']='running the recompiled code linked in' in output and 'interpreting everything' not in output
    record['headless_slice_passed']=not a.window and record['linked_code_reported'] and headless_passed(output,a.frames,record['returncode'])
    (logs/'result.json').write_text(json.dumps(record,indent=2))
    print(output[-6000:]);print(json.dumps(record,indent=2))
    return 0 if record['headless_slice_passed'] or (a.window and record['returncode']==0 and record['linked_code_reported']) else 1

if __name__=='__main__':
    try:sys.exit(main())
    except (OSError,ValueError,KeyError) as e:
        print(f'BLOCKED: {e}',file=sys.stderr);sys.exit(1)
