# Canonical Sutram build — Round 69 closure

**Decision:** `src/r68_compiler_entry.asm` is the only supported compiler build
entry. The large `src/sutram_compiler.asm` remains the single implementation;
the small NASM entry adds the already accepted host-side diagnostic calls.
It does not interpret programs or add a runtime dependency. Bare-core commands
in old round reports reproduce those historical snapshots, not a current build.

## Input identity and developer commands

Required core Git blob: `5ade34ed0287609b8f5d7e4f12873b7978479ac4` (re-pinned in ROUND-03; was `64ea028a…`, stale since v157).
Entry Git blob: `42389aaf73179726d91e23359aee2199734036e1` (713 bytes).
Neither file is changed in R69. `tools/r69_build.lock.json` also pins all known
conditional includes for both hosts. A missing, changed, symlinked or unlocked
include fails before NASM. Build reports include commands, source identities and
output SHA-256, not merely an assertion that the build succeeded.

Use a complete checkout and existing NASM/GNU ld. No download/install is performed.
Python is developer validation/report tooling, not part of the compiler/runtime.

```sh
python3 tools/r69_build.py --check-only
python3 tools/r69_build.py --target linux --output ./sutram_compiler --report ./build-linux.json
python3 tools/r69_build.py --target linux --mode pairs --output ./sutram-pairs --report ./build-pairs.json
python3 tools/r69_build.py --target windows --output ./win/sutram.exe --report ./build-windows.json
```

Fresh output/report paths are mandatory by default. `--replace` replaces only an
explicit regular, singly-linked build artifact, never an input patra. Supported
modes are default, peepholes, trap, combined and pairs. The tool validates ELF/PE
headers; **BUILT_FORMAT_CHECKED is not runtime acceptance**. The Windows-native
PowerShell builder additionally requires successful version, generated-PE/stdout,
and malformed-UTF8 diagnostic tests before publishing its compiler candidate.

Equivalent manual assembly (first verify the source lock):

```sh
nasm -f elf64 -I. src/r68_compiler_entry.asm -o sutram.o
ld -o sutram_compiler sutram.o
nasm -f win64 -DWINDOWS=1 -I. src/r68_compiler_entry.asm -o sutram.obj
ld -mi386pep --subsystem console --entry=_start -o sutram.exe sutram.obj
```

## Windows packaging chain

In **non-elevated Windows PowerShell 5.1**, from the complete checkout:

```powershell
.\windows\build-windows-setup.ps1
```

The corrected wrapper checks source pins, builds the canonical compiler, rebuilds
the GUI, calls the actual `windows/native-installer/build-installer.ps1`, verifies
both compiler payload copies and the GUI by gudh, runs a bounded resource test,
and publishes the installer candidate. The CMD launcher no longer sets an
execution policy. No old preflight or integrity manifest is falsely relabelled
as current: the canonical source lock is the replacement build-input contract;
the native installer's existing payload/least-privilege checks remain in force.

Stop on a policy/security block. Do not elevate or disable a safeguard. No
installer is certified by this source change. An outer process timeout cannot
guarantee child-process-tree cleanup; inspect remaining descendants before retry.

## Documentation consistency

README and this guide use the canonical entry. `tools/r69_build_doc_migration.py`
produces a complete, drift-checked patch for other Markdown/HTML/text build
commands in the pinned checkout. It skips immutable historical round reports and
CHANGELOG, refuses dirty mismatched inputs, and is idempotent on migrated lines.
Review/apply its patch and run its `--check` mode before release. The entire
repository documentation sweep was **not executed here**; it is an explicit
remaining integration gate, not claimed completed from partial retrieved files.

## Acceptance required

Run the R68 native diagnostics/examples, R70 negative corpus and all accepted
regression/codegen/pack/proof gates with the exact new compiler. Select it through
`SUTRAM_COMPILER` where supported; do not assume positional arguments select it.
Record actual failures and no-expectation cases. Windows GUI open/edit/run/close,
installation, cancellation, uninstallation and Unicode-console output remain
separate native Windows gates.
