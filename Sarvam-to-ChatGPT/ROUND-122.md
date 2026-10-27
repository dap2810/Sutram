# Sutram — ROUND-122: Sarvam → ChatGPT

**Base:** main at **v372**, compiler **v253** · **Deliver into:** `ChatGPT-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md` and `docs/PATH-TO-COMPLETION.md`. If this brief conflicts, they win.

## THE TASK: five English words in the library that ALREADY have a Sanskrit answer in the language
**The owner scanned the tree. These five are not missing translations - they are inconsistencies:**

| English in `lib/` | The project's own Sanskrit word | Already a keyword? |
|---|---|---|
| `char` (15 uses) | **`akshar`** | yes |
| `int` (5 uses) | **`anka`** | yes |
| `div` (1 use) | **`bhaj`** | used in `ganita` |
| `slice` (in prose) | **`vibhag`** | yes |
| `len` (30 uses) | **`aayam`** | chosen last round |

**So a learner meets `akshar` in the language and `char` in the library.** **This round fixes that, and only that.**

## Part 1 — Your label review settled `shodhan`

> *"`śodhana` / शोधनम् has dictionary senses cleaning, correcting, improving, and also sifting, investigation and
> examination. As a technical metaphor for exposing wrong state so the author can correct it, it is a defensible,
> appropriate debugger name."*

**Kept, and recorded with your reasoning rather than just the verdict.**

## Part 2 — The work

### WS1 — the doc impact of five renames
**Claude is renaming `char`->`akshar`, `int`->`anka`, `div`->`bhaj`, `len`->`aayam` in `lib/`, and `slice`->`vibhag` in
prose.** **Deliver every document that mentions them, as a TSV with the `mode` column you used last time**
(`KEEP_HISTORICAL`, `PROPOSE_EXACT_CURRENT`, `ALREADY_PRESENT_NOOP`, `REGENERATE_FROM_SOURCE`).

**That column saved me from rewriting archived snapshots last round.** **Use it again.**

### WS2 — the nine `kosh` words, reviewed
**The owner has approved this direction but not these words yet. Review my proposals:**

| English | My proposal |
|---|---|
| `push` | `kshep` (क्षेप, throw/place) |
| `pop` | `uddhar` (उद्धार, drawing out) |
| `cap` | `dharita` (धारिता, holding capacity) |
| `clear` | `shodh` (शोध, cleansing) |
| `empty` | `rikt` (रिक्त, empty) |
| `peek` | `iksh` (ईक्ष्, to look) |
| `dequeue` | `apanay` (अपनय, taking away) |
| `enqueue` | `yuj` (युज्, join) |

**Which are right, which are wrong, and which collide with the 38 existing keywords?** **`shunya` is already `false`, so
`empty` cannot be `shunya` - check the rest the same way.**

### WS3 — the sixth class, one paragraph.

## Part 3 — Constraints
Least privilege. **Return raw output, not descriptions of output.** PASS / FAIL / NOT-RUN separately.
**You write NO source outside your own folder.** **Do not touch `backups/`.**
