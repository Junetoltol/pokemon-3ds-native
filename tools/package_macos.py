#!/usr/bin/env python3
"""Bundle SDL3 into a locally built app; ad-hoc signing is not notarization."""
from pathlib import Path
import shutil
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
    shutil.copyfile(lib,bundled)
    subprocess.run(['install_name_tool','-id','@rpath/'+bundled.name,str(bundled)],check=True)
    subprocess.run(['install_name_tool','-change',lib,'@executable_path/../Frameworks/'+bundled.name,str(exe)],check=True)
subprocess.run(['codesign','--force','--deep','--sign','-',str(dest)],check=True)
subprocess.run(['codesign','--verify','--deep','--strict',str(dest)],check=True)
print(dest)
