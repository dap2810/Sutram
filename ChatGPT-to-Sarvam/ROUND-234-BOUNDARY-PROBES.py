"""Focused R234 observations using existing compilers; no source tree changes.
Usage: python3 ChatGPT-to-Sarvam/ROUND-234-BOUNDARY-PROBES.py V315_ROOT V324_ROOT
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

PROBES={
'chakra_max': 'mukhya() {\nvitti n = 0\nchakra i = 9223372036854775807 tak 9223372036854775807 {\nlikha(i)\nn = n + 1\nyadi (n == 3) { krama }\n}\n}\n',
'chakra_kosh': 'mukhya() {\nchakra i = 1 tak 3 {\nkosh k[1]\nkosh_kship(k, i)\n}\nlikha(parimana())\n}\n',
'kuru_kosh': 'mukhya() {\nvitti i = 0\nkuru {\nkosh k[1]\nkosh_kship(k, i)\ni = i + 1\n} yavat (i < 3)\nlikha(parimana())\n}\n'}
ADAPTER='''yoj khand
yoj vakyank
mukhya() {
    vitti text = vartani_grahan()
    vitti n = vartani_aayam(text)
    abhava(n < 32, "input too long\\n")
    mala cells[33]
    mala ok[1]
    khand_mukt(text, n, cells)
    vitti value = varna_tak_ank(cells, n, ok)
    likha(ok[0])
    likha(value)
}
'''


def run(root,source,stdin=''):
    with tempfile.TemporaryDirectory() as directory:
        temp=Path(directory);p=temp/'probe.sm';exe=temp/'probe.bin';p.write_text(source)
        c=subprocess.run([str(root/'sutram_compiler'),str(p),str(exe)],cwd=root,capture_output=True,text=True,timeout=30)
        row={'compile_exit':c.returncode,'diagnostic':(c.stdout+c.stderr).replace(str(temp),'<tmp>').replace(str(root),'<repo>')}
        if c.returncode==0:
            r=subprocess.run([str(exe)],input=stdin,cwd=temp,capture_output=True,text=True,timeout=5)
            row.update(exit=r.returncode,stdout=r.stdout,stderr=r.stderr)
        return row


result={'probe_sources':PROBES,'adapter_source':ADAPTER,'boundaries':{},'adapter':[]}
for label,argument in zip(('v315','v324'),sys.argv[1:]):
    root=Path(argument).resolve()
    result['boundaries'][label]={'compiler_sha256':hashlib.sha256((root/'sutram_compiler').read_bytes()).hexdigest(),
                                 'runs':{name:run(root,source) for name,source in PROBES.items()}}
root=Path(sys.argv[2]).resolve()
for text in ['42\n','-42\n','0\n','-9223372036854775808\n','9223372036854775807\n',
             '9223372036854775808\n','hello\n','12 34\n','\n','+42\n','12\x00x\n']:
    result['adapter'].append({'stdin':text,**run(root,ADAPTER,text)})
print(json.dumps(result,indent=2))
