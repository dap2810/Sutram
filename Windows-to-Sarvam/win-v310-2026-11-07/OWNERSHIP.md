# v310 native installer ownership

**C4 FAIL: unequal existing superseded content causes loss of the target's prior bytes in a controlled recovery fixture.** Ordinary interrupted recovery succeeds. No user file was used as the loss probe; its sentinel bytes are retained in this evidence folder, and whole installations/transactions were moved aside before restoring the baseline.

All engine tests execute the **complete, unchanged `install-core.ps1` embedded in the pinned setup**, with its exact embedded ZIP, at the real canonical per-user destination. C2 uses two engine processes rather than two wizard windows. Initial installation and both controlled interruptions use the actual setup GUI. No mocked filesystem/registry, edited engine, security changes, or forced resume of suspended processes.

## C1 — suffix preservation

The real clean install was interrupted after `58/657` target files appeared, while a later compiler was still staged. The untouched clean interruption had no superseded directory: there was no old target to supersede. Absence alone is not a passing test.

To exercise replacement, the test seeded a known intermediate payload at `docs/BUILDING.md`, recorded its complete hash in a `STAGED` journal entry, and supplied an older backup. These are explicit synthetic owned transaction inputs. The actual engine moved those intermediate bytes to:

`transaction/backup/_superseded/docs/BUILDING.md.707D163BD76C`

Full preserved hash: `707d163bd76c4aa94e9b0c7ef56a25187645b35969a8d0bf589d644cf23e6ec8`. The filename's suffix is the first 12 uppercase hex characters. C1 passes for this fixture.

A read-only, non-delete-sharing handle on the later staged `win/sutram.exe` deliberately stops its final rename. Exit 1 is expected fixture control, preserving transaction evidence before commit cleanup. It is not an unexplained installer failure.

## C2 — concurrency and fresh state

Two actual embedded-engine processes launched `0.021868` seconds apart. One completed with exit 0; the other refused with exit 1:

```text
[2026-11-07 13:18:50] ERROR: Another Sutram installer or uninstaller is working on C:\Users\dmech\AppData\Local\Programs\Sutram. Let it finish, then run this one again.
[2026-11-07 13:19:05] Installation complete: C:\Users\dmech\AppData\Local\Programs\Sutram
```

After both exited: **657/657 payload hashes match**, no target pathname disappeared, and no pending transaction remained. Only installation log/journal/state metadata changed. [Raw process results and comparison](ownership/c2-result.json), [first log](ownership/c2-first-engine.log), [second log](ownership/c2-second-engine.log). The recorded process seconds are observation upper bounds because the controller collected the first process before the second; they are not individual exit timestamps. This proves the concurrent-start case, not every possible arbitrary-writer race or delayed state-read interleaving.

## C3 — edit during publication

During a clean run, after `docs/BUILDING.md` appeared but before the final compiler was published, the observer appended a unique line. It recorded the engine still running, the later target absent, and its staged copy present. The engine completed with exit 0; the edit survived exactly:

`d488a9b854551d76dbc4c31d790bd5ab2e900e68a140e076cf4af60f603eb53f`

[Edit bytes and observation](ownership/c3-result.json), [engine log](ownership/c3-edit-engine.log). This is the requested already-published-file case. It does not prove protection against an edit between a target's hash check and its rename/delete. The edited installation was preserved as a whole and a verified baseline restored before further testing.

## C4 — unequal superseded copy

Using the same interrupted transaction, the test installed a different journal-owned sentinel as the target and precreated its expected 12-hex-prefix backup name with **different bytes**. No hash collision is required: a filename can contain any prefix.

- Target before retry: `31c7b5e5f5bd5decad64b3e34c9939e4f5c33c73149b22762bbdfebc249d4dce`.
- Existing superseded file before/after: `bb8f7f7405c17b55c3b8ce2adbc99b82ac39060a6d3931a8aa70cd7e55295f95`.
- Target after retry: `e40e82f0c36119362825540563ff4ba6b2d09bad22e809ee4f34eb7b61c3bb69` (new payload).
- Copies of the original target hash anywhere in the installed tree or transaction afterward: **0**.

The unchanged engine journals `SUPERSEDED`, deletes the target because the named backup exists, and publishes the new file. It subsequently stops at the deliberately locked later compiler. Thus the loss is observable **before commit cleanup**. No equality-mismatch warning occurs; the only error is the intentionally blocked later rename.

The vulnerable statement is `windows/native-installer/install-core.ps1:604` at source `300c3ee5777d02b609fdbe4db83571e2c53af6cd`. [Fixture inputs](ownership/c4-unequal-existing-fixture.json), [before/after hash inventory and result](ownership/c4-unequal-existing-result.json), [actual log](ownership/c4-unequal-existing-engine.log), [journal](ownership/c4-unequal-existing-after-journal.txt), [sentinel bytes preserved outside the installation](ownership/c4-unequal-existing-owned-before.txt).

**Pathname-only comparison would miss this defect:** no target pathname disappears in either seeded fixture, because the deleted path is replaced. Content-hash comparison finds the lost bytes. C1 preserves its old hash; C4 does not. The fixtures demonstrate a reachable engine branch under seeded recovery state, not spontaneous loss during the unmodified ordinary retry.

## Every disappearance in ordinary recovery

A separate unmodified clean install was interrupted after `57/657` files, then retried successfully (engine exit 0, observed `14.969` seconds). Target inventory before/after reports:

- `payload.pending.sha256`: SHA-256 `eb7e29272129507e162ec9d858662be514dc58650e325faedeba340b9b84f643`; same bytes after retry: `target/payload.manifest.sha256`.

No other target pathname disappeared; `0` preexisting target files changed bytes. Final installed payload verification is **657/657**. [Ordinary complete inventory diff](ownership/ordinary-diff.json). The pending record's removal is expected completion, and its bytes are the installed manifest.

## Reproduction and recovery

`ownership.py` plus `ownership-controller.ps1` record all argv, process exits, fixture data, complete target/transaction inventories and hashes. The five earlier fixture journals were recovered as exact prefixes of the retained append-only journal; each prefix's full SHA-256 was verified against its contemporaneous inventory. They are not reconstructed from guessed events.

Use a dedicated test installation or preserved backup when reproducing. Keep the fixture's non-delete-sharing handle until the engine exits; otherwise normal commit cleanup removes its backups. The final working installation is v310 with matching package/manifest/uninstaller hashes, one fresh-shell PATH entry, no pending transaction and all 12 recorded installer/wizard processes closed.

Requested next change for Sarvam: eliminate deletion based on an existing prefix-name. Prefer moving to a fresh unique backup and preserving both copies; a full-hash-then-delete check alone still has a writer race. Independently reproduce and fix in a review branch, then rerun these native cases on the exact rebuilt artifact. This round's brief explicitly prohibited product changes, so **no repair or release acceptance is claimed** here.
