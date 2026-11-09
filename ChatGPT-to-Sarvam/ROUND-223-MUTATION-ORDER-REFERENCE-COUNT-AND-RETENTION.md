# ROUND-223 — mutation order, an independent reference count, and evidence retention

Reviewed main: **1c6dfc5d146e79d73564ebbcadfdce3118bc8fdf**, 9 November 2026.
Inputs: ROUND-223, adjacent Claude ROUND-161, Muse ROUND-154, current source and evidence.
**Own builds, compiler/suite/gates, PowerShell, Wine and native Windows: NOT RUN — read-side role, no toolchain used.**
Only static source/report reads, searches and file counting. No production changes, evidence deletions or Windows-folder writes.

Product files are unchanged since R222. Current setup remains **a11703c290479f46f51f02dd3b5fce9e2d635ecc9fe8fca2b6a7292f5a27ed2d**; R222 independently hashed its 2,037,248 bytes.

## WS1 — destruction before inspection: inspect the actual resource, not merely an identity field

The failure shape is **mutating a resource before capturing the state needed to decide or reverse that mutation**. Merely moving a read earlier is insufficient if it reads only InstallLocation while deleting an entire key, or if the captured state is discarded before a failure-prone operation completes.

Scope below: every mutating family found in install-core.ps1 (I), uninstall-core.ps1 (U), and the shipped wizard's staging routines. Numbers are source lines at this pin. This is not an assertion about every Windows API side effect. Directory creation through the filesystem provider must not be equated with registry-provider key recreation merely because both use New-Item.

