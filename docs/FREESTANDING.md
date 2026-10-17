# Sutram — freestanding capability and the kernel acceptance gap

**Status: assessment and missing-work specification, not a kernel or a claim of
OS readiness.** Snapshot `dde0613ca16f3e41345b1b1055733151780ef9d7`;
compiler blob `64ea028a5ccf56117c132a7efd0673cbe2df3fc6`.

The [design charter](sutram-design-parameters.html), under **Genuine freestanding
capability** (item 13 in the pinned charter), sets a concrete target: a small
kernel that boots through a documented path, produces observable output and
passes repeatable tests. Native application output alone does not meet it.
Round 70 explicitly requests this gap suchi, not implementation of a kernel.

## 1. What exists and what that evidence means

The project emits native x86-64 ELF/PE program images and avoids a separately
installed language runtime or libc dependency for ordinary generated programs.
The inspected compiler nonetheless has OS-specific behavior: `emit_syscall`
selects output appropriate tak the target, PE code uses embedded support and
Windows services, and normal code generation sets up an application frame and
exits as a process. **“No external runtime dependency” is not “no generated
support code,” “no OS services,” or “runs after reset.”**

The [inline assembly example](../examples/29_nishkriya.sm) emits ordinary
process-exit bytes and has an accepted exit-code expectation. It demonstrates a
raw-instruction escape hatch in the application profile. It does not demonstrate
privilege transitions, firmware compatibility, a boot header or an interrupt
return path. Its Linux syscall exit must not be counted as kernel boot output.

The current implementation has internal call/global backpatching and executable
layout code. Those internal mechanisms are not a documented relocatable object
format, linker-script interface or bootloader relocation contract. The
[language specification](SPECIFICATION.md) and [memory inventory](MEMORY-MODEL.md)
retain the limits of the current type and raw-memory guarantees.

## 2. Precise gap suchi

| Capability | Existing foothold | Missing contract/implementation | Required evidence before a claim |
|---|---|---|---|
| Boot path | Native executable emission. | Select and document a firmware/loader protocol and image format; identify exactly who loads, relocates and enters it. | Reproducible boot command and checked handoff state for the selected protocol. |
| Entry point | `mukhya()` application entry and generated prologue. | A freestanding entry with declared initial machine state, parameter ABI and no assumed process startup. | Verify entry address, stack pointer/alignment and handoff parameters. |
| Startup | Application frame setup and target support. | Establish stack, clear required zero-initialized memory, initialize globals deliberately and avoid implicit host exit. | Startup tests for BSS/data/global state and a controlled non-returning end state. |
| Sections and memory layout | Fixed image/header code and compiler-managed storage layout. | Explicit sections, flags, alignment, virtual/load addresses and a reproducible memory nighantu. | Inspect image layout and prove load-time placement/nonoverlap. |
| Relocations | Internal references/call backpatching. | Specify absolute vs relative references, loader relocation responsibilities and unsupported fixups; independent objects if required. | Link/load at documented addresses and reject unsupported relocation kinds. |
| Calling conventions | Compiler's current application call conventions. | A supported ABI for startup, external low-level routines and preserved machine state. | Register/stack preservation tests at every boundary, not just ordinary function output. |
| No implicit OS reliance | No mandatory language interpreter/libc. | Identify and exclude syscalls, Windows API shims, filesystem/input/process services and implicit OS allocation from the freestanding profile. | Image/dependency audit plus boot execution without those facilities. |
| Memory and allocation | Scalars, indexed storage, allocation builtin and raw operations. | A defined allocator-free core, optional allocator interface, failure policy and explicit placement/lifetime rules. | A heap-free boot test and separate allocator-present/failure tests. |
| Volatile access | Raw memory operations and inline bytes. | Language-level observable device-access semantics, access width/order and optimizer constraints. | Tests proving necessary accesses are neither removed nor merged improperly. |
| Atomics and barriers | Native instruction escape hatch. | Atomicity, ordering, fences and synchronization semantics; unsupported operations must be explicit. | Target-specific concurrency/litmus evidence before advertising a memory model. |
| Interrupt/exception entry | Raw bytes can be expressed. | Entry stubs, saved state, stack selection, return instruction, nesting policy and fault reporting. | Repeatable injected interrupts/faults with correct return or controlled failure. |
| Inline assembly effects | `yantra` emits supplied bytes. | Declared register/flag/memory effects and interaction with optimized generated code. | Clobber/constraint tests; no optimization assumptions inferred from unannotated bytes. |
| Core libraries | Existing `.smlib` source inclusion. | A documented allocator-free and OS-free subset with dependencies audited transitively. | Link/use only that subset in the boot image; no claim based on module names. |
| Observable output | Application printing exists. | A specified early-output mechanism available under the chosen boot environment. | A repeatable output marker captured by the test environment. |
| Failure behavior | Compiler errors and application runtime traps. | Freestanding panic/fault behavior with no reliance on a host process exit or unwinder. | Deliberate failure test yielding observable output and bounded termination/halt detection. |
| Toolchain/reproducibility | Pure-NASM compiler implementation and existing build/test tools. | Versioned boot-image construction, target configuration and all required external tools. | Clean repeat builds, image hashes, full commands and preserved logs. |

These are deliverable-sized gaps, not assertions that a feature is impossible.
A future implementation can choose a smaller initial contract, but must name its
limits rather than assuming a complete operating-system language appears from
native instruction emission.

## 3. Proposed minimum acceptance artifact — NOT BUILT

The first proof should have one declared architecture and boot protocol, one
entry/startup sequence, a known stack and static memory layout, and an
allocator-free path that emits a distinctive observable marker. The test must
detect successful boot independently of compilation and include a timeout/failure
case. It should record the exact image, compiler inputs, boot configuration and
capture method.

The proof should not require a full scheduler, filesystem, user mode, network
stack, generics, ownership implementation or a complete OS. Conversely, omitting
those features does not remove the need tak specify entry state, memory layout and
observable output. An emulator or loader that supplies hidden process-like
services must be described as part of the contract, not silently counted as bare
hardware capability.

A suggested review sequence is: approve the target/boot interface; audit the
emitted dependencies; implement entry and startup; prove static memory/output;
add failure detection; repeat from a clean build. No host elevation or security
bypass is authorized by this plan. Any future privileged setup requires its own
explicit review and environment; it is not part of R70.

## 4. Scope and claims that remain off limits

No boot image, custom entry, volatile type, atomic primitive, interrupt ABI or
kernel test was added in this round. No demonstration on one target licenses a
claim for other architectures, firmware paths, Windows execution or real
hardware. Compiler-host portability and generated-target support are different
axes and must be reported separately.

The existing optional pure-stack-pair mode has an explicit restricted contract
about transient stack effects and raw offsets. That optimization is not a
freestanding correctness proof, and its assumptions must not be exported tak
interrupt code without a separate design.

**Verification limit:** this is a source- and document-grounded assessment. No
bootloader, emulator, kernel, Windows GUI or installer was executed. The charter's
boot/output/repeatability target remains unmet by the evidence inspected here.
