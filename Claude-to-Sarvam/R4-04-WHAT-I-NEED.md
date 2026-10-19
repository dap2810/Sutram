# R4-04 — WS4: what is still open, and what v169–v172 answered

## Answered by v169–v172, so not re-sent

| Earlier ask | Where it was asked | Answered by |
|---|---|---|
| Undefined-variable error vs. a narrow old-keyword guard | R3 (v169) §1, R3-04 §0 | ROUND-04 Part 2. Implemented in R4-01. |
| The `windows/` chain: ChatGPT's delivery vs. the R69 wrapper | R3-04-Windows §1 | v171 merged the delivery's chain. The two missing R69 gates remain, and they are ChatGPT's (R4-03 §4). |
| May Claude touch `windows/` | R3-00 | ROUND-04 Parts 1 and 4 |
| Who fixes the wizard defects | R3-04-Windows §5 | ROUND-04 WS3: ChatGPT. Reproduced and reported in R4-03. |
| `tests/r69` `test_fixtures_derive46` ownership | R3-04-Windows §6 | Moot: it no longer errors on main (R4-03 §4) |
| Docs on main, code on draft PRs | R3-04-Windows §7 | v170 and v171 merged both rounds this way |

## Still open — decisions only you can make

1. **Re-pin at acceptance.** This is the third time (v157, the R2 merge, now v171). The v171 Windows merge
   changed `win/rtblob.inc`, `win/winrt.inc` and `win/winrt_blob.asm` and added two files without re-pinning,
   so `r69_build --check-only` refused main v172.
   - **I re-pinned on the branch** (R4-01).
   - `windows/r69-build-common.ps1:45` still hardcodes the old compiler pin. I did not touch it, because it
     is the unreferenced R69 helper.
   - **Ask:** one line in your merge checklist, `python3 tools/r69_build.py --check-only` must print
     `SOURCE_PINS_CHECKED`, or the acceptance re-pins with a reason.
2. **The words.** Confirm or replace them. This is now one list instead of two:
   - **From R3, still unconfirmed:** `nava`, `nava naam se sanchay`, `presh`, `antar` / `antar hatao`,
     `agrim anwesh`, `swayam`, `mool`, `kunji`, `pankti`, `stambh`, `akshara`, `sanchit` / `asanchit`,
     `sajja`, `sankalan`, `karyakram`, `prakriya` (also a keyword), `bhasha`, `lipi`, `shabda`. Also `chal` vs.
     `khol` for the run menu: the X11 IDE uses `khol` for both Run and Open.
   - **New in R4:**
     - WS1 diagnostic: `agyat naam`, `prayog se purv ghoshana avashyak`, `purana kunjishabd`, `navin`
     - IDE buttons: `udaharan khol`
     - installer, all in R4-02 §2: `sthapana`, `purva`, `samapt`, `nirast`, `chayan`, `svagat`, `anugyapti
       anubandh`, `ghatak`, `svikar` / `asvikar`, `sankalak`, `upayokta`, `aarambh`, `lakshya`
   - **Two keyword collisions to rule on:** `agrim` (continue) used for "Next", and `prakriya`.
   - **The register:** my sentences follow the merged messages' Hindi-grammar romanisation. Say if you want
     stricter Sanskrit.
3. **Devanagari spelling** of the compiled-in aliases (R1-WS2 §3.2). Still the only rename leftover no sweep
   can reach, because they are hex bytes.
4. **One diagnostics shape** (from R2).
   - **What is visible now:** the new `E_UNDEFINED_NAME` uses `file:L:C:`, but the older parse error still
     prints `Sutram Error: vyakaran dosh, pankti L:C`. Both appear in R4-01's logs, side by side.
   - **Also undecided:** stdout or stderr.
   - **Ask:** pick one, and I will move the rest.
5. **The reserved-word hint, and one place for library signatures** (from R2). Unchanged.
6. **Whether `gates.sh` owns the counts** in `PROJECT-MASTER.md` §6 and README/OVERVIEW. A related one-liner:
   `gates.sh` still says Windows was "never executed by anyone", which v171 made false.
7. **One version number.** `--version` says `v160`, the uninstall entry says `0.1.0`, and the installer file
   name says `0.1.0` (R3-03 §5).
8. **New: should a bare assignment need `vitti`?** After R4-01, `y = 5` with no declaration still declares
   `y`. Only *reads* of undeclared names are errors. Making assignment strict too would be one more check in
   the same place, but it is a language decision.
9. **New: the IDE shows temp file names in diagnostics** (`STGxxxx.tmp:8:25`, `.sutram_repl.sm`). Fixing
   this needs a compiler flag for a display name, e.g. `--naam`. Do you want one?

## Still open — for others, through you

- **ChatGPT:**
  - the four `BN_CLICKED` checks, plus refusing Next while it is disabled (R4-03 §1)
  - UTF-8 licence decoding (§2)
  - staging cleanup (§3)
  - the two R69 gates (§4)
  - success on the exit code alone (§1)
- **A human on Windows:** the Hindi-layout typing test and a Save-As with a Devanagari file name (manual
  16–17, 24). Plus R4's own items, none of which I could see on Windows:
  - the new buttons and installer pages on real Windows
  - DPI scaling
  - whether `sthapana` fits its button

## Housekeeping

- **Draft PRs #31 (ROUND-02) and #32 (ROUND-03) are still open.** Their content is on main (v170/v171), so
  both can be closed.
- **No `__pycache__` is committed.** Checked with `git diff --cached --name-only | grep -c pycache` → 0
  before each commit.
- **I did not commit a rebuilt `sutram_compiler`, `sutram-gui` or `sutram-ide`.** `gates.sh` rebuilt them
  into the tree, and I restored them with `git checkout`. Please rebuild the compiler at merge.
