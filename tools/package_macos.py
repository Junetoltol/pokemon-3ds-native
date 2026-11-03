#!/usr/bin/env python3
"""Bundle SDL3 into a locally built app; ad-hoc signing is not notarization."""
from pathlib import Path
import shutil
import os
import subprocess
import sys
source=Path(sys.argv[1]).resolve(strict=True)
dest=Path(sys.argv[2]).resolve()
if dest.exists(): raise SystemExit('destination exists; refusing overwrite')
shutil.copytree(source,dest)
exe=dest/'Contents/MacOS/pokemon-3ds-native'
libs=subprocess.check_output(['otool','-L',str(exe)],text=True).splitlines()[1:]
for line in libs:
    lib=line.strip().split(' (')[0]
    if 'libSDL3' not in lib: continue
    frameworks=dest/'Contents/Frameworks';frameworks.mkdir(exist_ok=True)
    bundled=frameworks/Path(lib).name
    source_lib=Path(lib)
    if lib.startswith('@rpath/'):
        candidates=[]
        if os.environ.get('SDL3_ROOT'):
            candidates.append(Path(os.environ['SDL3_ROOT'])/'lib'/Path(lib).name)
        lines=subprocess.check_output(['otool','-l',str(exe)],text=True).splitlines()
        for i,line in enumerate(lines):
            if line.strip()=='cmd LC_RPATH':
                value=lines[i+2].strip().split('path ',1)[1].split(' (offset')[0]
                value=value.replace('@executable_path',str(exe.parent)).replace('@loader_path',str(exe.parent))
                candidates.append(Path(value)/lib.removeprefix('@rpath/'))
        source_lib=next((c for c in candidates if c.is_file()),None)
        if source_lib is None: raise SystemExit(f'cannot resolve SDL library: {lib}')
    shutil.copyfile(source_lib,bundled)
    subprocess.run(['install_name_tool','-id','@rpath/'+bundled.name,str(bundled)],check=True)
    subprocess.run(['install_name_tool','-change',lib,'@executable_path/../Frameworks/'+bundled.name,str(exe)],check=True)
resources=dest/'Contents/Resources/Licenses'
resources.mkdir(parents=True,exist_ok=True)
shutil.copyfile(Path(__file__).resolve().parents[1]/'docs/SDL-LICENSE.txt',resources/'SDL3.txt')
subprocess.run(['codesign','--force' ,'--deep','--sign','-',str(dest)],check=True)
subprocess.run(['codesign','--verify','--deep','--strict',str(dest)],check=True)
print(dest)
