"""Prepare the complete documentation-only handoff in main; no git mutation."""
from pathlib import Path
import hashlib,json,shutil
BASE=Path(__file__).resolve().parent.parent
for version,checkout in [('v310','windows-v310-acceptance'),('v311','windows-v311-verification')]:
    name=f'win-{version}-2026-11-07';source=BASE/'build'/checkout/'Windows-to-Sarvam'/name
    assert (source/'RESULTS.md').is_file()
    (source/'.gitattributes').write_text('# Preserve the exact bytes of raw Windows evidence, including CRLF journals.\n* -text\n',encoding='utf8')
    if version=='v310':
        p=source/'RESULTS.md';s=p.read_text(encoding='utf8')
        note='**Historical candidate:** v311 subsequently arrived and the same defect was retested. See the [separate v311 repair verification](../win-v311-2026-11-07/RESULTS.md) for the final installed machine state.\n\n'
        if note not in s:s=s.replace('\n\n','\n\n'+note,1);p.write_text(s,encoding='utf8',newline='\n')
    shutil.copy2(__file__,source/'publish-v310-v311.py')
    files=[p for p in sorted(source.rglob('*')) if p.is_file() and p.name!='EVIDENCE.sha256']
    manifest=''.join(hashlib.sha256(p.read_bytes()).hexdigest()+' *'+p.relative_to(source).as_posix()+'\n' for p in files)
    (source/'EVIDENCE.sha256').write_text(manifest,encoding='utf8',newline='\n')
    dest=BASE/'Windows-to-Sarvam'/name
    shutil.copytree(source,dest,dirs_exist_ok=True)
    for line in manifest.splitlines():
        expected,rel=line.split(' *',1);assert hashlib.sha256((dest/rel).read_bytes()).hexdigest()==expected
    print(version,'copied and verified',len(files)+1,'evidence files')

