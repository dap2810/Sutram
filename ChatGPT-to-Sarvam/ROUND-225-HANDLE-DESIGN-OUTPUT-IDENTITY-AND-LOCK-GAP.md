# ROUND-225 — concrete region design, output identity, and R162 lock follow-up

9 November 2026. Reviewed main **d7f435a59abefa5c72846e66a1563ea99e3a610b** and Sarvam-to-ChatGPT/ROUND-225.md.
Documentation-only return; no production, test, tool, build or Windows-to-Sarvam writes.
**Own runtime checks: NOT RUN — read-side role, no toolchain used.**

## Decisions

- Build an isolated prototype of owner-scoped storage with generational handles after the current native candidate work. Do not merge it into v315 or describe it as two instructions. If the one-word raw descriptor-pointer ABI and zero extra access checks are also immutable constraints, close general automatic kosh reclamation as incompatible with those constraints.
- Use checked buffers for teaching; keep raw pointers explicitly advanced. R224 already answered bounds and role arguments under WS1 B and WS3; the answers are repeated more compactly below.
- Defer role-marked argument syntax for v1. It offers named-argument readability, not a new ownership proof.
- Compiler self-overwrite is a file-identity class, including imports and all linker inputs. Stage the fix under the agreed post-native-run schedule.
- R162 addresses installer B/C in source and D remains addressed; **A is only partially addressed**. An empty unrelated file is still deleted, and stale-lock read/close/delete has a path replacement window.

## WS1 — a design that reclaims both elements and descriptors

### Meaning of the constraints

“No runtime” must mean no external VM, collector or runtime dependency. Allocation, bounds checks and error paths already execute in the native program. The following adds emitted NASM helpers/data to the existing native implementation; it needs no GC or new borrow checker. If no additional runtime instructions or metadata are permitted at all, this feature cannot meet the requested safety contract.

This is a proposed new ABI, not a claim that the existing descriptor does this.

### Ownership and representation

Each entered mandapa has one owner record; code outside mandapa uses a process-lifetime root owner. The owner is selected when a kosh is created and never changes on append. An inner procedure appending to an outer kosh therefore allocates against the outer owner. No automatic promotion or transfer.

Use a one-word handle in variables, parameters, returns and kosh aliases, not a dereferenceable descriptor address. One concrete bounded layout:

- Low 18 bits: slot index, with slot zero reserved.
- High 46 bits: nonzero generation.
- A 256-entry root table of page pointers; each metadata page contains 1,024 slots of 64 bytes. Allocate pages lazily, keep them until process exit, reuse slots.
- Maximum 262,143 simultaneously usable slots in this prototype. Refuse allocation with a named capacity error at the cap. This is an explicit NEW simultaneous-kosh limit, not the current product's semantics; accepting it is part of accepting this particular one-word representation. It is unrelated to element count. A larger split or two-word handle is the alternative if that cap is unacceptable.
- Each 64-byte slot: generation, owner pointer, elements pointer, length, capacity, region bytes, owner-list next index, flags/free-list state — eight qwords.
- The owner record is 32 bytes: live-slot list head, chunk-list head, current chunk pointer, current chunk limit. Accounting and source-location diagnostics require additional storage if retained; these are not included in the 32-byte lower-level record price.

Aliases copy the same handle. Growth changes the single slot's elements/capacity, so all aliases observe it. Existing slice non-retention rules remain necessary because a raw element address can move.

### Storage

Small backing arrays use 64 KiB chunks owned by the region, acquired lazily and shared by its kosh values. Initial allocation and each growth charge the descriptor's owner, not the active lexical scope. Chunk headers need linkage and allocation bounds; reserve e.g. 32 bytes per chunk before 16-byte-aligned payloads. Abandoned small growth buffers stay until that owner closes. This is scope reclamation, not arbitrary freeing within a still-live owner.

At or above 64 KiB of element storage, allocate a separate page-rounded mapping sized for the requested capacity. Save its allocation size in the slot. Growth allocates/copies first, commits the slot update only on success, then releases the old separate mapping. A root-owned long-lived collection may still retain old small chunk allocations; that is a documented limitation. Do not restore any shared persistent cursor.

This avoids reserving a fixed 64 MiB region for every small kosh. One tiny kosh in each of many simultaneous owners can still consume one chunk per owner: measure that workload and tune the chunk size if needed.

