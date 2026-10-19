"""Rebuild/check the embedded Win64 adapter from NASM source; developer tool."""
from pathlib import Path
import argparse,struct,subprocess
ROOT=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--check',action='store_true')
    args=ap.parse_args()
    work=ROOT/'build/windows'
    work.mkdir(parents=True,exist_ok=True)
    out=work/'rtblob.bin'
    subprocess.run(['nasm','-f','bin','-I.','win/winrt_blob.asm','-o',str(out)],cwd=ROOT,check=True)
    data=out.read_bytes()
    if data[-16:-8]!=b'SUTRTV01':raise ValueError('Missing runtime metadata')
    off,size=struct.unpack('<II',data[-8:])
    if size!=len(data)-16 or off>=size:raise ValueError('Invalid runtime offsets')
    lines=['; Generated from win/winrt_blob.asm. Build metadata trailer is excluded.',f'RT_BLOB_LEN equ {size}','RT_INIT_OFF equ 0',f'RT_SYSCALL_OFF equ {off}','rt_blob:']
    lines+=['db '+','.join(f'0x{x:02x}' for x in data[i:min(i+16,size)]) for i in range(0,size,16)]
    content='\n'.join(lines)+'\n'
    target=ROOT/'win/rtblob.inc'
    if args.check:
        if target.read_text(encoding='utf8')!=content:raise ValueError('Runtime source/artifact mismatch')
    else:target.write_text(content,encoding='utf8')
    print(f'RUNTIME_OK bytes={size} syscall_offset={off} check={args.check}')
if __name__=='__main__':main()
