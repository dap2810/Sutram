# R24-01 — WS1: the corpus manifest is right; the four files on main are not

**Branch `claude/round-24`, commit `9132b910`, draft PR #63.** It stacks on #62 (and #61, #60).
Environment: **Linux**.

## I did not regenerate the manifest, and here is why

**`SHA256SUMS` holds the fuzzer's bytes. The four files on main do not.** On main `affb99dc`:

- `mutation-15-27971`, `-37233`, `-42057` and `-574` contain U+FFFD (`EF BF BD`) where the fuzzer wrote
  bytes that are not valid UTF-8.
- They were last changed by `9c278db2` and its three siblings, the ROUND-20 merge. R21 and R22 restored
  the bytes on my branches, but **the per-file merge cannot write those bytes, so they never reached main.**
  Your merge tool writes text.
- **Regenerating the manifest "from the files as they now are" would pin inputs that are not the inputs
  that crashed.** `mutation-15-37233` as it is on main does not crash v226's compiler at all (R21-02). The
  corpus would then be guarding against a crash nobody ever saw, and the manifest would be certifying the
  damage it exists to detect.

## What I did instead: inputs your merge cannot damage

- **The four files are now stored as `NAME.sm.b64`:** base64 text, ASCII only. A text copy cannot change
  ASCII, so these survive your merge tool.
- **`tools/crash_corpus.py` decodes them,** and `SHA256SUMS` keeps the four original hashes under
  `NAME.sm`, unchanged. The manifest needs no edit at all.
- **Two new refusals,** so this cannot happen silently again:
  - a `NAME.sm` beside its `NAME.sm.b64` FAILs: `is a stale text copy of NAME.sm.b64; delete it`;
  - any `.sm` in the corpus that is not valid UTF-8 FAILs: `store it as NAME.sm.b64`.

**I simulated your merge on a copy of main.** I copied the branch's files onto main **as text**, as your
tool would, and ran the corpus:

```
FAIL  manifest: r15-original/mutation-15-27971.sm is a stale text copy of mutation-15-27971.sm.b64; delete it
... (the other three)
crash corpus: 227 cases + manifest, 4 failed
```

Then I deleted the four old `.sm` files:

```
PASS  manifest: 213 files pinned
crash corpus: 227 cases + manifest, 0 failed
```

**So for this merge: add the four `.sm.b64` files, replace `tools/crash_corpus.py`, and delete the four
`r15-original/mutation-15-{27971,37233,42057,574}.sm`.** After that the corpus is green on main, and it
stays green through any later text merge.

| Check | Environment | Result |
|---|---|---|
| `crash_corpus.py` on the branch | Linux | **227 cases + manifest, 0 failed** |
| the same on v226's compiler | Linux | 221 failed, all SIGSEGV (the four decoded inputs crash it again) |
| main + this change copied as text, old `.sm` still there | Linux | 4 failed: `stale text copy; delete it` |
| … after deleting the four | Linux | **0 failed** |

## The other failing gate on main: the modes

**Main still has all four executables at 100644.** Your tool can't fix that, and neither can a text file
from me. **The fix is one click:** the **Merge** button on PR #60 (or on #63, which contains it). GitHub's
merge is a git merge, so the mode comes with it. If you'd rather I push the mode change directly to `main`,
say so and I'll do it. I haven't, because R22 asked for it on a branch.
