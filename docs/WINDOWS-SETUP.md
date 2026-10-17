# Sutram on Windows — setup and usage guide

Sutram runs on Windows **natively**: no WSL, no Linux VM, no Python, no C runtime.
`sutram.exe` is a real Win64 program, and the programs it compiles are real
Windows executables (PE32+). This guide covers installation, compiling, running,
and troubleshooting.

---

## 1. What you need

End users of an accepted prebuilt package need no compiler toolchain.
Building the compiler source requires NASM and a compatible linker.
Installer tooling and Windows acceptance are separate; read
**INSTALLATION-ROUTES.md** before choosing a packaging route.

---

## 2. Install

### Method A — per-user wizard (requires release acceptance)

1. Use an independently verified `Sutram-Setup.exe`, not an arbitrary legacy build.
2. The supported contract is `%LOCALAPPDATA%\Programs\Sutram`, with user-only
   PATH changes and no elevation. Stop if the package asks for administrator access.
3. After a successful installation and PATH selection, open a new terminal.

This describes the required installer behavior, not a Windows run performed
by the clean-source audit. Known source-build blockers are recorded in
**INSTALLATION-ROUTES.md**.

Release acceptance must check the per-user Start Menu entry, optional Desktop
shortcut, HKCU **Apps & Features** entry, and matching uninstaller.

### Method B — portable folder (no installation)

1. Unzip a verified portable Windows package into a folder you own.
2. Open a terminal in the extracted compiler folder.
3. Run `sutram.exe` directly; adding it to PATH is not required.

The repository contains `windows/install.bat`; it is not a root-level script
and is not an accepted workaround for an unverified installer.

Keep the folder together: the language packs live in `lang\` beside `sutram.exe`.

### Method C — build from source

Requires NASM and a PE-capable linker (GNU `ld`, or MSVC/lld-link).

```
nasm -f win64 -dWINDOWS -I. src\sutram_compiler.asm -o sutram.obj
ld -mi386pep --entry=_start -o sutram.exe sutram.obj
```

The installer sources are under `windows/native-installer/`. The legacy
`windows/BUILD-WINDOWS-SETUP.cmd` chain is not a verified build route in the
clean snapshot: its wrapper and preflight still expect an older directory
layout. Do not bypass the preflight or regenerate hashes merely to silence
it. See **INSTALLATION-ROUTES.md** for the integration gate.

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
| Antivirus or policy blocks the `.exe` | The cause must be investigated; an unsigned binary is not automatically safe | Keep protection enabled. Record the exact alert and package hash, verify provenance with the maintainer, and stop pending review. Do not bypass the block. |
| Paths with spaces or non-Latin characters fail | Shell quoting | Quote the paths: `sutram.exe "C:\My Files\a.sm" "C:\out\a.exe"`. |

---

## 6. Linux vs Windows — what differs

| | Linux | Windows |
|---|---|---|
| Compiler binary | ELF (`sutram_compiler`) | PE (`sutram.exe`) |
| Output format | ELF (`.bin`) | PE (`.exe`) |
| Output selection | name ending `.bin` | name ending `.exe` |
| Language-pack search | `lang/`, then `$HOME/.local/share/sutram/lang/` | `lang\`, then `%USERPROFILE%\.local\share\sutram\lang\` |
| Install | source build/direct execution; no root install script in this checkout | accepted per-user wizard or portable package; see INSTALLATION-ROUTES.md |
| Status | maintainer-reported Linux gates; see root README | implementation status below is not complete real-Windows acceptance |

Both targets come from the **same primary compiler source**, but platform
backends and system operations still require independent execution tests.

---

## 7. Windows feature status

Reported as implemented: compiling, printing strings and numbers (`likha`, `shabda`),
arithmetic, variables, `yadi`/`anyatra`, `yavat`, `punaravartana`,
`krama`/`uddeshya`, functions with up to 6 arguments, recursion, early returns,
block comments, language packs, error diagnostics, exit codes.

The Windows keyboard-input (`grahan`) implementation reads through
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
  aliases; bundled language packs provide additional native keyword words.
- Generated programs are native machine code, not interpreted.
- The end user needs no toolchain at all.
- The installer is a *packaging* tool. (The reference installer happens to be
  written in C + PowerShell — that is build-time packaging only; it is not part
  of the language, the compiler, or the programs Sutram produces.)
