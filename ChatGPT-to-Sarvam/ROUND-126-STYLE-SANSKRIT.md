# Sutram — ROUND 126: Sanskrit writing style (read-side verdict)

**Assignment:** `Sarvam-to-ChatGPT/ROUND-126.md` (Git blob `ab502c9d75da6c26b3f6c984a690bc79392eb3dd`); **pinned starting `main`:** `aaaa66557073e37d838a47f190f8a5cec6b3d0ab`.
**Evidence read:** `LANGUAGE-PRIORITY.md`; `docs/reports/SANSKRIT-FOR-LANGUAGE-DESIGN.md` (draft, not linguistic certification); `docs/LANGUAGE-REFERENCE.md` (blob `86bc60620bde169a2136cd6b1e934323f94d59bb`); `src/sutram_compiler.asm`; `examples/01_hello.sm`, `02_arith.sm`, `05_func_params.sm`.
**IMPORTANT:** TODAY blocks use supported syntax/examples; AFTER blocks marked **PROPOSED** are not runnable on today's compiler unless the text says **ALREADY SUPPORTED**. Changes are additions only; existing syntax and programs must remain valid. No runtime, GC or new tool.

## P1 — printing a labelled value

**BEFORE — today:**

```sutram
mukhya() {
    vitti x = 5
    likha("x = ")
    likha(x)
    likha("\n")
}
```

**AFTER — PROPOSED (single statement, including one final newline):**

```sutram
mukhya() {
    vitti x = 5
    likha_pankti("x = ", x)
}
```

**Why (Sanskrit):** `likha_pankti` is a fixed technical "write a line" compound; it is speakable, though NOT a full inflected Sanskrit sentence.
**Compiler work:** **MEDIUM** — add a distinct built-in that emits two existing prints plus a newline; no runtime.
**Break existing programs:** **NO** — retain all `likha` arities and their behavior.

**Source correction:** the premise "three statements required" is **not strictly true**: current `likha("x = ", x)` already prints two values in one call (`src/sutram_compiler.asm:16102-16162`), followed by `likha("\n")` (two statements total). Its three-argument form means `likha(fd,buf,count)` raw write, so **DO NOT** repurpose it for a three-piece print.

## P2 — a counted loop

