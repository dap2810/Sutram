# Sutram Windows usage

## Installation and build route

[Installation routes](INSTALLATION-ROUTES.md) is the single maintained statement
of which native per-user installer path is supported, where its builder emits
artifacts, how the legacy NSIS path differs, and why the currently stale setup
wrapper should not be used. Installation privileges/defaults are not duplicated
here. A source-review ZIP is not a complete installed environment.

## Compile and run

From a verified distribution/checkout containing the native compiler and packs,
pass quoted paths as needed:

```text
sutram.exe input.sm output.exe
output.exe
sutram.exe --lang gujarati program.sm output.exe
sutram.exe --version
```

Windows programs need a PE target. Do not expect a Linux ELF file merely renamed
`.exe` to run on Windows. Keep compiler, required relative folders, examples,
language packs and GUI files from a coherent build together. Source instructions
are not a claim of target-specific feature acceptance.

## Troubleshooting without weakening protections

If `sutram` is not recognized, start a new terminal after verified per-user PATH
integration, or use the verified executable's full path. Quote paths containing
spaces/non-Latin characters. If a language pack is missing, verify the actual
package's `lang` directory and the command's working directory before retrying.

A policy/antivirus block is not automatically a false positive. Record the error
and obtain an authorized review; do not disable protections or bypass policy.
A valid PE header and unsigned-build explanation do not prove safety or runtime
correctness. Repeated silent failure requires logs, exit codes and exact hashes,
not a blanket instruction to allow a file.

The GUI counter is a title-only scoped cluster count, not glyph shaping or caret
replacement. Follow [the manual Windows checklist](R68-WINDOWS-GUI-CHECKLIST.md)
for opening, editing, file operations, rendering observations and closing. No
Windows GUI or installer pass is asserted by this documentation update.
