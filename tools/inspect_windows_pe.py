"""Read-only PE32+ section/import inventory for the tested Windows artifacts."""
from pathlib import Path
import struct,hashlib,json
r=Path(__file__).resolve().parents[1]
rows=[]
for rel in ['win/sutram.exe','sutram-ide-gui.exe','Sutram-Setup.exe','build/windows/hello.exe']:
    b=(r/rel).read_bytes();pe=struct.unpack_from('<I',b,60)[0]
    assert b[pe:pe+4]==b'PE\0\0'
    machine,count=struct.unpack_from('<HH',b,pe+4);opt=pe+24
    assert machine==0x8664 and struct.unpack_from('<H',b,opt)[0]==0x20b
    section_start=opt+struct.unpack_from('<H',b,pe+20)[0]
    sections=[]
    for n in range(count):
        off=section_start+n*40
        virtual_size,rva,size,raw=struct.unpack_from('<IIII',b,off+8)
        flags=struct.unpack_from('<I',b,off+36)[0]
        assert not (flags&0x20000000 and flags&0x80000000)
        sections.append({'name':b[off:off+8].split(b'\0')[0].decode(),'rva':rva,'virtual_size':virtual_size,'raw':raw,'size':size,'flags':hex(flags)})
    def raw_offset(rva):
        for s in sections:
            if s['rva']<=rva<s['rva']+max(s['virtual_size'],s['size']):return s['raw']+rva-s['rva']
        raise ValueError('RVA outside sections')
    import_rva=struct.unpack_from('<I',b,opt+120)[0];dlls=[]
    if import_rva:
        off=raw_offset(import_rva)
        while any(b[off:off+20]):
            name_rva=struct.unpack_from('<I',b,off+12)[0];start=raw_offset(name_rva)
            dlls.append(b[start:b.index(b'\0',start)].decode());off+=20
    rows.append({'file':rel,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'machine':'AMD64','format':'PE32+','sections':sections,'import_dlls':dlls})
print(json.dumps(rows,indent=2))