**BEFORE — today (existing range form, NOT C's three-clause for):**

```sutram
mukhya() {
    chakra i = 0 tak 10 {
        likha(i)
        likha("\n")
    }
}
```

**AFTER — PROPOSED optional alternative spelling:**

```sutram
mukhya() {
    chakra i = 0 arabhya 10 paryantam {
        likha(i)
        likha("\n")
    }
}
```

**Why (Sanskrit):** `ārabhya` (आरभ्य, "beginning from") and `paryantam` (पर्यन्तम्, "up to") express a more genuine Sanskrit range than the Hindi/Urdu particle `tak`; `chakra` is still a noun, so this is a readable range phrase, **not a fully grammatical Sanskrit sentence**.
**Compiler work:** **MEDIUM** — parse `arabhya … paryantam` **contextually only after `chakra`** as a new alternative, emitting exactly the old loop logic and preserving its endpoint/direction rules; do not create global reserved keywords.
**Break existing programs:** **NO** — keep `chakra i = a tak b` unchanged.

**Grammar evidence:** Cappeller [`ārabhya`](https://www.gretil.uni-goettingen.de/gretil/6_sres/2_dict/cappse_u.htm) = "beginning with/from"; `paryantam` is the Sanskrit "up to an endpoint" construction. Neither makes the whole expression a naturally inflected Sanskrit clause when numerals and raw identifiers are read aloud.

## P3 — declaring a variable

**BEFORE — today:**

```sutram
mukhya() {
    vitti x = 5
    x = x + 1
    likha(x)
}
```

**AFTER — KEEP AS IS (ALREADY SUPPORTED):**

```sutram
mukhya() {
    vitti x = 5
    x = x + 1
    likha(x)
}
```

**Why (Sanskrit):** `vitti` is a settled **technical marker**, not a Sanskrit verb saying "let there be x"; an explicit marker is clearer than silently assigning and declaring, and dictionary purism is not worth introducing shadowing/typo ambiguities.
**Compiler work:** **SMALL (zero code work)**.
**Break existing programs:** **NO**.

## P4 — returning from a function / end of `mukhya`

**BEFORE — permitted explicit return, often written mechanically:**

```sutram
mukhya() {
    likha("namaste\n")
    prati 0
}
```

**AFTER — ALREADY SUPPORTED, no new syntax:**

```sutram
mukhya() {
    likha("namaste\n")
}
```

**Why (Sanskrit):** the end of a procedure is already evident at `}`; the owner's settled `prati` ("return") remains for **explicit** returning, not an obligatory decorative final clause.
**Compiler work:** **SMALL (zero code work)**.
**Break existing programs:** **NO** — retain explicit `prati 0` and all meaningful returns.

**Source correction:** the claim "every `mukhya` ends with `prati 0`" is false as a requirement; existing `examples/01_hello.sm` and `examples/08_demo.sm` omit that return. This read-side check does not certify exit-status bytes for every platform.

## P5 — an actionable beginner error

**BEFORE — current reported diagnostic without `yoj brihat`:**

```text
Sutram Error: agyat prakriya: brihat_yuj
```

**AFTER — PROPOSED appended Sanskrit hint (keep the original diagnostic line):**

```text
Sutram Error: agyat prakriya: brihat_yuj
सङ्केतः: 'brihat_yuj' इति प्रक्रिया 'brihat' नामके विभागे अस्ति।
स्रोतसः आरम्भे 'yoj brihat' लिखतु।
```

**Why (Sanskrit):** a correct Sanskrit hint states the missing module, quotes the **exact compilable repair**, and does not substitute a vague word for a useful action.
**Compiler work:** **MEDIUM** — only when an unknown callable name has a **unique, verified declaration** in an unincluded shipped `.smlib` module, append the hint; when ambiguous or absent, preserve the existing unknown-function message alone.
**Break existing programs:** **NO** for valid source/codegen; diagnostic snapshots or consumers comparing stderr/stdout exactly **may need updating**, so preserve the first line and gate new text on verified lookup. No error-code suppression or new dependency.

## P6 — the speakable test

**BEFORE — today:**

```sutram
mukhya() {
    vitti yog = 0
    chakra i = 1 tak 3 {
        yog = yog + i
    }
    likha("yog = ")
    likha(yog)
    likha("\n")
}
```

**AFTER — PROPOSED, using ONLY P1/P2's additive syntax:**

```sutram
mukhya() {
    vitti yog = 0
    chakra i = 1 arabhya 3 paryantam {
        yog = yog + i
    }
    likha_pankti("yog = ", yog)
}
```

**Why (Sanskrit):** one can **pronounce** the actions and understand `ārabhya … paryantam` as a Sanskrit range, but the result is **NOT a grammatical Sanskrit prose sentence**: `chakra` is a noun, `yog = yog + i` is mathematical notation, and identifiers have no visible case inflection.
**Compiler work:** **MEDIUM** (only P1+P2 changes; no additional P6 machinery).
**Break existing programs:** **NO**, provided both changes are opt-in alternatives.

**Speakable verdict:** **Sutram v1 should be speakable as Sanskrit-oriented *instructions*, not claim to be fluent Sanskrit prose.** To promise genuine natural-sentence reading would require explicit case/verb agreement and nontrivial parsing, likely a large, potentially breaking language redesign; do **not** smuggle that into the v1 grammar.

## Sanskrit construction beyond the six — and Pāṇini

**"And then":** `tataḥ` (ततः, "then/thereupon") and `anantaram` (अनन्तरम्, "afterwards") are legitimate discourse connectors ([tataḥ dictionary](https://kosha.sanskrit.today/word/en/tataH), [anantaram dictionary](https://sanskritdictionary.org/anantaram)). A future **optional, contextual** separator such as `tatah` between full statements could be speakable; **recommend NOT adding it for v1**, since the line/block sequence already has the exact order and a new particle could imply hidden control flow. It would not itself transform code into grammatical Sanskrit prose.

**Pāṇini's notation:** `anuvṛtti` (अनुवृत्ति, inherited material from preceding sūtras) and `adhikāra` (अधिकार, governing scope) are genuine devices of the Aṣṭādhyāyī ([example with inherited words](https://sanskritdictionary.com/panini/7-2-61), [overview](https://www.wisdomlib.org/hinduism/essay/a-study-of-asiddha-in-the-ashtadhyayi/d/doc1906453.html)). An explicit **block-scoped governing clause** could someday reduce repeated annotations, but implicit carry-forward across statements would **hurt** beginner comprehension, source provenance and static checking. The `it` markers and pratyāhāra abbreviations are *metalanguage*, not conversational Sanskrit; borrowing their compression would not make loops spoken sentences. There is **no evidence that these ideas are unused by every existing programming language**, so do not claim worldwide uniqueness. **Recommendation: study the scoping technique, implement none in v1 without an independent specification and tests.**

**Priority:** **P1 FIRST** if any actual new syntax is authorized: compact labelled output improves the immediate beginner example, while preserving the existing `likha` API and requiring no new runtime. **P4 requires no implementation; it is already available.**

**Evidence/status:** **PASS — static source/document read and linguistic distinction.** **NOT RUN - no toolchain —** new syntax, compiler build, output parity, Linux/Windows execution and regression suite. **NOT APPLIED —** all proposed features. All other language packs stay frozen; no source, compiler, tests or backups modified by ChatGPT.
