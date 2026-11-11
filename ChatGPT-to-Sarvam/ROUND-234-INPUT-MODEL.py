"""R234 temporary source-substitution experiment; not a compiler return-type patch.
Uses an existing v324 compiler. Original and grahan->vartani_grahan sources are
compiled and, if accepted, run in temporary folders. No project source is changed.
Usage: python3 ChatGPT-to-Sarvam/ROUND-234-INPUT-MODEL.py ROOT
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(sys.argv[1]).resolve()
COMPILER = ROOT / 'sutram_compiler'
SOURCES = ['examples/23_grahan_input.sm','examples/24_guess_game.sm','examples/26_calculator.sm',
           'examples/349_r126_kosh_in_one_branch.sm','examples/46_language_reference.sm',
           'examples/59_windows_grahan_runtime.sm','tests/r79_real/report_blocks.sm','tests/r79_real/report_plain.sm']
INPUTS = {'23_grahan_input':'5\n','24_guess_game':'7\n','26_calculator':'20\n4\n',
          '46_language_reference':'7\n','59_windows_grahan_runtime':'42\n',
          'report_blocks':'1\n1\n2\n3\n4\n','report_plain':'1\n1\n2\n3\n4\n'}


def replace_calls(source):
    tokens = [m for m in re.finditer(r'/\*.*?\*/|//[^\n]*|\#[^\n]*|"(?:\\.|[^"\\])*"|\w+|[^\s]',source,re.S)
              if not m.group().startswith(('/*','//','#','"'))]
    spans = [a.span() for a,b in zip(tokens,tokens[1:]) if a.group()=='grahan' and b.group()=='(']
    for start,end in reversed(spans):source=source[:start]+'vartani_grahan'+source[end:]
    return source,len(spans)


result={'model':'Replace direct grahan() calls with existing v324 vartani_grahan(); not the final compiler implementation',
        'compiler_sha256':hashlib.sha256(COMPILER.read_bytes()).hexdigest(),'programs':[]}
with tempfile.TemporaryDirectory() as directory:
    temp=Path(directory)
    for relative in SOURCES:
        original=(ROOT/relative).read_text();modified,count=replace_calls(original)
        row={'path':relative,'call_sites':count,'stdin':INPUTS.get(Path(relative).stem,'')}
        for variant,source in [('original',original),('text_reader',modified)]:
            p=temp/(variant+'.sm');exe=temp/(variant+'.bin');p.write_text(source)
            if exe.exists():exe.unlink()
            c=subprocess.run([str(COMPILER),str(p),str(exe)],cwd=ROOT,capture_output=True,text=True,timeout=30)
            status={'compile_exit':c.returncode,'diagnostic':(c.stdout+c.stderr).replace(str(temp),'<tmp>').replace(str(ROOT),'<repo>')}
            if c.returncode==0:
                try:
                    r=subprocess.run([str(exe)],input=row['stdin'],cwd=temp,capture_output=True,text=True,timeout=5)
                    status.update(exit=r.returncode,stdout=r.stdout,stderr=r.stderr)
                except subprocess.TimeoutExpired:status['timeout']=True
            row[variant]=status
        result['programs'].append(row)
print(json.dumps(result,indent=2,ensure_ascii=False))
