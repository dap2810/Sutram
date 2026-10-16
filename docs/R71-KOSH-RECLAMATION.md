# R71 revised workstream 2 — staged Linux kosh growth reclamation

**Source-review follow-up, 2026-10-16. Not a fully integrated compiler release.**
This responds to the revised `Sarvam-to-ChatGPT/ROUND-71.md`, Git blob
`38b607afa51f479fa6d12abbfbac740b04000e76`. Its new workstream 2 replaces the
canonical-build task with the compiler's kosh growth leak. Sarvam's correction
acknowledges the R69 return; do not repeat the withdrawn claim that R69 was skipped.

## Change and ordering

The pinned `.ge_call_koshpush` allocates a larger mapping, copies the cells, and
updates the owning variable. No release of the superseded mapping is emitted in
that path. The new preparation tool adds three narrowly scoped compiler calls:

1. **Before new-capacity arithmetic:** verify `length == capacity` on the growth
   branch and ensure `(2*capacity + 2)*8` fits a positive signed byte count. Zero
   capacity still follows the existing fallback capacity of four.
2. **Immediately after growth allocation:** reject null and Linux raw error
   returns `[-4095,-1]` before writing the header, copying or releasing storage.
3. **After successful copy and pointer publication:** release the OLD mapping
   using `munmap(old_user_pointer - 16, old_capacity*8 + 16)`. Restore the generated
   program's RAX, RCX, RDI, RSI, R11 and stack depth; preserve old R8/new R10 and
   length R9 until the existing code switches R8 to the new pointer and appends.

The conditional jump that skips growth also skips every new hook. Plain scalar
programs do not receive these payloads. Allocation and release errors terminate
with exit 1 and explicit diagnostics instead of silently proceeding. The checks
are specific to the growth path, not a general allocator audit or free API.

The implementation is NASM. The Python tool only performs a source-identity-
checked transformation and stages the unchanged include dependencies. It does
not parse Sutram, emit a substitute backend or add an application runtime.
The helper is inlined into the existing compiler source in the staged output.

## Target boundary: Linux ELF only

The inspected Windows runtime shim maps allocation to `VirtualAlloc`, but it
has no syscall-11 release branch. Adding a raw Linux syscall or trusting the
shim's default return would be wrong. Therefore this staged profile rejects
PE output containing a `kosh_push` emission with:

```
Sutram Error [E_KOSH_RECLAIM_TARGET]: reclamation profile requires Linux ELF output
```

This is deliberately a limitation, not a claim that Windows reclamation is
fixed. No Windows source or prebuilt runtime blob was changed. A Windows follow-
on requires a reviewed `VirtualFree(base, 0, MEM_RELEASE)` mapping, regenerated
embedded blobs and real Windows execution. Compiler-host platform and generated
program target are distinct; the emitter guards `target_pe`.

The original checked-in production compiler is unchanged until review. This
profile is selected explicitly by preparing and building its separate stage.
Do not replace a supported compiler or update its source lock without review.

## Allocation, aliases and what remains live

Only **superseded** kosh mappings are reclaimed. `clear`, `pop`, `dequeue`, the
last live buffer, scope exits and explicit raw allocations retain their prior
reclamation limitations. This does not implement a destructor or final kosh
release. The backing header uses the existing private layout; it is not made
into a new public ABI.

**Growth invalidates raw pointers and other aliases into old backing storage.**
This change must receive a compatibility review before default activation.
There is no ownership or borrow checker that prevents retaining such aliases.
The existing rejection of growth through a kosh parameter is retained, but does
not prove that all aliases in every program are safe. Invalid raw pointers or
corrupted headers remain outside this profile's guarantee. No concurrent-growth
or memory-safety claim is made. Tests preserve raw binary64 bits (including NaN
payloads); they do not add a universal floating-point semantics contract.

## Recommendation on a general reclamation primitive — DESIGN ONLY

**Yes, the language eventually needs an explicit final-resource reclamation
contract.** Prefer a typed owner-level disposal operation, or deterministic
cleanup for an owned buffer, over silently exposing arbitrary `munmap` as an
ordinary safe builtin. Before approving it, define ownership, post-disposal use,
repeated disposal, aliases, failure reporting, collection-header layout, platform
allocator identity and integration with `asurakshit`. An unsafe raw release may
be appropriate for systems work only with explicit base/size/allocator duties.

No new `free`, `munmap`, `kosh_free` or disposal keyword/builtin was added in this
follow-up. This paragraph is a recommendation for Sarvam and the owner, not an
implemented language rule. Fixing growth retention alone is not memory safety.

