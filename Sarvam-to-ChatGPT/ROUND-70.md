# Sutram — Round 70 handoff: Sarvam → ChatGPT

**Date:** 2026-10-16
**Base:** main — your R68 is merged, Muse's R26 is merged.
**New this round:** the project now has a written **design charter**. Read
`docs/sutram-design-parameters.html` before starting. It states the 19 requirements Sutram is being
built to satisfy, each with an honest status. **This round works toward that charter.**

## Why this round is different

Until now we have been adding features round by round. The owner has now written down what the language
is *for*, and the charter names the gaps plainly. The most important line in it:

> **Do not claim safety, portability, performance superiority, or OS readiness without corresponding
> evidence.**

That is the standard for this round. Everything below is source work toward the charter, and every claim
must be one you can demonstrate.

## The charter's own ordering — work in this order

1. Stabilise the foundation — semantics, correctness, procedural core, type rules, diagnostics, tests.
2. Make substantial programs manageable — modules, visibility, separate compilation, resource
   management, error handling, core libraries.
3. Prove systems capability — freestanding, hardware interfaces, a documented boot path, a tested
   minimal kernel.
4. Add reusable abstractions — generics, traits, methods, first-class functions, closures, collections.
5. Expand carefully — concurrency, async, targets, interoperability, metaprogramming.

**We are at step 1–2.** Do not jump ahead to step 4.

## Workstream 1 — a written specification for what already exists
The charter's item 19 asks for evaluation order, numeric behaviour, error semantics and Unicode
behaviour to be *specified*, not just implemented. Write `docs/SPECIFICATION.md` covering what the
compiler **already does and is already tested for**: operator precedence and associativity, evaluation
order, integer and float behaviour including overflow, string and byte semantics, the keyword grammar,
and the language-pack resolution rules. **Specify only what the tests already pin down.** Where behaviour
is untested, say "unspecified" — that is a finding, not a failure.

## Workstream 2 — invalid programs that must be rejected
The charter asks for tests of invalid programs, not only valid ones. The suite has compile-fail
expectations; extend them into a systematic **negative corpus**: for each category (bad type, bad arity,
unknown identifier, malformed literal, unterminated string, misplaced keyword), at least one program that
must be rejected, with the diagnostic it must produce. Table it.

## Workstream 3 — the memory model, specified before it is claimed
Item 10 is "not started", and the charter is emphatic: *specify the rules before claiming memory safety*.
**Do not implement ownership this round.** Write `docs/MEMORY-MODEL.md` describing what the compiler does
today — allocation, lifetime, what is freed and what is not, what can leak, what is undefined — and then
the **proposed** ownership rules, marked clearly as design and not implemented. This is the document a
future implementation will be built against.

## Workstream 4 — the freestanding path, honestly assessed
Item 12 is partial and the charter names the acceptance target: **a small kernel that boots through a
documented boot path, produces observable output, and passes repeatable tests.** We are not there.
Assess honestly what exists (the compiler emits native ELF/PE with no runtime and no libc;
`nishkriya` gives inline assembly) and write `docs/FREESTANDING.md` stating exactly what is missing to
reach that target — entry point, sections, relocations, startup, volatile access, atomics. **A precise
gap list is the deliverable, not a kernel.**

---

## Safety constraints — hard requirements
- **Least privilege.** No UAC, no admin, no HKLM, no registry beyond HKCU, no disabling safeguards.
- **No credentials** anywhere — placeholders only, including tests, CI and commit messages.
- **No new network access. No push-triggered workflow** — `workflow_dispatch` only.
- Do not rewrite accepted goldens. Do not touch `lib/*.smlib` (Muse's side).
- **Fail closed on unknown input**, as your R67/R68 tools do.
- **Preserve the constraint:** Sanskrit keyword core · `.sm` · one pure-NASM compiler source · native
  machine code · no runtime dependency · no toolchain for the end user.

## Definition of done
- Four documents, each honest about what is specified versus unspecified, or done versus not done.
- The negative corpus as tests that actually run and pass.
- One honest line per workstream on what you could not verify.
- State the compiler input blob your tool requires and the output blob you produced.

**A verified partial beats a claim.** That sentence is now the project's standard, and this round is
where it starts being applied to the language's design, not just its code.
