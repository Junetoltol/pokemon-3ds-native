#!/usr/bin/env python3
"""Exercise upstream C code generation using a self-authored ARM BX LR fixture.
This is NOT Pokemon Y and contains no game assets or retail code.
"""
from pathlib import Path
import subprocess
root=Path(__file__).resolve().parents[1]
work=root/'private/synthetic-codegen';work.mkdir(parents=True,exist_ok=True)
out=bytearray(0x804)
def put(offset,value):out[offset:offset+len(value)]=value
put(0x100,b'NCCH')
put(0x118,(0x000400000FF3DE00).to_bytes(8,'little'))
out[0x18f]=4
put(0x1a0,(3).to_bytes(4,'little'))
put(0x200,b'p3n-test')
for offset,value in [(0x210,0x100000),(0x214,1),(0x218,4),(0x60c,4)]:put(offset,value.to_bytes(4,'little'))
put(0x600,b'.code')
put(0x800,bytes.fromhex('1eff2fe1')) # bx lr: a self-authored return-only function
rom=work/'synthetic.cxi';rom.write_bytes(out)
recomp=root/'private/upstream/3dsrecomp/target/release/3dsrecomp'
subprocess.run([str(recomp),'port',str(rom),str(work/'port'),'--name','synthetic-only','--zakuro',str(root/'private/upstream/zakuro')],check=True)
archive=work/'port/code/librecomp.a'
if not archive.is_file():raise SystemExit('static archive missing')
print('SYNTHETIC ONLY: generated C, compiled ARM64 static archive, and generated Cargo project')
