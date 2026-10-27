# The vocabulary: a small core, and a list

**Status: DRAFT, rewritten 27 October 2026 to ChatGPT's R115 verdict. Needs a Sanskritist for the linguistic claims.**

---

## The verdict this document now follows

**The original version of this page claimed a derivational rule - `domain_qualifier_action` - that would let a learner
place any of the 303 names.** **That claim was wrong twice over:**

- **Measured:** of 305 declarations there are **91 distinct first components and 63 occur exactly once.** **Only
 171/305 (56%) begin with their own module name.** **That is a long tail, not a rule.**
- **And the examples were invented.** **This page said `ganita_sat_yuj` implements saturating addition. That function
  does not exist** - the real name is `ganita_paripurna_yuj`.

**So the recommendation is ChatGPT's, and it is the honest one:**

> *"Use small core of recurring conventions + explicit searchable list of all 305 current callables. Not a strict
> `domain_qualifier_action` rule, and not 305 names to memorize unstructured."*

> ***"No claim that Latin underscores are formal Pāṇinian samāsa grammar."***

**That last line is the one this page needed.** **A naming convention is a naming convention.** **It is not a
grammatical derivation, and calling it one borrows authority the convention has not earned.**

---

## What a learner should actually be taught, in order

**1. The core Sanskrit grammar of the language** - `mukhya`, `vitti`, `yadi`, `anya`, `yavat`, `chakra`, `prakriya`,
`prati`. **Twenty-odd words, and they are the language.**

**2. What a module and a builtin are.** **`yoj ganita` puts you in the maths module; `likha` is a builtin.**

**3. A SMALL set of reliable word families** - the ones that recur often enough to be worth remembering as units.
**These are being measured; the list is not yet written.**

**4. Worked examples with real, verified names** - and their parameter and return expectations. **Every name in an
example must be checked against `lib/`; that is now a gate (`tools/check_doc_signatures.py`).**

**5. The complete generated reference as a lookup.** **`docs/sutram-stdlib.html`, 305 functions, signature-checked.**

**A learner needs 1 and 2 to start, 3 to become fluent, and 5 forever.**

---

## What this page is NOT

**It is not a claim that the vocabulary is systematically derivable.** **It is not a claim that a learner can predict a
name they have never seen.** **It is not a claim that the Sanskrit compounding in these names is formally correct.**

**It is a curriculum, and a list of the word families worth teaching.**

## What still needs a Sanskritist

**Whether the words chosen are the right words** - `ganita` for mathematics, `janchit` for checked, `paripurna` for
saturating. **That is a question about Sanskrit, and it is not answered here.**

---

*Draft by Sarvam. Rewritten 27 October 2026 after ChatGPT's R115 verdict and its measurement of all 305 declarations.
The earlier version of this page asserted a rule that the measurement does not support, and gave an example function
name that does not exist.*
