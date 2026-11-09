# R166-00 — WS3: the chapter now says what a block gives back, three ways, each measured on v315 first: `nirmmita` written in it, yes; a `kosh` made in it, no; a `mala` made in it, never - and returning that `mala` is not refused. `agrim` is among the ways a block ends, and a budget counts rounded-up bytes. WS2: `R158` refuses the replaced figures as current. And the correction I owe: **the privacy gate I reported as passing could not read 21 UTF-16 files or a WSL kernel version - 36 files still carried system details.** The hardened gate found them; they are normalised now.

## Release line

```
main (the commit carrying this file; SHA in my chat report): Sutram 1.0 (v315) - sampurna sutra
     compiler byte-identical to 308c2161's - this round changed no compiler, so the guard is identity
     gates: 80 PASS / 0 FAIL / 1 NOT-RUN  (sh tools/gates.sh, Linux, Xvfb; NOT-RUN = Windows execution)
     suite: NO-EXPECTATION=4 PASS=327 (331 run) · crash corpus: 227 cases + manifest, 0 failed
     installer 6f9cdbda02164cb521aa853ea920f60dd77d871eb2e70b32da3130b1ebb05018 (the books and the changelog changed;
     its 658 payload files pass the hardened privacy gate)
staged r163-output-collision 315660ec: v316, not merged - after Tuesday
R158 doc currency: 23 checks, 0 failed · R159 no personal paths: 10,844 of 10,844 tracked files inspected, 0
```

## ROUND-166, part by part

| part | state |
|---|---|
| WS1 normalisation | done in `55131d98` / `f70d85e5` - **and incomplete until tonight** (below): 36 more files |
| WS1 the three checks | digests: 700 pairs left as delivered, now explained by a verifier and a note beside each manifest; JSON keys: 3 files, no collision, and now checked per object with duplicate detection; file names: none |
| WS1 the limits | stated, and one claim corrected: "a fresh clone carries none" was wrong - a clone's checkout carries none; its history holds every string |
| WS2 `R159` | done, failed before (805 files); **hardened tonight** - it failed again, on 36 files, and passes now |
| WS2 the wrong figures in `R158` | **done**: check 9 `figures` (below); a 24-byte descriptor was already check 8 |
| WS3 the three-way rule, §2's title, §7, `agrim`, the aligned budget | **done**, both books, measured first (below) |
| WS3 `parimana()` counts capacity; a loop inside a block | done before (`d80079ca`, `55131d98`) |
| WS3 the program behind 49,920 / 392 | the chapter's own §2 program; 392 does not reproduce, 264 KB does (`env -i`); your 13,256 / 15,708 still need your programs |
| WS4 the lock | fixed in `0d0f8d15` (R163), before this brief: nothing already at the lock's path is read, deleted or taken; ChatGPT R226's follow-up agrees it is source-fixed. Not run on Windows |
| WS5 the overwrite class | staged, `315660ec`; a path through `..` refused, checked tonight |

## WS3 - what a block gives back, measured on v315 before the chapter says it

`Claude-to-Sarvam/evidence-r166/memory-claims-measured.txt` (each program, its compile, its output, its peak):

| claim | program | result |
|---|---|---|
| `nirmmita` made in a block is given back | `nirmmita(32)` in a block; `parimana()` inside and after | 80 inside, 48 after (only the `mala` below remains) |
| a `kosh` made in a block is not | `kosh k[4]` + one push in a block | `parimana()` 96 inside, **96 after** |
| a `mala` made in a block is never given back | `mala m[4]` in a block | 48 inside, **48 after** |
| ... at scale | 200,000 calls, each making a `mala` of 31 numbers in a block | `parimana()` at the end **51,200,000** (200,000 x 256); peak **49,920 KB** - as with no block |
| returning that `mala` is not refused | `nivartanam m` from inside a block | compiles, runs, prints an address |
| ... but an outer `vitti` cannot take it | `p = m` | refused, `E_VITTI_PRAKAR` (the kind rule - not the escape check) |
| `agrim` ends a block too | 200,000 passes leaving the block by `agrim` | `parimana()` 0 at the end; peak 308 KB |
| a budget counts rounded-up bytes | `parimita 1000` + `nirmmita(1000)` | **refused**, `E_PARIMITA`, exit 1 |
| | `parimita 1008` + `nirmmita(1000)` | allowed, `parimana()` 1008 |

What the chapter now says (both books):
- **§2's title** is "a block that gives back what `nirmmita` made in it" (it said "a block whose memory is given back").
- **§2** lists `agrim` with the last line, `nivartanam` and `krama` among the ways a block ends.
- **New, after "Where the block is matters":** *What a block gives back, and what it does not* - the three kinds, with
  the `mala` measurement, and "inside a block that is meant to give its memory back, take that memory with
  `nirmmita`".
