# R84 WS1 — Separate compilation, precise blocker (PARTIAL)

Source inspected on current main v224 commit 4c8209c935389d5f2a9c54b9c98d577fe58f514d. Assignment: Sarvam-to-ChatGPT/ROUND-84.md. The existing draft PR #41 (https://github.com/dap2810/Sutram/pull/41) already supplies the smallest independent Sutram module fixtures and strict native ELF-object harness; do NOT duplicate it.

## Existing smallest Sutram case (PR #41)
- examples/r76/module_helper.sm: prakriya joda(a,b), returns a+b, no mukhya.
- examples/r76/module_main.sm: mukhya prints joda(17,25), with no yoj textual import.
- tools/r76_module_object_probe.py compiles each separately, demands ELF64 x86-64 ET_REL before invoking GNU ld and running output 42 newline. Four fixture tests already in PR #41.

On a complete checkout including PR #41, the actual acceptance command is:

    python3 tools/r76_module_object_probe.py --compiler ./sutram_compiler --helper examples/r76/module_helper.sm --main examples/r76/module_main.sm --report /tmp/r84-two-modules.json

**NOT_RUN:** Current local host lacks NASM and a local executable Sutram compiler checkout; git clone fails DNS resolution. Therefore no actual Sutram compiler exit, stderr or generated ELF object was fabricated.

## Verified source-format blocker
Inspected src/sutram_compiler.asm at main: the write_elf routine near lines 22865-22945 explicitly writes:

    mov word [rsp+16], 2   ; ELF e_type ET_EXEC, not ET_REL=1
    mov word [rsp+18], 0x3E ; AMD x86-64
    mov word [rsp+56], 1 ; one program header

The writer emits one fixed-load executable + code, not relocatable symbol/relocation sections. File extension .o does NOT change ELF type. src/r71_module_link.inc describes only a linker substrate and explicitly says production .sm to .smo emission is NOT wired. Current yoj is textual inclusion.

## Independently executed GNU toolchain control (not Sutram)
- GNU as --64 compiled two independent handwritten assembly units into independent_link.o and independent_main.o.
- readelf -h showed Type REL / Machine AMD x86-64 on both. GNU ld linked, and running linked_demo returned exit code 42 (expected).
- NEGATIVE: ld -o should_not_link linked_demo independent_link.o returned exit 1, with exact stderr including: "ld: cannot use executable file 'linked_demo' as input to a link". A duplicate-helper error was also produced. Here linked_demo is a GNU-assembled ET_EXEC, NOT an output from Sutram.
This validates the host linker infrastructure and an ET_EXEC rejection, not real Sutram separate compilation.

## Sarvam follow-up
1. Run PR #41 probe on a complete native Linux checkout; preserve actual exit codes, stdout/stderr, e_type and SHA256.
2. If actual ET_EXEC is reproduced, introduce review-only real per-module symbol/export and relocation records, ET_REL emission and clean link acceptance before considering merge. Do not change compiler source lock or goldens just to bypass gate.
3. Draft PR #41 remains unmerged. Separate compilation IS NOT implemented, and the R84 criterion of a native Sutram-produced link/failure log is NOT fully satisfied.

Statuses: source inspection PASS; GNU two-object linker control PASS; GNU ET_EXEC rejection EXPECTED_FAILURE; native Sutram object/link NOT_RUN/BLOCKED. No source compiler changes.
