# R139-00 — WS1: I did not merge PR #67. It carries compiler and runtime changes, as you feared - a different out-of-memory fix and its own slice checks. Main has had its own fixes for all of it since v308-v309, and ChatGPT has now verified v309 on native Windows: the out-of-memory exit 32 of 32, the arithmetic refusals 7 of 7, the suite 322 pass, and upgrade, clean install, interruption and recovery all complete. I took from PR #67 the two things main lacked: the `.gitattributes` line for Markdown and the builder's LF normalization. WS2: the CRLF came from a Windows checkout of Markdown that had no eol rule; it is fixed at the source, and the package build is now byte-exact from any checkout. WS3: the arithmetic decision is done - refused, in v309.

## Release line

```
gates: 75 PASS / 0 FAIL / 1 NOT-RUN   (sh tools/gates.sh, Linux, Xvfb; NOT-RUN = Windows execution)
suite: NO-EXPECTATION=4  PASS=327  (331 run)
Sutram 1.0 (v309) - sampurna sutra      (compiler unchanged since 01f1171)
```

- **Commit:** the one carrying this file (SHA in my chat report).
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **The guard: NOT re-run, because no compiler, runtime, library or language-pack byte changed** this round. `src/`, `win/`, `lib/`, `lang/` and the binaries are as at `01f1171`. The v308 → v309 guard (R137-00) stands.
- **The installer is rebuilt** (the builder, the engine and the release notes changed): `Sutram-Setup.sha256` = `a11098537e1d5b4247fb188df95a51c16d99802d30cb3c22e4c37598ca752cf2`, `PASS payload v309 = compiler v309`, `--self-test` exit 0 under Wine. **This is not the package ChatGPT tested** (`9d046b4e...`); the compiler inside is the same.

## WS1 - PR #67: what it carries, and why it is not merged

**Does the branch carry anything beyond the installer? Yes.** `edac959a` (base `e282e237`, v307) changes:
- **`src/sutram_compiler.asm`, +121 lines:** its own slice-escape checks. `r127_check_slice_value` is extended to cells, fields, globals and scalar parameters, and sees through `?:` and `+ 0`.
- **`win/winrt_blob.asm`, `win/rtblob.inc`, `win/pe_imports.inc`, `win/pe_layout.inc`:** its own out-of-memory fix - `TerminateProcess` instead of `ExitProcess` after the message, a new import.
- **The installer and docs:** `.gitattributes`, `build-installer.ps1`, `install-core.ps1`, the installer README, `docs/MEMORY-MODEL.md`.
- **Tests:** `tests/windows/test_installer_io.ps1`, `tools/test_v307_fix_regressions.py`.

**Why not merge it:**
- **Each of its compiler and runtime fixes has a counterpart on main that was built after it and verified natively:**

| PR #67 | main |
|---|---|
| slice checks at each destination | v308: one predicate for every door; v309: a slice is not a number in any expression. Gates R134 (27) and R137 (59) |
| `TerminateProcess` after the out-of-memory message | v308: a 64 KiB commit reserve released before the message. **Native v309: 32/32, no `0xC00000FD`** |
| per-file replace with `File.Replace`; identical files left alone | v308: a journaled transaction (stage, back up, rename in); v309: lock and re-check; R140: identical files not even staged |
| log through a shared write handle | v308 (R136): the same, plus retries and never failing the run |

- **Merging would put two implementations of each fix on main,** written against v307 and conflicting with v308-v309 in the same functions. **Your rule - the out-of-memory fix is a different release condition - is better kept by not taking a second one.**

**What main lacked, and now has from it:**
- **the `.gitattributes` rule for Markdown and the other payload text** (WS2 has the scoped version);
- **the builder's LF normalization,** in `build-installer.ps1` as ChatGPT wrote it, and in the Linux builder.

**After the change, the installer gates pass** on the rebuilt package:
- `installer version`: PASS (payload v309 = compiler v309);
- `R93 installer gate`: 11/0;
- `R130 installer engine`: 16/0;
- `R134 install transaction`: 25/0;
- `R140 package` (new): 7/0.

## WS2 - where the CRLF came from

**A Windows checkout.**
- Git for Windows checks text out as CRLF (`core.autocrlf=true`).
- The root `.gitattributes` forced LF only for sources: `*.sm *.smlib *.asm *.inc *.lang *.sandesh *.sffi`.
- **Markdown, HTML and the example outputs had no rule,** so on Windows they arrived as CRLF.
- **The committed bytes were always LF:** `git ls-files --eol` shows all 514 files under `docs/`, `examples/`, `README.md` and `LICENSE.txt` as `i/lf`.
- A package built from that checkout (`build-installer.ps1`) therefore carried 153 files whose bytes differed from the installed, Linux-built copies.
- **On the v309 package, the new gate finds exactly 153 payload text paths without an eol rule.**

**Fixed at the source:** `.gitattributes` now gives `text eol=lf` to:
- every text file the installer carries (`/README.md`, `/LICENSE.txt`, `docs/**` Markdown, HTML and text, `examples/**` Markdown, `.out`, `.exit` and text);
- the installer's own scripts, which the wizard embeds (`windows/native-installer/*.ps1`, its README).

**Scoped to those paths on purpose:** the partners' folders have committed CRLF and mixed files, and a global `*.md` rule would turn them into modified files on the next checkout. **No committed file's bytes changed;** `git status` shows only the edited files.

**Belt and braces, in both builders:** text in the staging folder is normalized to LF before it is hashed.
- `tools/build_installer_linux.py` also normalizes the copies the wizard embeds (the scripts and `LICENSE.txt`).
- It also writes every ZIP entry with a fixed date (1980-01-01) and fixed attributes, and links the wizard with `--no-insert-timestamp -s`. **Without `-s` the wizard carried the absolute path of its build folder.**

**Measured here:**
- **I built the package twice:** once from this tree, and once from a copy in another folder where all 514 docs/examples/root text files and both installer scripts were converted to CRLF and every file was dated 400 days earlier.
- **Both builds: `a11098537e1d5b4247fb188df95a51c16d99802d30cb3c22e4c37598ca752cf2`, the same bytes.**
- Before the last two fixes the two builds differed: first by the embedded `LICENSE.txt` (CRLF), then by the build path. That is how they were found.

**The release note says it as observed, not as cause:**
- a package built from a CRLF checkout had 153 files that differed from the installed copies, and an upgrade replaced them all;
- that upgrade was suspended by Acronis, and the same upgrade from an LF package was not;
- **one observation, not an established cause.** ChatGPT's v309 handoff says the same: no causal relation to a security product is established.

**And the engine (ChatGPT's v309 item 3):** a late retry restaged all 657 files. Now a file already installed with this payload's bytes is not copied at all (`Already installed n/N`). A rerun after a late stop copies nothing it does not need to.

## WS3 - the arithmetic decision: done, refused (v309)

`k[0:1] + 0` and every other operator on a slice is `E_VIBHAG_ANKA` from v309 (R137-00, R138-00).
- **Native Windows confirms it:** both original reproductions (add and XOR, the 7/99 stale read) are refused with exit 1 and no executable; four broader forms are refused; `pankti_gan(k[0:2])` prints 2.
- **"The only measured defect in the language" is closed at that measurement.** As R140 asks, I do not claim every slice expression is closed: the gates test the forms found so far.

Evidence: `Claude-to-Sarvam/evidence-r139-r140/`.
