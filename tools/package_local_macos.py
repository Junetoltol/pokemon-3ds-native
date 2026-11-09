#!/usr/bin/env python3
"""Build a private macOS app around a local port. Never bundle ROM data."""
import argparse
import json
from pathlib import Path
import plistlib
import subprocess
from port import ROOT, PRIVATE, PROFILES, inspect_dump, validate_profile

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--game',choices=sorted(PROFILES),required=True)
p.add_argument('--rom',type=Path,required=True)
a=p.parse_args()
rom=a.rom.resolve(strict=True);info=inspect_dump(rom);validate_profile(info,a.game)
port=PRIVATE/'ports'/a.game
manifest=json.loads((port/'local-input.json').read_text())
if info['sha256'] != manifest['sha256']:raise SystemExit('input hash differs from local compiled port')
source=port/'bin'/f'pokemon-{a.game}-local'
app=PRIVATE/'apps'/f'Pokemon {a.game.title()} Local.app'
if app.exists():raise SystemExit('app exists; refusing overwrite')
macos=app/'Contents/MacOS';macos.mkdir(parents=True)
# APFS clone preserves disk space without aliasing future signatures/writes.
subprocess.run(['cp','-c',str(source),str(macos/'runtime')],check=True)
data=PRIVATE/'runtime-data'/a.game;data.mkdir(parents=True,exist_ok=True)
logs=PRIVATE/'runs';logs.mkdir(parents=True,exist_ok=True)
code='''#include <mach-o/dyld.h>
#include <filesystem>
#include <vector>
#include <string>
#include <unistd.h>
#include <fcntl.h>
#include <cstdio>
int main(int argc,char** argv) {
 uint32_t size=0; _NSGetExecutablePath(nullptr,&size);
 std::vector<char> path(size); if(_NSGetExecutablePath(path.data(),&size))return 126;
 auto runtime=(std::filesystem::canonical(path.data()).parent_path()/"runtime").string();
 int log=open(LOG_PATH,O_CREAT|O_WRONLY|O_APPEND,0600);
 if(log>=0){dup2(log,1);dup2(log,2);close(log);}
 chdir(ROOT_PATH);
 std::vector<std::string> values={runtime,ROM_PATH,"--data",DATA_PATH,"--mute","--rasterizer","software","--renderer","gl"};
 for(int i=1;i<argc;++i)values.push_back(argv[i]);
 std::vector<char*> args;for(auto& value:values)args.push_back(value.data());args.push_back(nullptr);
 setenv("RUST_LOG","info,cranelift_jit=warn",1);
 execv(runtime.c_str(),args.data());perror("could not start local runtime");return 127;
}
'''
for key,value in {'LOG_PATH':logs/f'{a.game}-app.log','ROOT_PATH':ROOT,'ROM_PATH':rom,'DATA_PATH':data}.items():
    code=code.replace(key,json.dumps(str(value)))
launcher=port/'app-launcher.cpp';launcher.write_text(code)
subprocess.run(['clang++','-std=c++20','-O2',str(launcher),'-o',str(macos/'launch')],check=True)
with (app/'Contents/Info.plist').open('wb') as f:
    plistlib.dump({'CFBundleExecutable':'launch','CFBundleIdentifier':f'org.pokemon3dsnative.local.{a.game}','CFBundleName':f'Pokemon {a.game.title()} Local','CFBundlePackageType':'APPL','CFBundleVersion':'1','NSHighResolutionCapable':True},f)
subprocess.run(['codesign','--force','--deep','--sign','-',str(app)],check=True)
subprocess.run(['codesign','--verify','--deep','--strict',str(app)],check=True)
print(app)
