# Sutram — ROUND-128: `nivartan`, written down

**Base:** main at **v395** · **Deliver into:** `ChatGPT-to-Sarvam/`

**Read first:** `docs/WHATS-LEFT.md`, `docs/LANGUAGE-REFERENCE.md`, your own `ROUND-126-STYLE-SANSKRIT.md`.

## The owner's decision
**`nivartan` becomes the keyword. `prati` stays accepted as a legacy alias.**

**Why the alias and not a clean removal:** **`prati` is in every program written for this language, including the ones the
owner has tested on Windows.** **The alias means `nivartan` IS the keyword - it is what the reference says and what new code
writes - while no existing file stops compiling.** **The guard then proves it: 0 DIFFER.**

## The fact that makes this safe
**`prati` is a statement keyword. It never appears in program output.** **So renaming it changes NOTHING observable: every
golden file stays byte-identical, and the crash corpus behaves identically.** **The only thing that can go wrong is a file
that fails to COMPILE - and the alias prevents that.**

**Devanagari: `निवर्तन` (nivartana) for `nivartan`.** **`प्रति` stays as the Devanagari alias.**

---

## WS1 — the reference entry

**Rewrite the `prati` entry in `docs/LANGUAGE-REFERENCE.md` as `nivartan`.** **Include:**
- **`निवर्तन` and its meaning** - **the noun for "returning, turning back", from `ni` + `vṛt`**
- **that `prati` still works as an alias, and why**
- **one runnable example with its exact output**
- **and the honest note you gave in R126: `prati` is a prefix and `nivartan` is the noun, so the change is an improvement
  in precision, not a correction of an error.**

## WS2 — every place it is documented

**Find every document that shows `prati` in a code sample.** **List them, and give the exact replacement line for each** -
**in the `path | mode | anchor_exact | insert_exact_line` shape you used in R123.**

**Do not rewrite a historical changelog entry.** **A record of what was true then stays true.** **Say which you marked
KEEP_HISTORICAL.**

## WS3 — and the question I most want answered
**Is `nivartan` the right word for a keyword, or is a keyword better served by a shorter form?**

**`prati` was 5 letters; `nivartan` is 8.** **It appears in every function ever written in this language.** **So: is there a
shorter genuine Sanskrit noun for "return" that is not a fragment?** **`nivṛtti`? `pratyaya`? `pratidā`?** **If `nivartan` is
the best available, say so plainly and I will stop asking.** **If there is something better, say it now, before 1,400 sites
are migrated.**

## Return
`ROUND-128-NIVARTAN-DOCS.md` with the reference entry · **the exact-insertion list** · **the KEEP_HISTORICAL list** · and
your answer to WS3.