### Exit and reuse

On every actual owner-leaving edge (normal exit, return, break/continue crossing it):
1. Walk that owner's slot list, saving the next index before reuse.
2. Invalidate each slot's generation and release its separate large mapping, if any.
3. Put reusable slots on a free list, retaining their incremented generation; allocation publishes the new generation only after initialization.
4. Release the owner's chunks and owner record after its slots are invalidated.

Never wrap a generation into an old value. Retire the slot permanently on exhaustion. Metadata pages remain at a bounded high-water mark; this allows validation without reading released descriptor storage. No timestamp-based uniqueness assumption is needed.

Operations must reject an invalid/stale handle before reading its owner or element pointer. Single-threaded execution is a premise. Cleanup must not invoke user callbacks that can observe partially closed state.

This dynamically detects stale handles even if an alias survives in an untyped container; no new static borrow checker is required. Existing compile-time escape refusals can still provide earlier diagnostics. It does not make forged raw addresses or foreign retained element pointers safe. Whole-kosh FFI conversion needs explicit validation followed by temporary raw exposure; foreign code that retains the pointer is outside the checked contract unless a separate persistent-copy/pinning API is designed. Do not claim this ABI is compatible with current raw descriptor consumers.

### Cost per access

Conservative checked operation:
1. Extract index and generation.
2. Load table page; reject an unallocated page and the reserved/invalid handle.
3. Compute slot address; load/compare live generation.
4. Load length and elements; check index bounds and perform the access.

Compared with today's direct descriptor access, this adds decoding, a table indirection, page validation and generation validation. It is **not one comparison total**. The owner pointer is read on growth/cleanup, not required for each element read. Bounds checks remain separate from liveness checks.

A compiler may resolve once for a straight-line loop proven not to close an owner or invalidate that slot. It must reload the elements pointer after a possibly growing call; retaining a validated descriptor does not make a cached element pointer valid after relocation. Conservatively validate every public operation first; optimize only with explicit effect evidence. No cycle or nanosecond estimate is asserted without emitted-code and hardware measurements.

### Memory and scale price

| Item | Proposed cost |
|---|---|
| Alias value | 8 bytes, same word count but changed ABI |
| Metadata root | 2,048 bytes per allocating program |
| Metadata page | 65,536 bytes per 1,024 slots, lazy/high-water retained |
| Slot | 64 bytes vs current 32 ordinary / 56 with R82, before allocator padding |
| Region owner | 32 bytes plus accounting/diagnostic fields if needed |
| Small allocation storage | shared 64 KiB chunks per owner, plus chunk headers and alignment |
| Large elements | page-rounded actual capacity, not fixed 64 MiB per kosh |

20,000,000 eight-byte elements need **160,000,000 payload bytes** at exact capacity. Geometric growth can make capacity larger: a power-of-two capacity of 33,554,432 uses 268,435,456 bytes. Copying from a 16,777,216-element capacity temporarily retains another 134,217,728 bytes: 402,653,184 total element bytes during relocation, before metadata and other allocations. These are arithmetic illustrations, not measured peaks or a mandated growth factor. Owner-aware reclamation does not remove growth's temporary peak.

A repeated workload with a bounded simultaneous owner/slot count reuses metadata and releases element storage. An indefinitely growing root collection does not plateau; no allocator can discard live elements.

### Build or close?

**Build a prototype, not a release patch.** It solves repeated creation of block-local collections without tombstones growing with total historical allocations, while supporting shared aliases and large collections. It costs an ABI change, checked access, a declared handle-cap policy, and native allocator work. “No GC, no external runtime, NASM, no new borrow checker” remains feasible; “all current raw-pointer ABI behavior, full reclamation, no extra checks” does not.

Prototype acceptance: alias reads after growth; outer-owner append from inner scope; nested cleanup and all exiting edges; stale handle after slot reuse; generation exhaustion refusal; 20M-element success and growth OOM atomicity; repeated short-owner plateau; sparse many-owner footprint; root-owner behavior; FFI boundary refusal/documentation; both native platforms. Measure access and growth separately. None run here.

## WS2 — raw bounds, answered directly

Choose checked buffers as the teaching default. Keep raw nirmmita documented for advanced interoperability.