| Mutation family | Inspection before mutation? | Disposition |
|---|---|---|
| I:479 / U:138 initial WriteAllText(LogPath) | No old content read; truncates log before installation validation | Normal wizard supplies a new private staging log. Direct script invocation against an existing log overwrites it; scoped scratch-log assumption |
| I:514 / U:148 lock OpenOrCreate + DeleteOnClose | No content/ownership read of existing lock file | **Additional reserved-path deletion case**, detailed below |
| I:549 committed transaction recursive cleanup | Read-Journal first at 546; descendants not inventoried | Journal authorizes whole private transaction directory; unrelated added contents are not individually preserved. The second read at 550 deliberately observes the removed journal, not a before-state check |
| I:588–592 extraction | New GUID staging directory, then Expand-Archive -Force and payload verification | Payload verification is after staging writes, but these are private-stage writes, not overwrites of installed payload |
| I:137–140 staging .part/staged files | Matching staged hash is reused; otherwise .part overwritten, staged destination deleted after replacement hash passes | No old .part hash; a mismatching staged file is treated as disposable private transaction data |
| I:680 redundant stage deletion | Installed target hash already equals new payload | Deletes staged copy by presence, not its own hash; private-stage policy |
| I:659 metadata backup | Existence checked; copy uses overwrite=false | Copies before overwrite, but existing backup is not replaced or verified to be this run's current before-image |
| I:663 pending manifest replacement | Existing manifest read at 613 | Read precedes overwrite; old contents remain in memory, not a dedicated durable before-image |
| I:713 / 716 / 720 payload deletion/move aside | Current target hash rechecked; superseded-copy full hash checked; operation journaled | Inspection precedes destructive step; no new destroy-before-read finding. Later races are a separate question |
| I:730 publish / I:742 obsolete-file move | Publish has staged-file and target handling; obsolete file must match prior manifest | Journal before rename. Move-Into uses non-overwriting File.Move; a conflicting destination fails rather than silently replaces |
| I:746 installed manifest rewrite | Read at 612, backed up at 653–660 | Read precedes write. Backup is eventually discarded on commit; this is upgrade recovery, not permanent undo |
| I:749 uninstaller overwrite | Hash checked at 581–585 **only when marker exists and pending is false**; metadata backup precedes overwrite | Interrupted-install path skips ordinary modification guard; see below |
| I:751 marker rewrite / I:914 state rewrite | Marker previously checked, oldState read at 537; both backed up | Read before write; state is serialized after integration changes. Interruption can leave applied changes without the new final state |
| I:270 / I:308–309 / U:59–60 PATH mutation | Read existence, raw contents and type before write/delete | Fixed ordinary preservation path. R155-01 now selects creation ownership from retained-vs-new branch |
| I:468 shortcut Save / I:473 removal / U:176 removal | Existing ownership/hash checked; preserved branch exits before Save; new hash recorded after Save | Read before overwrite/delete for recorded links; hashless records not adopted |
| I:852 class command write | Early conflict read at 573 and later read at 846 | Nonempty conflicting command refuses; matching/empty prior value not recorded for exact restoration |
| I:853 icon write | No previous icon read in setter/caller | **Overwrite before inspection**, unchanged; later matching-value cleanup cannot recover old icon |
| I:854–876 .sm default write | Non-destructive open, then hadDefault and value read before setting | Original destructive-key opening fixed. Original value kind still not retained |
| I:883 OpenWithProgids/Sutram.Source write | No previous named-value read | **Overwrite before inspection**, unchanged. U:215 also deletes without reading this value |
| I:884–895 Uninstall/Sutram key recreation and eight writes | Registration read at 518, but only location/live-install checks decide | Partial read is not a snapshot of values/subkeys. Whole-key recreation discards additional state under the stated namespace policy |
| I:917 pending removal / I:923–924 journal copy and transaction cleanup | Transaction marked committed; existing destination install-journal.log is not inspected | Private/reserved metadata policy. Existing installed journal overwritten; all committed backups then removed |
| I:929 installed install.log copy | No old destination hash/content check | **Overwrite before inspection**; I:930 hashes only the new log. U:262–264 later hash check does not protect the earlier overwrite |
| I:935 payload stage cleanup | Generated path prefix checked | Recursive cleanup, not per-entry ownership. Private-stage policy |
| U:195 / 202 class default/key cleanup | Current default equality, then key emptiness | Read before delete, but no prior installation provenance; extra nonempty branches survive |
| U:207–224 extension restoration/cleanup | Default equality checked; absent/empty record consulted; keys checked empty | Default read before restore; OpenWith named value is exception above. Empty REG_EXPAND_SZ restored as REG_SZ |
| U:231 product registration delete | Current InstallLocation matches | Whole tree removed after partial identity inspection; unrelated metadata still not individually protected |
| U:119 / 132 manifest file/directory cleanup | Manifest, safe path, current hash and directory emptiness checked | Inspection precedes removal. I:357–401 defines a similar helper but has **no call site in this install script**; do not count it as a live installer deletion path |
| U:240–248 five metadata-file removals | Manifest/state/marker have been consumed; installed journal contents not checked | Reserved names removed without current-content ownership checks. Marker/state lifetime also breaks retry below |
| U:255 uninstaller retry deletion | Exact path/hash checked at startup, not on each retry | Known self-image policy; marker/state already gone on final failure |
| U:264 installed log / U:181,267 directories | Log hash or directory emptiness checked | Read before deletion; no claim that checks make operations atomic |
| U:283–285 temporary script/log cleanup | Parent, staging-name format and exact two-entry inventory checked | Read names before removal, no content provenance; private-stage policy |
| Wizard write_file / successful cleanup | make_unique_stage creates fresh directory before CREATE_ALWAYS writes; cleanup follows engine success | Private artifacts. Deletes exact staged filenames, then non-recursive directory removal |
| Wizard make_unique_stage | GetTempFileNameW creates a unique empty temporary file; that file is deleted to create a directory | Intentional owned placeholder replacement. A race gap exists, but no sequential destruction of a preexisting ordinary file is shown |

