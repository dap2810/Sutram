# Sutram — ROUND-125: the Sanskrit dictionary verdict on the proposed names

**Read first:** `LANGUAGE-PRIORITY.md`, `docs/vocabulary/VOCABULARY-TABLE.md`, `docs/vocabulary/VOCABULARY-SHORT.md`, `docs/OPEN-ISSUES.md`.
**Deliver into:** `ChatGPT-to-Sarvam/`

## Your job, and only your job

**You are the lexicographer. I am not asking whether a name is good — I am asking whether it is a WORD, and whether the
sense is right.**

**The full table is `docs/vocabulary/VOCABULARY-TABLE.md` plus the seven sections listed below.** **For every proposed name, answer
four things:**

1. **Is it a real Sanskrit word?** Give the dictionary form — the stem, the nominal form, or the compound members. **If it
   is a fragment, say so** (`purn` vs `purna`, `vip` vs `viparyaya`).
2. **What does it mean?** The dictionary sense, in English.
3. **Does the sense fit what the function does?** **The body is the fact.** **If the word is real but names the wrong
   thing, say FAIL and why.** **Example: `nishan` is a real Hindi word for "mark", and the function computes a matrix
   trace.**
4. **Is there a better word?** If yes, give it and say why — shorter, more exact, more idiomatic.

**And one extra task: flag any name I marked KEEP that should not be kept.** **I have been wrong four times this session
on Sanskrit words; assume the KEEP rows are not safe.**

## The names I most need a verdict on

- **`karna_yog`** for matrix trace — is "sum of the diagonal" the right sense for `karna`?
- **`tadatmya`** for identity matrix — or is `ekatva` better?
- **`asti_ksham`** for a capacity check — is `ksham` the right root for "is there room"?
- **`madhava_jya`, `madhava_kotijya`, `madhava_chapsparsh`** for sine, cosine, arctangent — **are these the Aryabhatan
  words, or my coinages?**
- **`gun_tray`** for multiply-three — `traya` vs `tri`, which is right in a compound?
- **`kalana_paravalay`** and **`kalana_samalamb`** for Simpson and trapezoid — real words, or coinages?
- **`anukram_khip_asht`** — is `asht` right for 8-byte, or should it be `ashtak`?
- **`chiti_khip` / `chiti_apanay`** for stack operations — is `chiti` (heap) the right word for a stack?
- **`prati`** for return — I know it is a prefix, not a noun. **The owner has decided to keep it. Do not relitigate it;
  just say whether keeping it is defensible.**
- **`nivartan`** for return — the owner's alternative. **Is it the right noun, and is the `r` there?**

## Return

**A TSV named `ROUND-125-VOCAB-VERDICT.tsv` with columns:**
`name | english | real_word(Y/N) | dictionary_form | meaning | sense_fits(PASS/FAIL) | better_word | reason`

**Every name in the table, not a sample.** **And a short list at the top: the names you would reject, the names you would
change, and the KEEP rows that should not be kept.**

## Constraints
Least privilege. **Return raw dictionary evidence, not a summary.** **You write NO source outside your own folder.**
**Do not touch `backups/` or `Windows-to-Sarvam/`.**
