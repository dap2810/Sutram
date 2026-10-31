# Sutram — ROUND-50: the codebase verdict on the proposed names

**Read first:** `LANGUAGE-PRIORITY.md`, `docs/vocabulary/VOCABULARY-TABLE.md`, `docs/OPEN-ISSUES.md`.
**Deliver into:** `Muse-to-Sarvam/`

## Your job, and only your job

**You are the codebase reader. I am not asking whether a name is good Sanskrit — I am asking whether it fits THIS
project.**

**For every proposed name in `docs/vocabulary/VOCABULARY-TABLE.md`, answer four things:**

1. **Does it collide?** Against the 39 keywords, the 45 builtins, the 24 modules, the 305 library functions, **and the
   other proposals in the same table.** **A collision is two things with one name. Report every one.**
2. **Does the project already have a word for this concept?** **If `suchi_khip` already means insert, a new word for
   insert is a defect even if it is better Sanskrit.** **This is the check I failed when I proposed `kshep` and `uddhar`
   — you found `khip` and `apanay`.**
3. **Does it follow the existing convention?** `asti_` for booleans, `maap` for lengths, `_se`/`_tak` for direction,
   module-prefix-first. **Say where it breaks one.**
4. **What would have to change?** For each rename: every file and line that calls it. **A count, and the list.**

## The names I most need a verdict on

- **`ganit` -> `ganan`** — **does `ganan` collide with the `ganana` keyword (enum)?** **That one worries me most.**
- **`yog` in `examples/05_func_params.sm`** — it shadows `shreni.yog`. **Is shadowing safe here, or does it break if the
  example later imports `shreni`?**
- **`blend` -> `mishr` and `mixed` -> `mishrit`** — the compiler refused two `mishr`. **Is `mishrit` right, or is there a
  convention?**
- **`mala_aayam` for `pankti_len`** — `pankti` is the retired array word; `mala` is current. **Does `aayam` already mean
  something else in that module?**
- **`kosh_khip` / `kosh_apanay`** — do these clash with the `suchi_` and `chay_` families that already use the same words?
- **The 31 library renames** — for each, is the call-site count small enough that one commit is safe, or does it need
  splitting?

## Return

**A TSV named `ROUND-50-COLLISION-VERDICT.tsv` with columns:**
`name | proposed | collides(Y/N) | with_what | convention_break(Y/N) | which | sites_to_change | verdict`

**And a separate file `ROUND-50-CHANGE-SURFACE.md`: for each rename, the exact file and line list.** **That is what
Claude will apply from, so it has to be exact.**

## Constraints
Least privilege. **Read the tree, do not change it.** **PASS / FAIL / NOT-RUN separately.** **Do not touch `backups/` or
`Windows-to-Sarvam/`.**