Filesystem CreateDirectory/New-Item Directory operations at I:90,136,510,589,643,646,658,804 create/open directory locations; they do not by themselves reproduce the registry-key deletion issue. Journal and log append writes do not truncate existing bytes. Write-Durable's nonappend call is the installed-manifest replacement listed above. build-installer.ps1 selects sutram_wizard.asm; the older installer.c and sutram_setup.asm are not evidence of an additional shipped path merely because they remain in the tree.

### Additional actionable observations from this pass

**A. Existing lock file gets deleted without content inspection.** Put an ordinary file at the reserved sibling path <InstallDir>.sutram-lock, with no other process holding it. OpenOrCreate opens it, and DeleteOnClose arranges its deletion. Neither engine reads its bytes. In setup this occurs before later registration/preflight refusals, so even a failed install can consume that file. This is a deterministic source trace under the specified preconditions, **not a native result**. Define the lock as installer-owned reserved metadata explicitly, or use a locking design that does not delete a preexisting arbitrary file. Do not “fix” by deleting an occupied lock before opening it.

**B. VerifyOnly is not a no-mutation mode for existing transaction state.** I:549 committed-transaction cleanup happens before the VerifyOnly branch at 603. It also acquires the delete-on-close lock first. Therefore “verification changes nothing” is unsupported. Either put validation-only handling before destructive recovery, or document these exact housekeeping effects.

**C. Pending recovery bypasses the old-uninstaller hash check.** At I:578 the check is gated on not pending; at I:749 overwrite is unconditional. Metadata is copied into backup if that backup path is absent, but successful commit deletes the backup directory. A pending-install marker is recovery context, not proof that a subsequently modified uninstaller is still owned. Distinguish a recoverable interrupted installer image from a user-modified image, or explicitly disclose the reserved-artifact replacement policy. This is not a claim that normal, nonpending reinstall lacks its hash check.

**D. R221 retry issue remains:** U:247–248 deletes state/marker before the self-delete loop. If the loop exhausts, the next invocation fails the startup marker check. Keep the resumable state until cleanup can complete, or provide a tested recovery path.

These are bounded cases, not a reason to prohibit all writes before all reads. Ordinary creation of fresh private artifacts is appropriate. User-state replacement, private scratch cleanup and recovery-record lifetime need different contracts.

## WS2 — my count and list from the current reference

**18 current-reference correction items**, under the grouping below: **12 retained from Muse R154's list plus 6 additional items**. This is a count of identified actionable errors/overstatements/stale citations in **docs/LANGUAGE-REFERENCE.md**, not eighteen reproduced compiler bugs, nor a proof that the document has no nineteenth issue.

Two readers agreeing on a count cannot prove completeness: they may share omissions or count different documents/versions. Pin the document, classify the claims, and reconcile the individual rows.

### Twelve retained items (Muse R154 numbering in parentheses)

