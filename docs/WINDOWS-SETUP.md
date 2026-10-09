# Sutram on Windows — setup and usage guide

Sutram runs on Windows **natively**: no WSL, no Linux VM, no Python, no C runtime.
`sutram.exe` is a real Win64 program, and the programs it compiles are real
Windows executables (PE32+). This guide covers installation, compiling, running,
and troubleshooting.

---

## 1. What you need

Nothing, for the normal case. The installer and the compiler are self-contained.
NASM is only needed if you want to *build the compiler from source*; it is not
needed to install or use Sutram.

---

## 2. Install

### Method A — wizard installer (recommended)

1. Get `Sutram-Setup.exe`.
2. Double-click it. The wizard asks for a destination folder
   (default `C:\Program Files\Sutram`) and whether to add Sutram to `PATH`.
3. Finish. `sutram` is then available from any Command Prompt or PowerShell.

The installer also offers a Start Menu entry, an optional Desktop shortcut,
registers Sutram in **Apps & Features**, and installs a matching uninstaller.

### Method B — portable folder (no installation)

1. Unzip `sutram-windows-native.zip` anywhere (e.g. `C:\Sutram`).
2. Open a terminal in that folder.
3. Run `install.bat` once if you want it added to `PATH` — or just use
   `sutram.exe` directly from that folder.

Keep the folder together: the language packs live in `lang\` beside `sutram.exe`.

### Method C — build from source

Requires NASM and a PE-capable linker (GNU `ld`, or MSVC/lld-link).

```
nasm -f win64 -dWINDOWS -I. src\sutram_compiler.asm -o sutram.obj
ld -mi386pep --entry=_start -o sutram.exe sutram.obj
```

To build the **installer** as well (Windows host with MinGW GCC + PowerShell):
`BUILD-WINDOWS-SETUP.cmd` — see `windows/` and `windows/native-installer/`.

---

## 3. Compile and run

```
sutram.exe examples\01_hello.sm hello.exe
hello.exe
```

Output:

```
Namaste, Sutram!
```

The **output extension chooses the target**: `.exe` produces a Windows PE
executable, `.bin` produces a Linux ELF executable. Same compiler, two targets.

Other common commands:

```
sutram.exe --version                              show the version
sutram.exe --lang gujarati prog.sm out.exe        compile with a language pack
sutram.exe -i                                     interactive shell (REPL)
```

Language packs are looked up as `lang\<name>.lang` relative to the current
folder, or in `%USERPROFILE%\.local\share\sutram\lang\`.

---

## 4. How the generated .exe works

Each compiled program is a single-section PE32+ image containing:

```
[512-byte PE headers][~850-byte runtime][your compiled code]
```

The runtime finds `kernel32` at startup by walking the process environment
block and reading its export table — so the generated program has **no import
table and no external dependencies**. It translates the compiler's standard
output/input/exit operations into `WriteFile`, `ReadFile` and `ExitProcess`.
Nothing else needs to be installed to run a Sutram-made `.exe`.

---

## 5. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| "Unsupported 16-Bit Application" or "not a valid Win32 application" | The file is an ELF binary, not PE — i.e. it was produced by a build whose PE backend is missing | Recompile with this build (`.exe` output). Verify the first two bytes are `4D 5A` (MZ). |
| The program runs but prints nothing | Old builds marked the section read-only, so the runtime faulted while resolving `kernel32` | Use this build (the section is writable and the runtime realigns the stack). |
| `sutram` is not recognised | `PATH` not updated | Open a **new** terminal, or run `sutram.exe` with its full path. |
| Language pack not found | `lang\` is not next to the compiler / not in the profile folder | Run from the Sutram folder, or install packs to `%USERPROFILE%\.local\share\sutram\lang\`. |
| Antivirus flags the fresh `.exe` | New, unsigned binary | Allow it; the compiler is a plain PE with no imports. |
| Paths with spaces or non-Latin characters fail | Shell quoting | Quote the paths: `sutram.exe "C:\My Files\a.sm" "C:\out\a.exe"`. |

---

## 6. Linux vs Windows — what differs

| | Linux | Windows |
|---|---|---|
| Compiler binary | ELF (`sutram_compiler`) | PE (`sutram.exe`) |
| Output format | ELF (`.bin`) | PE (`.exe`) |
| Output selection | name ending `.bin` | name ending `.exe` |
| Language-pack search | `lang/`, then `$HOME/.local/share/sutram/lang/` | `lang\`, then `%USERPROFILE%\.local\share\sutram\lang\` |
| Install | one-line script (`install.sh`) | wizard installer or portable folder |
| Status | fully working | compiler + printing/arithmetic/control flow/functions working; see below |

Both targets come from the **same single compiler source**, so the language and
its behaviour are identical.

---

## 7. Windows feature status

Working: compiling, printing strings and numbers (`likha`, `shabda`),
arithmetic, variables, `yadi`/`anyatra`, `yavat`, `punaravartana`,
`krama`/`uddeshya`, functions with up to 6 arguments, recursion, early returns,
block comments, language packs, error diagnostics, exit codes.

Keyboard input (`grahan`) works on Windows: the generated `.exe` reads through
the embedded runtime (`ReadFile`) instead of a Linux system call. Arrays
(`pankti`) and structs (`rachana`) allocate through `VirtualAlloc`. Arrays and
structs still need a confirming run on a real Windows machine.

Not yet ported to Windows: the network builtins. The interactive REPL is
implemented (via `CreateProcessA`) and is awaiting a check on a real Windows
machine.

---

## 8. Philosophy (unchanged)

- The compiler is one pure-NASM source; no C, no Python, no runtime dependency.
- Sanskrit keywords are the language core; Devanagari spellings are accepted
  aliases; every Indian language has a pack of native keyword words.
- Generated programs are native machine code, not interpreted.
- The end user needs no toolchain at all.
- The installer is a *packaging* tool. (The reference installer happens to be
  written in C + PowerShell — that is build-time packaging only; it is not part
  of the language, the compiler, or the programs Sutram produces.)