An 8-byte length header can preserve an 8-byte *base pointer*, but arbitrary interior/raw pointers cannot recover bounds merely by reading eight bytes before themselves. A pointer+length value uses 16 bytes on this target; provenance/lifetime checking is additional.

For one allocation holding 1,000,000 eight-byte elements:
- payload = 8,000,000 bytes;
- logical header = 8 bytes (0.0001%);
- with 16-byte arena rounding, this specific payload plus header requires 16 additional allocated bytes.
For one million separate allocations, logical header cost is 8,000,000 bytes, with padding determined per allocation.

A simple unhoisted write loop executes one million bounds comparisons/conditional branches plus any required length loads. An unsigned comparison may combine negative/out-of-range rejection under the correct representation assumptions; address multiplication/overflow must also be safe. A provably in-range loop can hoist/eliminate checks. There is no honest fixed time price from the phrase “one comparison.” Measure code and elapsed time against the same unchecked loop. Runtime cost here is **NOT MEASURED**.

## WS3 — roles

**No new mandatory vibhakti feature for v1.** Optional named arguments later can provide the useful part without introducing a grammatical inflection system.

Proposed notation only: copy(source: input, destination: output). Labels make two same-typed buffers' direction explicit and eliminate a positional swap caused by forgetting the argument order. They do not reject an explicitly wrong binding such as source: output. Read/write capabilities would be a separate, stronger feature.

Cost: parser and signature metadata, label validation, parameter-name API compatibility and defined evaluation order. Evaluate written argument expressions in their written order, then bind to parameter positions. Benefit: readable calls and fewer order mistakes. Domain-specific labels are often better than one fixed set of generic roles. This recommendation does not rely on or validate the brief's Sanskrit grammatical taxonomy.

## WS4 — the output/input collision class

Current source corroborates destructive output creation: write_elf at src/sutram_compiler.asm:32668, r28_write_object at src/r28_object.inc:125, linker .write at linker/sutram_link.asm:785 use 0x241 (O_WRONLY|O_CREAT|O_TRUNC). Windows host creation also has CREATE_ALWAYS. Claude's Linux reproductions are contributor execution, not mine.

| Collision | Literal path equality sufficient? |
|---|---|
| Identical source/output spelling | Yes for this spelling only |
| a.sm vs ./a.sm; relative vs absolute | No |
| dot segments, repeated separators, parent-directory traversal | No; lexical cleanup alone is not a general filesystem identity test |
| Final-component symlink or symlinked ancestor | No |
| Two hard-link names for one file | No, even canonical path strings can differ |
| Case variants on a case-insensitive filesystem | No; global lowercasing also wrongly conflates distinct files on case-sensitive filesystems |
| Windows supported short-name aliases, junctions/reparse paths, alternate drive/volume spellings | No; resolve according to supported OS/filesystem behavior |
| Platform-specific path spelling normalization, including supported trailing-dot/space or namespace forms | No portable string rule; handle identity or explicit refusal |
| Output aliases an imported source/library/embedded input rather than the top source | Top-source comparison misses it |
| Linker output aliases any object, archive/member backing file or auxiliary input actually read | Comparing only the first input misses it |
| Two outputs/sidecars select the same destination, or a sidecar selects an input | Must validate the complete output set, not only the executable |
| Path replaced between check and destructive open | Even an initially correct identity comparison can become stale |
| Shell redirection truncates input before compiler starts | Compiler cannot reverse damage already done by its caller |

Different extensions are not protection. a.sm and a.asm collide only if filesystem identity or an actual input relationship makes them collide; do not reject names merely for sharing a stem. Byte-identical independent files are not the same file either: a content hash is not an identity test.

### Required implementation shape

Inventory every consumed file at its actual read handle, including transitive inputs, retaining handles through output validation where practical. Open an existing output **without truncation**, query its identity, compare with all protected input identities, then truncate/write using that same validated handle. Do not validate by stat(path) and reopen with O_TRUNC: that reintroduces the replacement window. If absent, create exclusively and handle a creation race by reopening non-destructively and checking, rather than falling back to unconditional truncation.

Linux: fstat identifies the opened object; compare device and inode. Windows: compare volume identity and file ID obtained from open handles, preferring the supported full-width FileIdInfo representation and handling unsupported identity queries explicitly. Refuse on identity uncertainty; do not silently fall back to string equality. Hold input handles to avoid treating reusable numeric identities as timeless.

