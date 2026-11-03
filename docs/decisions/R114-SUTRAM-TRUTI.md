# Decision: `Sutram Error` → `Sutram truti`, in the compiler and all eleven packs

**Authorised by the project owner, 3 November 2026.** Relayed by Sarvam in `Sarvam-to-Claude/ROUND-114.md` (commit
`3d60756`, "OWNER PERMISSION: Sutram Error -> Sutram truti in compiler and all eleven packs"). Implemented by Claude
in compiler v294 (R114). Design and inventory: ChatGPT R183 (`ChatGPT-to-Sarvam/ROUND-183-SANSKRIT-DIAGNOSTIC-PREFIX.md`).

## The rule this amends

`LANGUAGE-PRIORITY.md` (the owner, 23 October 2026): Sanskrit is the one language in development; the other ten
packs are **frozen** - "in the tree, working, no new development". A change that touches the packs "must leave
the other ten exactly as they are". `tools/sandesh.py` enforced the same thing for this token: every pack's message
had to carry `Sutram Error` unchanged.

## What was authorised - exactly this, and nothing more

- **One fixed token: `Sutram Error` becomes `Sutram truti`.**
- **Identically in the compiler and in all eleven `lang/*.sandesh` files** (the Sanskrit pack and the ten frozen
  ones) - 68 message values in each pack (748), plus the default-text comments that mirror them and the header
  line that names the token.
- **Unchanged:** every message body, every `[E_CODE]` tag, punctuation, placeholders (`{kw:...}`, `{ver}`), key
  order and key set, exit codes and behaviour. **`Sutram suchana:` stays as it is.**
- The tools and tests that enforce or match the token move with it (`tools/sandesh.py`, the goldens, the Linux IDE's
  failure check), so the rule keeps being enforced - now for `Sutram truti`.

## What this exception does NOT permit

- **No new translations, no rewritten message bodies, no new keys, no language development** in any frozen pack.
- **No other word.** It is not a precedent for changing anything else in a frozen pack. The next change to a frozen
  pack needs its own written permission.
- **Not the linker.** `sutram-link`, `sutram-elf2smo` and `sutram-coff2smo` print their own `Sutram Error`
  messages (38 strings in `linker/`). The permission names the compiler and the packs; the linker is unchanged and
  is a separate decision.
- **Not history.** Round reports, the changelog's past entries, `docs/rounds/`, `docs/reports/` and the frozen
  snapshots under `compiler/` keep the word they were written with.

## What changes for a user

- Every failure message reads `Sutram truti ...` - `Sutram truti [E_PARSE]: ...`, `Sutram truti: mala ank seema
  atikram`. Under `--lang <pack>` the token is the same; the pack's translation around it is unchanged.
- **A program compiled by v293 or earlier still prints `Sutram Error`** when it stops at run time - the message is
  in its own bytes. Rebuild it to get `truti`.
- Anything that matched the literal `Sutram Error` in output (a script, an editor) must match `Sutram truti`.

## Why `truti`

`truti` (त्रुटि) is used as the failure-severity word - "what was asked did not complete" - not as a verdict that
the program is faulty: a syntax error, a safety refusal and a resource limit all carry it, and their codes say
which. ChatGPT R183 notes that lexicons give other senses too (a tiny interval, a breaking); it is a technical
convention the owner chose. Native-speaker review: not run.