| # | Current text/location | Required correction and checked basis |
|---|---|---|
| 1 (M2) | line 19: generated, therefore cannot drift | Remove the guarantee. Current internal contradictions below disprove it |
| 2 (M3) | line 303: three-argument likha needs literal first | Three values print whatever comes first; line 331 says so. rfx_check_likha returns immediately before the old restriction |
| 3 (M4) | lines 376–377: at most two modules | Remove obsolete module-count bug claim. examples/99 imports seven; current source has 131072-byte expanded-source buffer, 128-entry function definitions, AST and other capacities |
| 4 (M5) | line 438: string + kosh yields E_VARTANI_CAT | Kosh operand checking precedes string concatenation classification in rfx_check_str_binop; E_KOSH_GANIT is the documented outcome to use |
| 5 (M6) | lines 945–946: rikta kosh se messages | Source msg_kosh_empty/peek_empty/dequeue_empty use “riktat koshat”; fix all three quoted messages as one diagnostic-family item |
| 6 (M7) | line 995: three-word slice descriptor | r23_gen_slice builds two qwords, 16 bytes: elements pointer and length |
| 7 (M9) | lines 1411,1416: 8272 transcript and 16-byte header | **32-byte descriptor; 8224 bytes for this kosh, but 8288 for the example's final total.** See explanation below |
| 8 (M10) | line 1460: excluded from parimita because each kosh has own region | Exclusion is the lexical allocation/budget policy; small kosh elements can be in the arena |
| 9 (M11) | lines 1392–1393: “from v284” / “now” per-kosh-region explanation | Keep historical measurements tied to their original version, explicitly end that model at v301; do not present it as current |
| 10 (M12) | line 1064: 344 examples | Independently counted 331 top-level .sm files, 347 recursively. Specify scope and measured corpus version instead of 344 |
| 11 (M13) | line 1065: R148 measured 16,385-term boundary | Muse R148 is explicitly read-only and contains no such measurement. Supply the actual contributor/fixture/commit citation; the present attribution is unsupported, not a new boundary measurement |
| 12 (M15) | line 1309: scratch escape check includes likh | r73_check_call lists other stores, not BN_LIKH. Remove the blanket coverage assertion or implement and validate the missing supported path; do not infer coverage from the builtin name table |

**Important correction to Muse's proposed arithmetic:** examples/317_r107_parimana.sm retains nirmmita(64) before making the kosh. Its current golden tests/expect/317_r107_parimana.out ends “a kosh of 1000 8288”. That is 64 + (32 + 1024*8), not 8224. Changing the transcript to 8224 would introduce another error. My R222 cited the stale totals without giving this exact replacement; this pass resolves it by reading the example and golden together. No execution here.

### Six additional current-reference items

| # | Location | Correction/basis |
|---|---|---|
| 13 | line 193 sankhya_bindu replacement advice | bindu_gunan does **not** use the shorter length: lib/sankhyiki.smlib asserts equal lengths with E_AKARA_ASAMYA before looping. Reference section 3a already agrees |
| 14 | quick start / section 7 output-target table | Scope suffix-driven ELF/PE choice to Linux-host compilation. _start's WINDOWS branch sets target_pe=1 unconditionally; .bin does not turn the Windows compiler into a Linux-target compiler |
| 15 | lines 1061–1063: widest statement / upper bound proves >200000 possible | Say widest **measured shape**. An upper bound above a threshold does not establish a realizable input above that threshold. Keep measurement and proof separate |
| 16 | line 983: no limit on how many koshes | Say no former per-small-kosh mapping-count ceiling; available memory and compiler/runtime capacities still constrain programs |
| 17 | lines 1426–1427: reclaiming waits for a stable descriptor | A stable descriptor exists since v302, as this very reference and r127 layout state. Describe the remaining reclamation/lifetime limitation without claiming the descriptor is absent |
| 18 | line 21: Compiler v29 / Package v35 | Stale unqualified metadata under the current reference title. Update it or explicitly mark it as the original document-generation snapshot, distinct from current compiler v315 |

### Why not Muse's nineteen?

- **M1 and M14 already fixed:** current line 13 describes moving elements behind a stable descriptor; current status box names v315 and 79/0/1. Muse's numbered list is pinned to 308c2161, not this tip.
- **M8 (“no crash demonstrated”) is not accepted.** Claude-to-Sarvam/evidence-r152/ffi-shape.txt explicitly records v313 ffi3, k_sum(xs, k[0:1]), segmentation fault, exit 139. R152-00 repeats the setup and result. This is **contributor-reported execution**, not mine, but it is evidence present in the repository. Keep the confirmed crash with a precise link to that fixture; do not erase it because another earlier report only showed a wrong value. Passing a descriptor as an integer need not itself crash; the foreign function's use as a count did in that reported probe.
- **M16–M19 are in MEMORY-MODEL.md's historical body**, not the current reference. The file explicitly labels that body R70 historical research and pins its snapshot SHA. These four are not current claims merely because the current implementation differs. Preserve them as history or add local “superseded” annotations; do not silently rewrite the historical observation to v315 semantics.

