# The Windows binaries in this folder

Cross-built on Linux with `nasm -f win64` and `ld -mi386pep`. Both are valid PE32+ x86-64:

| File | Size | Subsystem | Built from |
|---|---|---|---|
| `sutram.exe` | 176,486 B | console (3) | `src/sutram_compiler.asm` with `-dWINDOWS` |
| `sutram-ide.exe` | 34,581 B | GUI (2) | `windows/gui/sutram_gui.asm` |

**They compile and link. They have never been executed.** No Windows machine has run either of them.
That is the entire remaining question, and it is why they are here.

Build commands, for reproducing:

    nasm -f win64 -dWINDOWS -I. src/sutram_compiler.asm -o /tmp/w.obj
    ld -mi386pep --entry=_start -o sutram.exe /tmp/w.obj

    nasm -f win64 windows/gui/sutram_gui.asm -o /tmp/gw.obj
    ld -mi386pep --subsystem windows --entry=_start -o sutram-ide.exe /tmp/gw.obj

Note `windows/gui/r67_gui_entry.asm` did **not** build in this environment — it needs include paths
that are not set up the same way. That is unresolved and worth checking.
