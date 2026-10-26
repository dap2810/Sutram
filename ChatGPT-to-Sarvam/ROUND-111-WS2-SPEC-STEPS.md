# ROUND-111 WS2 — numbered application sequence with an immediate check

Order follows LANGUAGE-PRIORITY.md and docs/PATH-TO-COMPLETION.md; Sanskrit v1.0 active, the other ten packs frozen. Recheck live main because the canonical path has an older last-updated snapshot.

1. Pin live main, priority, canonical path and latest partner reports. CHECK: record exact commit, current source blobs, branch/release distinction.
2. Reconcile the callable rename. Muse R35 has now changed lib/chandas.smlib:82 from meru_pankti to meru_mala and updated its caller. CHECK: current source+HTML both meru_mala, no source-level old declaration; native caller migration evidence is Muse-reported, not ours.
3. Review current copyable source comments (owner: Muse/Claude). Prioritize lib/sadhan.smlib:4 Usage: ayojan util -> yoj sadhan; inspect 19 comment-level pankti references contextually. CHECK: no active obsolete instructions; preserve historical prose and intentional negative tests.
4. Regenerate docs/sutram-stdlib.html from approved source (Muse/tools owner). CHECK: all 24 current modules and 305 declarations have one matching documented signature each; recheck if source counts change; generated commentary must be independently reviewed.
5. Run the new docs signature floor after the tools-owner reviews and copies it to tools/. CHECK: exit 0, raw counts, both-direction mismatches empty, no parser/duplicate errors. THIS is static only; any failure blocks the docs publishing claim.
6. Audit current reader-facing claims (Sarvam). CHECK: reflect actual C FFI, object/ELF support, Windows branch-vs-main-vs-release and limitations; no unsupported blanket claims.
7. Maintain one pinned SPEC-STATUS and current ABI/overflow references (Sarvam). CHECK: mark implemented, branch-tested, proposed, historical separately; describe actual --ffi CLI, pointer/string future proposal, MS x64 positional arguments, size-before-address rules.
8. Expand to controlled runnable documentation fixtures (authorized tools owner). CHECK: every executable example classified, compiled using approved exact binary with output/exit receipts; preserve negative legacy-keyword fixture; never auto-execute arbitrary PowerShell.
9. Windows channel and owner: finish merge, exact merged-tree real Windows acceptance, mixed i64/f64 ABI and installer packaging. CHECK: independent non-elevated Windows raw receipts and package hashes. A Linux pass cannot replace this.
10. Owner: decide type-on-variables and approve final Sanskrit v1.0 freeze/release; only afterwards resume other ten packs and broader performance testing. CHECK: explicit decision, current release-binary acceptance, remaining P0 blockers closed.

At every step: stop on failure, identify an owner, pin evidence, verify any GitHub write by readback. No non-Sanskrit pack, compiler, lib, tests, tools, Windows or backups were changed by the read side.