out=BASE/'ChatGPT-to-Sarvam'
v310='''# Native Windows v310: initializer verified, recovery loss reproduced

Source tested: `300c3ee5777d02b609fdbe4db83571e2c53af6cd`; setup `bb134603d70d49c4abd08112b77a5309ff447280f8754cb4e6e24cb4626bba47`; compiler `303d6eaca05ae01a1c8ac0a825d81a51965932cda003b0d9e9421e3df63f126c`.

The requested v310 verification is complete. Both unsafe global initializers refuse, valid scalar global and length controls work, 322 native suite cases pass with no failures, and balanced nesting cleanly refuses at 1023 extra pairs after testing every preceding depth. The two-global A2 snippet fails because main is absent; adding main prints 3. Do not infer class closure from that syntax test.

Actual embedded-engine concurrency and edit-during-publication pass. In a controlled interrupted transaction, an unequal file at the expected `_superseded` prefix-name causes the target's prior bytes to be deleted and replaced, with no matching copy anywhere in the installed tree or transaction. This was reproduced before commit cleanup; only test-owned sentinel data was used, and its bytes remain in evidence. A pathname-only inventory would miss the loss. The full engine/setup were unchanged.

Ordinary interrupted retry succeeds; the only disappearing pathname is the pending manifest, whose identical bytes become the final manifest. Initial native Finish: 15.678 s. All 657 installed hashes matched and all 12 installer/wizard test processes closed at this candidate's final check. Original installations and test trees remain preserved.

- [Complete results and artifact identity](../Windows-to-Sarvam/win-v310-2026-11-07/RESULTS.md)
- [Ownership reproduction, exact logs, hashes and scope](../Windows-to-Sarvam/win-v310-2026-11-07/OWNERSHIP.md)
- [Commands, all source probes and raw results](../Windows-to-Sarvam/win-v310-2026-11-07/COMMANDS.md)
- [Per-file evidence SHA-256](../Windows-to-Sarvam/win-v310-2026-11-07/EVIDENCE.sha256)

The supplied brief explicitly prohibited product changes; this round therefore made none. v311 arrived while publication was being prepared and fixes this reproduced stable unequal-copy case. Read the [separate v311 verification](WINDOWS-V311-2026-11-07.md) for the final installed state. Preserve v310's failure as dated evidence. No release acceptance is granted; no old v309 counts are relabeled.
'''
(out/'WINDOWS-V310-2026-11-07.md').write_text(v310,encoding='utf8',newline='\n')
v311='''# Native Windows v311: recovery repair verified and installed

**The v310 unequal-superseded-copy reproduction now refuses safely on v311, keeping both original files.** The upstream fix was fetched and verified without modifying product source. Source `fae5319d2abf6dc1368d683b1aa4b80a8831ab5d`; setup `134fae95dc9d79a0cc7e563bbf59e6fc69983eae950c2c2799e20dea911a286b`; compiler `9740b045ef19ebcf0300010724803d61ecd8e4d3a1e0e23523b558d1dac974fb`; engine `b08e8fcd14611f8e80385b4fc26b43189918a760a4318d2ca6da3083175f1820`.

New native executions on that candidate:

- Requested globals refuse with exact diagnostics; scalar and local-binding controls work. Both brief/original add/XOR cases refuse; length control prints 2.
- 1024 sequential nesting probes: depths 0–1022 compile; 1023 refuses with exit 1 and no executable, crash or timeout.
- 322 native suite PASS, zero FAIL/COMPILE_FAIL/TIMEOUT; 3 no-expectation cases and 6 explicit skips remain separately reported.
- Full embedded-engine concurrency, publication edit preservation, superseded suffix preservation, unequal-copy refusal and ordinary interrupted retry pass within their documented scope.
- The upstream native fixture tests pass: 19 boundary assertions (18 interruption points, 36 stop/retry runs), 14 reuse assertions, 7 lock assertions. Those AST-extracted/instrumented fixtures are distinguished from complete real-installer tests.
- GUI setup reached Finish in 23.722 seconds; final installed payload/manifest/uninstaller match the pinned artifact, 657/657 hashes, registry 1.0.311, one fresh-shell canonical compiler. All 12 full-install test wizard/engine processes closed; no lock/pending transaction remains. Prior versions and test files are preserved.

**Remaining limit:** v311 compares full hashes before deleting an equal superseded duplicate. That closes the stable unequal-copy defect, but the comparison and deletion are still separate operations under arbitrary external writers. Do not claim atomic arbitrary-writer safety. Prefer a unique preserved backup if that stronger guarantee is required. The A2 syntax probes also do not establish class-wide closure.

OOM was not rerun, as the owner's brief directed. No new IDE/full-uninstall, expression-budget-exhaustion, gate-mutation, whole-setup reproducibility or cross-platform payload-equality claim. Existing evidence remains separately pinned. This is not release acceptance.

- [Complete v311 results](../Windows-to-Sarvam/win-v311-2026-11-07/RESULTS.md)
- [Ownership details and exact refusal](../Windows-to-Sarvam/win-v311-2026-11-07/OWNERSHIP.md)
- [Commands and all new native evidence](../Windows-to-Sarvam/win-v311-2026-11-07/COMMANDS.md)
- [Per-file evidence SHA-256](../Windows-to-Sarvam/win-v311-2026-11-07/EVIDENCE.sha256)
- [v310 failure for comparison](WINDOWS-V310-2026-11-07.md)
- [All previous handoffs](WINDOWS-HANDOFF-INDEX-2026-11-06.md)

Sarvam: please acknowledge both exact candidates, independently review the unequal-copy fix and remaining race scope, and update the native acceptance record without promoting this to a release verdict. All reports/probes/logs/screenshots are published in a documentation-only commit; its Git diff is the reviewable change. Product source changes in this turn are solely the upstream v311 fast-forward, not unreviewed local changes. No automatic workflow or CI run was launched.
'''
(out/'WINDOWS-V311-2026-11-07.md').write_text(v311,encoding='utf8',newline='\n')
index=out/'WINDOWS-HANDOFF-INDEX-2026-11-06.md';text=index.read_text(encoding='utf8')
start=text.index('**Publication timing:');end=text.index("**Owner's standing")
text=text[:start]+'''**Latest machine state (7 November): upstream v311 at `fae5319d`, installed and natively verified.** All 657 payload hashes match; one canonical compiler; all recorded installer processes closed. Read the [v311 handoff](WINDOWS-V311-2026-11-07.md) first.

The [v310 round](WINDOWS-V310-2026-11-07.md) reproduced loss of controlled target bytes when an unequal backup occupied the expected prefix-name. v311 now refuses and preserves both copies in that same reproduction. Compiler controls, 322 native suite cases, concurrency/publication-edit/recovery checks and 40 upstream installer-fixture assertions pass on v311. Arbitrary-writer atomicity and full release acceptance remain unproven. Older v309 repair evidence/PR #68 stays separately pinned; compare remaining differences before any integration.

'''+text[end:]
text=text.replace('do not stop at a diagnostic-only handoff when a fix is authorised.','do not stop at a diagnostic-only handoff when a fix is authorised. The later v310 brief expressly prohibited product edits for that verification round; the newly landed upstream v311 repair was then independently tested without local source changes.')
anchor='\nThe owner-supplied instructions'
rows='''
| 15 | **[v310 native verification](WINDOWS-V310-2026-11-07.md)** | **[Full evidence](../Windows-to-Sarvam/win-v310-2026-11-07/RESULTS.md)** | **322 suite passes; globals/arithmetic/nesting/concurrency/publication-edit controls pass. C4 unequal superseded backup loses controlled target bytes before cleanup; ordinary recovery succeeds. No product edits.** |
| 16 | **[v311 upstream repair verified](WINDOWS-V311-2026-11-07.md)** | **[Full evidence](../Windows-to-Sarvam/win-v311-2026-11-07/RESULTS.md)** | **Same C4 reproduction now refuses and preserves both copies. 322 native suite passes; 19/14/7 installer-fixture assertions; real concurrency/edit/recovery passes; 657/657 installed hashes; all 12 full-install processes closed. No release acceptance.** |
'''
text=text.replace(anchor,rows+anchor)
text=text.replace('## Decisions still requested\n','## Decisions still requested\n\n- Acknowledge the new v310 reproduction and independent v311 repair verification. Retain the remaining full-hash-then-delete writer-race limitation and A2 class-inference correction. The final installed candidate is v311, not PR #68.\n')
text=text.replace('Please acknowledge this consolidated index and the latest v309 evidence;','Please acknowledge this consolidated index and both v310/v311 evidence sets;')
index.write_text(text,encoding='utf8',newline='\n')
print('Main handoffs and consolidated index prepared.')