Arithmetic of this reconciliation: 19 - 2 already fixed - 1 disputed by saved crash evidence - 4 historical passages = **12 current-reference items**, then the six additional rows = **18**.

This does not count the original misquote as a defect, or count every sentence in one grouped fix separately. R222's gate-coverage findings are separate tool issues, not included in this reference count.

## WS3 — keep cited evidence: agreed

I agree with the decision. Keep cited outputs, scripts, probes, manifests, wildcard-covered artifacts and unique proposed source/patches. An uncited filename may still be necessary to reproduce a reported outcome: Muse's own uncited probe caveat demonstrates that.

Byte-identical content may be consolidated only with its original path/event identity, immutable recovery mapping and dependent links/commands/manifests accounted for. Equal bytes from two runs are not proof they were the same event. The 11 mappings were independently verified in R222, but the retained original EVIDENCE.sha256 paths and TSV-header mismatch still need a clear restoration/mapping workflow. No further deletion is proposed here.

A hash alone does not recover evidence. An accessible immutable historical object can; keeping evidence in the working tree avoids recovery friction. No history rewrite is needed. “Every clone breaks” is imprecise: old clones retain their history, but collaborators must reconcile incompatible history, and cited old commits may become unavailable from the rewritten remote. The practical decision to avoid that disruption is sound.

The shared-state Wine sentence also needs narrowing: sequential gates rule out simultaneous gates within that invocation, **not every race**, and 350 passing repetitions do not explain the original failure. Keep it as unreproduced/unexplained with better future capture, not “cause answered.”

## WS4 — verdict and release-note wording

**No advance YES for “v316 + nineteen fixed + one run.”** v316 has not been supplied, the count is not nineteen current-reference errors, and “one run” must mean a defined acceptance session rather than a launch.

A finite path remains:
1. Correct the actual current reference items, with the 8288 transcript and historical/crash distinctions above.
2. Resolve the locked-uninstaller retry path or supply a tested recovery procedure. Decide/document reserved file and registry policy; do not advertise exact user-state preservation while silently replacing those resources.
3. Test the final immutable package natively: ordinary install/IDE save-build-run/fresh terminal/uninstall, existing association/OpenWith state, PATH type/text and both reinstall transitions, shortcut preservation/collision/legacy states, and the targeted compiler/FFI/budget cases already assigned.
4. Record package hash, Windows configuration, results and remaining limitations. Reuse unchanged-component evidence with its original identity.

Suggested release notes:
- Current compiler: v315. Current setup: a11703c290479f46f51f02dd3b5fce9e2d635ecc9fe8fca2b6a7292f5a27ed2d; native acceptance pending, therefore candidate.
- Shared .sm keys are opened non-destructively; ordinary PATH updates preserve unrelated text/type; fresh-append ownership is fixed; modified/hashless shortcuts are preserved under the documented recorded-hash policy.
- Namespace-managed registry values, reserved metadata/logs/transaction files and lock files have narrower preservation behavior than arbitrary user files. Their policy and recovery limitations must be explicit.
- The memory chapters are delivered; the currency gate checks selected structural rules and compile/refusal/exit results, not all prose or successful stdout.
- Contributor gates report 79/0/1; native Windows is the NOT-RUN item. Historical tests and Wine results retain their tested artifacts/configurations.
- Known FFI misuse was reported to produce both a wrong value and a crash on v313; the boundary fix is retained. No general memory-safety, arbitrary FFI safety or race-freedom guarantee follows.
- Cited evidence stays; cleanup does not shrink historical clone content. Original failure records remain available.

**Conditional YES:** for the documented v1 scope after the final artifact passes that bounded native acceptance and the open recovery/preservation contract is resolved. Today: candidate. No code, build, CI, native test or cleanup action performed by this review.