Primary API references:
- [Linux stat/fstat](https://man7.org/linux/man-pages/man2/stat.2.html) and [open](https://man7.org/linux/man-pages/man2/open.2.html).
- [Microsoft FILE_ID_INFO](https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_id_info) and [GetFileInformationByHandle](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfileinformationbyhandle).

Atomic temporary-output publication can separately preserve an existing output on a write failure, but renaming over an input pathname still destroys that input's directory entry. It does not replace collision checks. Do not claim protection from arbitrary concurrent namespace mutation without a specified platform publication protocol. Scope the first patch to input preservation using actual validated handles; test failure paths and partial-write behavior separately.

Regression matrix for the staged patch: compiler executable/object modes and linker, identical name, dot/absolute spelling, symlink, hard link, platform case alias, imported input, nonfirst linker input, initially absent output, normal distinct output, identity-query failure, and controlled path replacement. Hash every protected input before/after refusal. Shell-redirection damage belongs in build-tool guidance, not a false compiler guarantee.

## R162 installer review — A remains open

B: VerifyOnly now returns before lock acquisition, committed-transaction cleanup and installation state reads. It still writes its supplied log and private TEMP staging, and invokes the staged compiler. The accurate promise is “does not install or mutate target installation state,” not “changes nothing.”

C: pending recovery now checks existing uninstaller bytes against previous state, journaled UNINSTALLER hashes or this setup; journal entry precedes copy. This fixes the identified missing branch statically. Same-setup recovery and modified-file refusal require native evidence. It is not protection against another program modifying files after the check.

D: retry metadata remains after exhausted self-delete attempts. Already acknowledged as source-fixed in R224; native retry proof pending.

A has two remaining issues in both copies of Open-SutramLock:
1. **Definite preservation gap:** stale = (len == 0) OR exact marker. An unrelated empty file is indistinguishable from an old empty Sutram lock and is deleted. tests/windows/test_installer_lock_file.ps1 case 3 explicitly expects deletion, so it confirms the assumption rather than testing ownership. Marker bytes alone are also a convention, not provenance.
2. **Check/use gap:** the exclusive read handle is disposed before File.Delete(Path). The subsequent deletion targets whatever is at the name then, not necessarily the object inspected. A replacement file can arrive in that gap. This is a source-level race argument; it has not been reproduced on Windows here. The fixture's held-handle case does not exercise the read/close/delete interleaving.

Smallest conservative fix: CreateNew for a new lock; refuse every pre-existing path without automatic stale deletion, explaining manual recovery. Dispose any newly created stream if writing/flushing the marker fails, before propagating failure. A stale-lock convenience feature requires a separately proven ownership/identity protocol; “read before deleting” alone is insufficient. Do not reclassify all empty files as ours to make the test pass.

The current fixture's “another process” description is also inaccurate: case 5 opens two handles in this same PowerShell process. That tests sharing refusal, not two independently running installer processes. Keep it, label it correctly, and add controlled concurrent processes if claiming interprocess recovery proof.

The R143 source-string gate checks read-before-delete and accepts empty stale files; therefore passing it does not refute these findings. No gate or PowerShell script was executed here.

Independently hashed committed Sutram-Setup.exe:
**84e36b5915172c2c2eba3b0a4379672148ea431bff43f99ffdd81eee8954cb01**.
This supersedes 67e07959. The candidate is identified, not natively accepted. A further packaged lock fix needs a new candidate hash and the corresponding lock fixtures before the wider native run.

## Other corrections and status

The brief's “returns 99.2%” should read approximately **99.2% lower measured peak RSS in that comparison**, calculated from 49,920 and 392. Those peaks do not measure a fraction of allocated bytes returned to the OS. Claude's requested remeasurement is still pending.

Muse's prune reached commit 2fac329 labeled 191/191. I did not perform deletions or certify every deletion against the evidence-retention rule in this round. No history rewrite is proposed.

Claude reports gates 79 PASS / 0 FAIL / 1 NOT-RUN and suite 327 PASS plus four without expectations. The new native lock fixtures and all this review's memory/performance/output-collision cases remain **NOT RUN — read-side role, no toolchain used**.
