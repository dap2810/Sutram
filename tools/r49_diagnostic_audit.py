#!/usr/bin/env python3
"""Round 51 strict, independent-source diagnostic acceptance over real native NASM output.

No output is invented. The acceptance corpus exercises parsing, repeated/nested
imports, qualified modules, semantic backpatching and graph diagnostics.
It asserts each error's filename, line, column, code and no binary side-effects.
"""
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
COMPILER = ROOT / "r48_after"
LOCATION = re.compile(r"^([^\s:]+\.(?:sm|smlib)):(\d+):(\d+):\s+Sutram Error \[([^\]]+)\]", re.M)
# (source under tests or examples, test source, expected diagnostics)
SPECS = [
 ("tests/r49_check", "missing_separators.sm", [("missing_separators.sm",2,"E_PARSE"),("missing_separators.sm",3,"E_PARSE"),("missing_separators.sm",4,"E_PARSE")]),
 ("tests/r49_check", "nested_expressions.sm", [("nested_expressions.sm",2,"E_PARSE"),("nested_expressions.sm",4,"E_PARSE")]),
 ("tests/r49_check", "top_level_malformed.sm", [("top_level_malformed.sm",1,"E_PARSE")]),
 ("tests/r49_check", "module_missing.sm", [("module_missing.sm",2,"E_MODULE_MISSING")]),
 ("tests/r49_check", "import_bad.sm", [("faulty_r49.smlib",2,"E_PARSE")]),
 ("tests/r51_check", "nested_root.sm", [("inner_r51.smlib",2,"E_PARSE")]),
 ("tests/r51_check", "namespaced_root.sm", [("broken_ns_r51.smlib",2,"E_PARSE")]),
 ("tests/r51_check", "semantic_import.sm", [("semantics_r51.smlib",2,"E_UNDEFINED_FUNCTION"),("semantics_r51.smlib",3,"E_UNDEFINED_FUNCTION"),("semantics_r51.smlib",4,"E_UNDEFINED_FUNCTION")]),
 ("tests/r51_check", "missing_three.sm", [("missing_three.sm",2,"E_MODULE_MISSING"),("missing_three.sm",3,"E_MODULE_MISSING"),("missing_three.sm",4,"E_MODULE_MISSING")]),
 ("tests/r51_check", "nested_braces.sm", [("nested_braces.sm",3,"E_PARSE"),("nested_braces.sm",5,"E_PARSE"),("nested_braces.sm",9,"E_PARSE")]),
 ("examples", "164_r41_cycle_reject.sm", [("r41_cycle_b.smlib",2,"E_MODULE_CYCLE")]),
 ("examples", "212_r41_v1_private.sm", [("212_r41_v1_private.sm",5,"E_MODULE_NOT_EXPORTED")]),
 ("examples", "213_r41_v1_dupexp.sm", [("r41_dup.smlib",4,"E_MODULE_DUP_EXPORT")]),
 ("examples", "214_r41_v1_noalias.sm", [("214_r41_v1_noalias.sm",3,"E_MODULE_V1_ALIAS")]),
 ("examples", "156_namespaced_alias_collision.sm", [("156_namespaced_alias_collision.sm",3,"E_MODULE_ALIAS_REUSE")]),
]

wrong_provenance = 0
unlocated = 0
failures = 0
for directory, name, expected in SPECS:
    with tempfile.TemporaryDirectory(prefix="r51-audit-") as dest:
        args = [str(COMPILER), "--check", str(ROOT/directory/name)]
        p = subprocess.run(args, cwd=dest, text=True, capture_output=True, timeout=25)
        output = p.stdout + p.stderr
        actual = [(file,int(line),int(column),code)
                  for file,line,column,code in LOCATION.findall(output)]
        error_lines = [line for line in output.splitlines() if "Sutram Error [" in line]
        observed = [(f,l,c) for f,l,c,_ in actual]
        wanted = [(f,l,c) for f,l,c in expected]
        unlocated += max(0, len(error_lines)-len(actual))
        correct = [(f,l,c) for f,l,col,c in actual if col>0]
        wrong_provenance += sum(1 for item in wanted if item not in correct)
        matched = (p.returncode != 0 and len(actual)==len(expected)
                   and len(error_lines)==len(actual)
                   and len(correct)==len(wanted)
                   and sorted(correct)==sorted(wanted)
                   and not any(Path(dest).iterdir()))
        if not matched:
            failures += 1
        print("R49_AUDIT_BEGIN", name, "exit", p.returncode)
        print(output.rstrip())
        print("R49_AUDIT_COUNTS",name,"expected",len(expected),"located",len(actual),"source_matched",len(wanted)-sum(1 for item in wanted if item not in correct))
        print("R49_AUDIT_END",name,"PASS" if matched else "FAIL",flush=True)

accepted = int(failures==0 and wrong_provenance==0 and unlocated==0)
print(f"R49_AUDIT_STATUS wrong_provenance={wrong_provenance} unlocated={unlocated} universal_diagnostics_accepted={accepted} cases={len(SPECS)} failures={failures}",flush=True)
if not accepted:
    raise SystemExit(1)
