# Sutram — Roadmap

Where the language goes next, kept separate from where it is now.

**Read this as direction, not commitment.** Nothing on this page is promised, scheduled, or
partially built unless it says so. It is written down so the direction is visible, and so we do not
accidentally design against something we intend to do later.

---

## Status legend

| Mark | Meaning |
|---|---|
| **Exists** | In the compiler today, tested |
| **Planned** | Decided, not started |
| **Exploratory** | A real possibility; the path is understood but the work is not committed |

---

## The guardrails (these do not change)

Whatever is added, these hold:

- Sanskrit keyword core, with Latin transliteration primary and Devanagari optional
- `.sm` file extension
- **one hand-written pure-NASM compiler source**, no C, no Python, no runtime dependency
- programs compile to **native machine code**, never interpreted
- the end user needs **no toolchain** — the installer ships a prebuilt binary
- all work at the lowest practical permission level; no elevation

Any roadmap item that would break one of these is out of scope by definition.

---

## Future feature: operating-system capability — **Exploratory**

The question we asked ourselves: *could Sutram be used to write an operating system?*

**Today, no.** Not a full OS, and not a minimal one either. But the gap is specific and bounded
rather than fundamental, and this section records exactly what stands in the way.

### What Sutram already brings to that job

- **Freestanding.** No libc, no runtime, no interpreter — raw machine code with nothing underneath
  it but syscalls. That is the correct starting shape for kernel code.
- **`nishkriya` inline assembly.** Any instruction is reachable from Sutram source today.
- **A flat binary with a known entry point.** This is close to the shape a bootloader wants to load.
- **PE32+ output already exists** (used for the Windows build). A UEFI application is a PE32+
  image — so the output machinery for something that boots on real hardware is partly in place.

### What is missing — the blockers

1. **No raw pointers.** There is no address-of and no dereference in the compiler. A kernel is
   largely "poke memory-mapped hardware", and there is currently no way to name an address. This is
   the decisive blocker.
2. **No `volatile`.** The performance work teaches the compiler to keep values in registers and
   reorder them. For a status register polled in a loop, that is fatal.
3. **Hard-coded load address.** `BASE_ADDR equ 0x400000`, with no linker-script equivalent. A kernel
   needs to control where it loads.
4. **64-bit codegen only.** It cannot write the boot chain (16-bit real mode, then a 32-bit stub) —
   only the 64-bit kernel body.
5. **No naked or interrupt functions.** Interrupt handlers need no prologue and a specific return
   tail; neither is expressible today.
6. **No freestanding mode.** The standard library assumes an OS underneath it. A kernel *provides*
   those services rather than consuming them.

For comparison: the languages that do write kernels — C, Rust, Zig, Ada, Forth, Modula-2 — all share
raw pointers, `volatile`, inline assembly, no required runtime, linker control, and naked/ISR
support. Sutram has two of those six.

### The route we would take

Not a rewrite — six bounded additions, all front-end and codegen work, none of which touches the
one-pure-NASM-compiler fundamental:

1. a raw pointer type, with address-of and dereference;
2. a `volatile` qualifier;
3. output control: a configurable load address and a raw-binary mode;
4. naked functions and an interrupt attribute;
5. a configurable entry point that is not `mukhya`;
6. a freestanding mode that excludes the syscall-based library.

**The entry point we would choose is UEFI**, because the PE32+ output already exists and a UEFI
application is a PE32+ image with a defined entry — the shortest realistic path from "compiler" to
"something that boots on real hardware". It still needs raw pointers to touch hardware, so item 1
comes first regardless.

### Honest caveat

We cannot verify any of this in the build environment: no emulator, no display, no way to boot a
kernel. Any claim about actually booting would be unverified until it is run on real hardware. That
is exactly the kind of claim this project does not make.

---

## Nearer-term items

| Item | Status | Note |
|---|---|---|
| Undo in the IDE | Planned | Editor comfort; the one obvious missing editor feature |
| Verify on a real Windows machine | Planned | The largest untested area; the Windows build has never been run on Windows |
| Module system for `ayojan` | Planned | Today it inlines textually, so all library functions share one global namespace |
| Windows build of the IDE | Planned | The IDE is Linux-only today; Windows users have the interactive shell |
| XMM register residency (Stage 2) | Exploratory | Stage 1 was implemented and measured slightly slower, so the flag stays off |
| A real standard-library package format | Exploratory | Would follow the module system |
| Operating-system capability | Exploratory | Described above |

---

## What we will not do

- We will not add a runtime, an interpreter, or a dependency on another language's toolchain.
- We will not trade the fundamentals above for a feature.
- We will not describe something as working before it has been measured or run.

---

*Sutram — सूत्रम् · the complete thread*
