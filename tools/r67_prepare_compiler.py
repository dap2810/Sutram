#!/usr/bin/env python3
"""Stage current-main R66 integration + scoped R67 pure stack-pair site.

Does not overwrite source, build binaries, download files, or enable the
pure-inline-assembly contract by default. See docs/R67-SOURCE-REVIEW.md.
"""
from __future__ import annotations
import argparse, difflib, hashlib, json
from pathlib import Path
import r66_prepare_review as r66

OLD = ".gs_nishkriya:\n    ; [AST_NISHKRIYA][hex_str_ptr][0][0]\n"
NEW = OLD + """%ifdef SUTRAM_R67_PURE_STACK_PAIRS
    ; Explicit opt-in contract: the WHOLE inline block is pure stack traffic.
    ; The matcher validates every byte BEFORE emission, never removes code.
    mov rdi,[rbx+8]
    call strlen
    cmp rax,64
    ja .r67_not_pair
    mov rdi,[rbx+8]
    lea rsi,[rdi+rax]
    call r67_is_pure_stack_pair
    test eax,eax
    jz .r67_not_pair
    pop rbx
    ret
.r67_not_pair:
%endif
"""
INCLUDE_OLD = "gen_code:\n"
INCLUDE_NEW = """%ifdef SUTRAM_R67_PURE_STACK_PAIRS
%include "src/r67_stack_pair.inc"
%endif

gen_code:
"""

def add_pair_site(text: str) -> str:
    for old in (OLD, INCLUDE_OLD):
        if text.count(old) != 1:
            raise ValueError("missing/duplicate R67 emission anchor")
    if 'SUTRAM_R67_PURE_STACK_PAIRS' in text:
        raise ValueError("R67 site already present")
    return text.replace(OLD,NEW,1).replace(INCLUDE_OLD,INCLUDE_NEW,1)

def prepare(data: bytes) -> bytes:
    # The pinned main metadata still reports caee... despite v145's sync note.
    # Fail on unknown updates. Never falsely treat a different compiler as input.
    staged = r66.prepare(data)
    return add_pair_site(staged.decode('utf-8')).encode('utf-8')

def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',type=Path,default=Path('src/sutram_compiler.asm'))
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--patch-output',type=Path,required=True)
    a=ap.parse_args()
    paths=[p.resolve() for p in (a.source,a.output,a.patch_output)]
    if len(set(paths))!=3 or any(p.exists() for p in paths[1:]):
        ap.error('use distinct fresh output/patch paths; no overwrite')
    before=paths[0].read_bytes();after=prepare(before)
    patch=''.join(difflib.unified_diff(before.decode().splitlines(True),after.decode().splitlines(True),fromfile='a/src/sutram_compiler.asm',tofile='b/src/sutram_compiler.asm'))
    made=[]
    try:
        for name,data in ((paths[1],after),(paths[2],patch.encode())):
            with name.open('xb') as f:
                made.append(name);f.write(data)
    except BaseException:
        for name in made: name.unlink(missing_ok=True)
        raise
    print(json.dumps({'input_blob':r66.git_blob(before),'output_blob':r66.git_blob(after),'output_sha256':hashlib.sha256(after).hexdigest(),'full_compiler_native_test':'not run by preparation'},indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main())