- **§4:** the budget counts each `nirmmita` rounded up to 16: `parimita 1000` refuses one `nirmmita(1000)`.
- **§7:** "what `nirmmita` made inside a block comes back when the block ends, everything else when the program
  ends" (it said "memory comes back when a block ends"), and "you can tell from the program where memory is held"
  (it said "you can see" - Muse R156: there is no tool that shows where).
- **The reference** gains *Nor a `mala`* beside *Not a `kosh` of pointers*.

Muse's other R156 items (the third `E_SCRATCH_ESCAPE` shape, `parimita = N` silently not a budget, `baait`
undefined, slice bounds, creation failure, `nirmmita` returning 0) were not in ROUND-166's list; I did not take them.

## WS2 - the replaced figures, a gate

`R158 doc currency` check 9, `figures`: no current document or book may give, as current, the v284 pair
(**52,760 / 13,480 KB**), or the block peaks the re-measurement replaced (**392 KB**, **"308 or 436"**). The changelog
is history and is not read. Self-tested (all four refused, 264 and 49,920 accepted), and run over the documents at
three commits (`evidence-r166/r158-figures-on-three-trees.txt`): `d7f435a5` fails (the chapter's 392), `d80079ca`
fails (my "308 or 436"), the tree before this round passes. The v284 pair was in no current document at any of them.

## The correction: the gate I reported as passing had missed 36 files

ChatGPT's R226 follow-up said `R159` and the normaliser **fail open** in places. I tested that instead of arguing
it, and it was right in a way that mattered: **both treated a file with NUL bytes as binary, and 36 tracked files are
UTF-16 text** (PowerShell transcripts, logs, `.reg` exports). 21 of those carried the owner's projects folder, home
folder or account name. With the kernel versions no pattern looked for (a WSL kernel, platform strings), **36 files
and 185 places** still carried system details. My R164-R165-00
said "0 after"; that was the gate's answer, not the tree's.

**Now:**
- **The gate** decodes UTF-16 (a BOM, or a NUL in every other byte) and `\uXXXX` escapes before it reads; reads a
  binary for the names as ASCII and as UTF-16 (both alignments); adds lower-case drive letters, kernel builds (a WSL
  kernel, a platform string), IPv4 and MAC addresses; applies every check to each file name; **never prints a name**
  (a matching file name is shown as its number); **fails if any tracked file cannot be read**; and reports the known
  identifiers and the policy forms apart. Self-test: 22 forbidden forms (2 in UTF-16) caught, 19 placeholders pass.
  Before re-normalising it failed on 36 files (`r159-hardened-before-renormalising.txt`); after, 0
  (`r159-hardened-after.txt`).
- **The normaliser** checks every proposed file before writing any: a file it cannot read, JSON that would not parse,
  a key repeated in one object (it parses with duplicate detection - the plain parser kept the last key silently),
  a structure or a non-text value that would move, a key that would change without `--allow-key-changes`. Any of
  them: exit 1, nothing written. `--apply` requires `--record`. UTF-16 is decoded, normalised and written back in its
  own encoding; a binary is never changed. Its self-test (an invalid escape and a key collision refused, UTF-16
  round-trips) runs first, and `R159` runs it too.
- **Normalised tonight:** 36 files (30 Windows, 4 mine, 2 ChatGPT's - its two platform strings).
  `evidence-r166/normalization-record-2.json` holds before and after for all 67 files this round changed; a file
  normalised twice has a link in each record.

**What the gate still cannot see**, said so nobody reads more into a pass: text in an image, a compressed archive
or an installer's payload (the installer's payload I scanned separately: 658 files, 0), an encoding other than UTF-8
and UTF-16, and the history.

## ChatGPT's other points

- **Manifests:** `tools/verify_evidence_manifest.py` checks a manifest against the tree and labels each entry OK,
  NORMALISED (the recorded digest is a "before" in a record and the file is the last "after"), REMOVED (a screenshot),
  COPY-KEPT (a byte-identical copy removed in R159 whose kept copy matches), or MISMATCH / MISSING. All eight Windows
  evidence manifests: **every entry explained** (`evidence-r166/evidence-manifests-verified.txt`), and a
  `PRIVACY-NOTE.md` beside each says so and how to check. Historical digests are untouched. The installed-payload
  manifests (`payload.manifest.sha256`) and ChatGPT's per-round source manifests describe older trees; their
  mismatches predate the cleanup and are not privacy changes.
- **Removed screenshots:** 116 links in 31 reports (28 Windows, 3 ChatGPT's) now say *screenshot removed under the
  privacy rule, 9 November 2026; the text keeps what it showed*. No historical image URL was added.
- **The chain of records:** ChatGPT's R226 record, my R164 record, my R166 record - the verifier reads all three.

## Not done, and why

- **The history** - not rewritten; the owner's decision.
- **Muse's other R156 chapter items** - not in this round's list.
- **Native Windows** - nothing here needs it; the lock fix is still not run there.
- **Your block programs** (13,256 / 15,708 KB) - still needed to explain your figures.
