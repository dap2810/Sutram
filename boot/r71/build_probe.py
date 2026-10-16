#!/usr/bin/env python3
"""Developer-only exact-instruction GAS bridge for this one boot source.
Prefer NASM -f bin boot/r71/boot.asm -o boot.bin when NASM is installed.
Does not translate Sutram or claim an emulator/firmware boot took place.
"""
from pathlib import Path
import argparse, hashlib, json, subprocess, tempfile, struct
ROOT=Path(__file__).resolve().parent

def gas_source(text: str)->str:
    out=['.intel_syntax noprefix','.code16','.text','.globl start']
    for raw in text.splitlines():
        line=raw.split(';',1)[0].strip()
        if not line or line in ('bits 16','org 0x7c00'):continue
        if line=='times 510-($-$$) db 0':out.append('.org 510,0')
        elif line=='dw 0xaa55':out.append('.word 0xaa55')
        elif line.startswith('db '):
            if line!='db "Sutram R71 boot-path probe",13,10,0':raise ValueError('unreviewed data')
            out.extend(['.ascii "Sutram R71 boot-path probe"','.byte 13,10,0'])
        elif line=='mov si,message':out.append('mov si,OFFSET FLAT:message')
        elif line.endswith(':') or line in ('cli','sti','cld','lodsb','hlt','xor ax,ax','mov ds,ax','mov es,ax','mov ss,ax','mov sp,0x7c00','test al,al','jz .halt','mov ah,0x0e','mov bx,0x0007','int 0x10','jmp .print','jmp .halt'):
            out.append(line)
        else:raise ValueError('unreviewed boot instruction '+line)
    return '\n'.join(out)+'\n'

def build(output:Path)->dict:
    if output.exists() or output.is_symlink():raise ValueError('refuse output overwrite')
    source=(ROOT/'boot.asm').read_text()
    with tempfile.TemporaryDirectory(prefix='sutram-r71-boot-') as td:
        d=Path(td);(d/'boot.S').write_text(gas_source(source))
        commands=[['as','--32','-o',str(d/'boot.o'),str(d/'boot.S')],['ld','-m','elf_i386','-Ttext','0x7c00','--oformat','binary','-e','start','-o',str(d/'boot.bin'),str(d/'boot.o')]]
        for cmd in commands:
            r=subprocess.run(cmd,capture_output=True,timeout=20,check=False)
            if r.returncode:raise RuntimeError(r.stderr.decode())
        data=(d/'boot.bin').read_bytes()
    if len(data)!=512 or data[510:]!=b'\x55\xaa':raise ValueError('invalid boot image')
    with output.open('xb') as f:f.write(data)
    return {'assembled':True,'assembler':'GNU as exact-instruction bridge','bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'boot_execution':'NOT_RUN','generated_by_sutram':False,'output':str(output)}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    print(json.dumps(build(a.output),indent=2))