## Exact inputs and produced source

The source preparation tool fixes all thirteen input identities in its code:
12 inherited R69 compiler/include inputs and the new helper. It refuses unknown
bytes, duplicate/missing anchors, symlink source paths, existing stages and
already-patched compiler input.

- Required core input: `64ea028a5ccf56117c132a7efd0673cbe2df3fc6`, 545722 bytes.
- Canonical R68 entry: `42389aaf73179726d91e23359aee2199734036e1`, 713 bytes.
- New helper: `e9a6f5d02f2b4c98343de6f85c3442ab8890d59a`, 3680 bytes.
- Checked-in core output in this review branch: unchanged inherited core blob.
- Full staged compiler output: **not produced in this session**. The complete
  core was not available in the container, and direct retrieval failed DNS.
  The tool records the real output Git blob and SHA-256 in
  `SOURCE-IDENTITIES.json` only when run against all complete pinned inputs.

No output compiler hash is invented. Preparation unit tests use an explicit
synthetic scaffold around captured growth anchors, not a pretend full compiler.
Existing R69/R70/R71 source locks must be reconciled to a reviewed new core after
integration; do not weaken them or pass an unchecked override.

## Reproducible source and native acceptance

In a full checkout of the review branch, with an already installed toolchain:

```sh
python3 -m unittest discover -s tests/r71_reclaim -p 'test_*.py' -v
python3 tools/r71_reclaim_prepare.py --stage /tmp/sutram-r71-reclaim
cd /tmp/sutram-r71-reclaim
nasm -f elf64 -I. src/r68_compiler_entry.asm -o reclaim.o
ld -o reclaim-compiler reclaim.o
nasm -DSUTRAM_R71_KEEP_OLD_KOSH=1 -f elf64 -I. src/r68_compiler_entry.asm -o legacy.o
ld -o legacy-compiler legacy.o
```

The stage is complete for the inherited NASM includes. Build **from that stage's
working directory** so a bare original core cannot accidentally be selected.
`SUTRAM_R71_KEEP_OLD_KOSH` is an explicit A/B-only baseline: its helper emits no
new runtime instructions. It is not a suggested production configuration.

Back in the review checkout:

```sh
python3 tools/r71_reclaim_acceptance.py \
  --compiler /tmp/sutram-r71-reclaim/reclaim-compiler \
  --legacy /tmp/sutram-r71-reclaim/legacy-compiler \
  --report /tmp/r71-reclaim-native.json
```

This command must actually compile/run both integer and floating kosh growth
fixtures, match exact stdout, prove byte identity for an unaffected scalar
program, observe per-process Linux `VmSize` at two input barriers, show the
legacy retained-mapping excess, and check PE refusal/no output. VmSize is not RSS
or a timing benchmark. The bound explicitly permits 256 KiB of incidental
address-space/stack differences; it does not manufacture an exact bytes/item
claim. Candidate `.out` files are not observed Sutram output until this run passes.

Then independently run the full regression suite, kosh/type/alias cases, R65
configurations, R70 negatives, codegen/packs/proofs and frozen baselines with the
intended compiler selected. Do not rewrite accepted goldens. Include references
retained across growth in compatibility review; do not demonstrate reclamation
by intentionally dereferencing an unmapped alias.

## Actual evidence and limits

**44 tests passed as uid 1000 on Linux x86-64:** 19 native-payload test methods,
18 source-preparation methods and seven acceptance-tool methods. Native payloads
were assembled through the narrow GNU-as instruction bridge, with a C driver for
mmap/mincore and register capture. The tests executed real Linux unmapping and
checked every page of the retired mappings, retained values, register/stack
survival, zero/non-power-of-two capacity, page boundaries, raw binary64 bits,
allocation failures, oversized capacity and a real rejected unaligned munmap.

These are **not** full NASM, Sutram frontend, Windows or firmware tests. The
acceptance-tool unit methods mock compilation only to test failure handling.
No complete compiler build, staged production preparation, `.sm` memory A/B,
full regressions, Windows release or firmware boot was run here. Prior R71
module/boundary/boot/specification limits remain unchanged; see the original
combined handoff. No existing library, golden, GUI, installer or workflow changes.

## External interface references used during this implementation

- Linux man-pages, `mmap(2)` / `munmap(2)`:
  https://man7.org/linux/man-pages/man2/munmap.2.html
- Microsoft, `VirtualFree` parameter and return contract:
  https://learn.microsoft.com/windows/win32/api/memoryapi/nf-memoryapi-virtualfree

These references describe OS interfaces, not evidence that this project's full
compiler or Windows implementation has been executed.
