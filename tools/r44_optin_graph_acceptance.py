#!/usr/bin/env python3
"""Native opt-in R41 cycle/missing diagnostic parity during R44 graph consolidation."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
COMP=ROOT/"sutram_compiler"

TESTS=[
 ("invalid_path", {"main.sm":"# sutram-module-v1\nayojan ../evil\nmukhya() { likha(1) }\n"},
  "main.sm:2: Sutram Error [E_MODULE_INVALID]: invalid module name\n"),
 ("root_missing", {"main.sm":"# sutram-module-v1\nayojan absent\nmukhya() { likha(1) }\n"},
  "main.sm:2: Sutram Error [E_MODULE_MISSING]: cannot open import absent\n"),
 ("nested_missing",{"main.sm":"# sutram-module-v1\nayojan outer@o\nmukhya() { likha(1) }\n",
                    "lib/outer.smlib":"# sutram-module-v1\nayojan absent@x\nprakriya outer() { pratiyati 1 }\n"},
  "outer.smlib:2: Sutram Error [E_MODULE_MISSING]: cannot open import absent\n"),
 ("cycle",{"main.sm":"# sutram-module-v1\nayojan cyc_a\nmukhya() { likha(1) }\n",
          "lib/cyc_a.smlib":"ayojan cyc_b\nprakriya foo() { pratiyati 1 }\n",
          "lib/cyc_b.smlib":"ayojan cyc_a\nprakriya bar() { pratiyati 1 }\n"},
  "cyc_b.smlib:1: Sutram Error [E_MODULE_CYCLE]: dependency cycle: cyc_a -> cyc_b -> cyc_a\n"),
]
def main():
    count=0
    with TemporaryDirectory(prefix="r44-optin-") as root:
        root=Path(root)
        for name,files,want in TESTS:
            directory=root/name
            for path,text in files.items():
                p=directory/path
                p.parent.mkdir(parents=True,exist_ok=True)
                p.write_text(text)
            run=subprocess.run([str(COMP),str(directory/"main.sm"),str(directory/"result.bin")],
                    cwd=ROOT,capture_output=True,text=True,timeout=30)
            got=run.stdout+run.stderr
            ok=(run.returncode==1 and got==want)
            print(f"{'PASS' if ok else 'FAIL'} {name}: rc={run.returncode} {got!r}")
            if not ok: print(f"  expected rc=1 {want!r}")
            count+=ok
    print(f"R41 opt-in cycle/missing parity: {count}/{len(TESTS)}")
    return 0 if count==len(TESTS) else 1
if __name__=="__main__":
    sys.exit(main())
