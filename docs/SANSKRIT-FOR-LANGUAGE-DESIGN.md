# Sanskrit for language design: what is actually there

**Status: DRAFT. Sections 2-6 need a Sanskritist's review before any of it is presented as authoritative.**

**Why this document exists.** The project's aim is a language someone in India who does not read English can learn.
**The Sanskrit vocabulary serves that aim. But there is a second, larger claim available - and a false version of it
circulates widely.**

**The false version:** *"Sanskrit is the most suitable language for computers."* **It is not supported by anything.
See `docs/SANSKRIT-AND-AI-BRIGGS-1985.md`.**

**The true version, and the one this document sets out:** **the Sanskrit grammatical tradition is a FORMAL SYSTEM -
a rule-based, generative, precisely notated grammar - and several of its mechanisms solve problems that modern
language design still argues about.** **That is a claim about mechanism, not about mysticism, and it can be checked.**

---

## 1. The premise: it is a formal grammar, not a natural language

**Pāṇini's Aṣṭādhyāyī is roughly 3,976 rules that generate Sanskrit morphology and syntax from roots.** **It is
ordered, it has meta-rules, it has priority resolution, and it uses a notation designed to be unambiguous.**

**That is what a compiler front-end is.** **So the useful comparison is not "Sanskrit vs English as a source
language" - it is "the Pāṇinian method vs the methods in modern language design".**

**And several of its mechanisms have direct analogues. Some of those analogues are better than what we have.**

---

## 2. The strongest five, in order of engineering value

### 2.1 Utsarga / Apavāda - general rule, and specific override

**What it is:** a general rule (utsarga) applies unless a more specific rule (apavāda) covers the same case, and the
specific rule wins **without deleting the general one.**

**What it maps to:** **exception handling and dispatch, with priority rather than deletion.**

**Why it matters for Sutram:** **`abhava` (negation) and `anya` (else) are crude versions of this.** **A principled
utsarga/apavāda mechanism would let a function declare a default behaviour and let a caller override one case, without
the default disappearing.** **That is what trait default methods and multimethod dispatch try to do, and both are
still contested in modern language design.**

**The benefit:** **one mechanism covers error handling, dispatch and defaults**, instead of three.

### 2.2 Kāraka - the six roles

**What it is:** every participant in a sentence plays a role: **kartā** (agent, the doer), **karma** (object, what is
acted on), **karaṇa** (instrument, with what), **sampradāna** (recipient, to whom), **apādāna** (source, from where),
**adhikaraṇa** (location, where).

**What it maps to:** **named arguments with semantic roles, and argument order made irrelevant.**

**Why it matters for Sutram, and this is the sharpest one:** **our C FFI is the weakest part of the language right
now.** A foreign declaration says `s_add|2|i64,i64|i64|sutram_ffi_add` - **two integers, and nothing about which is
which.** **ChatGPT's own audit said it: *"an ELF STT_FUNC symbol never provides C argument/return types: matching
names is not ABI compatibility proof."***

**Kāraka annotations would let a declaration say which argument is the destination, which is the source, and which is
the length** - **and the compiler could check that a call matches the roles, not just the arity.** **That is a real
safety gain in the one place the language is currently unsafe.**

**The benefit:** **the FFI becomes checkable by role, not just by count.**

### 2.3 Bahuvrīhi - the possessive compound

**What it is:** a compound that names a thing **by what it HAS, not what it IS.** *"The one whose house is white"* -
the compound describes the possessor through the possessed.

**What it maps to:** **structural typing** - a type is the set of members a value has, not a name it was given.

**Why it matters for Sutram:** **we have no traits and no general polymorphism.** **Bahuvrīhi is the word-formation
pattern for exactly that idea**, and it means the concept has a name in the language's own tradition rather than being
borrowed.

**The benefit:** **traits and structural typing get a Sanskrit name and a Sanskrit derivation** - **`rachana` (struct)
plus a bahuvrīhi reading gives "a thing having these members".**

### 2.4 Pratyāhāra - naming a set by two endpoints

**What it is:** phonemes are listed in a fixed order with terminal markers; **a pratyāhāra names a whole set by its
first element and a terminal marker.** **`aṇ` is all vowels; `hal` is all consonants.** **One short token, one
precisely defined set, defined by position in an ordered sequence.**

**What it maps to:** **range notation over an ordered domain** - **character classes, enum ranges, type ranges.**

**Why it matters for Sutram:** **a language that can name a contiguous range of an ordered set in two tokens is a
language where character classes and enum ranges are cheap to write.** **Most languages make you enumerate or write a
predicate.**

**The benefit:** **compact, precisely-defined ranges** - and it is a notation, not a feature, so it costs the compiler
almost nothing.

### 2.5 Sandhi - rules for what happens at a boundary

**What it is:** when two forms meet, they combine by rule - vowels merge, consonants change, and the rules are
ordered.

**What it maps to:** **rule-governed composition at a boundary** - **macros, token joining, module interfaces.**

**Why it matters for Sutram:** **`yoj` is textual inclusion.** **It pastes one file into another with no rules about
what happens at the seam.** **Sandhi is the principled version: the boundary has rules, and the result is
deterministic.**

**The benefit:** **`yoj` becomes governed rather than textual** - **which is the difference between a preprocessor and
a module system.**

---

## 3. Three more with real value

### 3.1 Anuvṛtti - inheritance by context
**A rule inherits what is already in scope rather than repeating it.** **That is lexical scoping and implicit
parameter inheritance.** **Benefit:** less repetition at call sites.

### 3.2 Adhikāra - the governing header
**A rule that governs a range of following rules.** **That is a section-scoped default.** **Benefit:** a block can
declare a property once instead of on every line.

### 3.3 Ekasheṣa - one remains
**When two identical things would be stated, one is retained.** **That is common-subexpression elimination, expressed
as a grammatical rule.** **Benefit:** a precedent for the optimiser, and a name for it.

---

## 4. Two historical facts worth having, accurately

**These are checkable and they belong to the language's heritage - unlike the NASA myth.**

**Piṅgala's Chandaḥśāstra (roughly 300 BCE) uses a binary-like notation for metrical patterns**, and his rules for
enumerating metres generate the sequence now called Fibonacci's. **The project already has a `meru` module - Meru
Prastāra is Pascal's triangle, which is the same combinatorial family.** **So the library's name is historically
grounded, and we can say so accurately.**

**The Katapayadi saṅkhyā encodes numbers as letters**, used in Kerala mathematics to make numbers memorable in verse.
**That is a mnemonic encoding - and it is directly relevant to how error codes could be made memorable in an
Indian-language language.**

---

## 5. What this does NOT claim

**It does not claim Sanskrit is better for computers.** **It does not claim any of these mechanisms is unique to
Sanskrit** - **modern languages have independently arrived at several.** **It does not claim the tradition is
superior.**

**It claims something narrower and more useful:** **a 2,500-year-old formal grammar contains mechanisms that solve
real problems, several of them have direct engineering analogues, and naming our mechanisms after them is both
accurate and useful for a language aimed at India.**

**And it claims the honest thing about priority:** **Pāṇini got there first, and the modern names are the ones we
learn instead.**

---

## 6. What needs a Sanskritist before this is authoritative

1. **Is my description of utsarga/apavāda priority correct?** **I have described the specific rule as winning without
   deleting the general one - is that right, or does the general rule cease to apply?**
2. **Are the six kāraka the standard six, and is my gloss of each correct?**
3. **Is bahuvrīhi genuinely the possessive pattern, or am I collapsing several compound types?**
4. **Is the pratyāhāra description accurate - first element plus terminal marker defining a set?**
5. **Are Piṅgala's binary notation and the Meru Prastāra / Fibonacci connection stated correctly?**
6. **Is Katapayadi saṅkhyā described accurately?**

**Every one of these is checkable by someone who knows the tradition.** **None of them should be presented as settled
until it is.**

---

## 7. How this makes the language prominent

**Not by claiming superiority - by being the only language whose design decisions have a documented intellectual
lineage, stated accurately, and checkable.**

**A language that says *"our exception mechanism is called utsarga/apavāda because Pāṇini's rule priority solves the
same problem"* is making a claim a reader can verify.** **A language that says *"NASA said Sanskrit is best for
computers"* is making one they can disprove.**

**The first earns attention from people who care about language design. The second earns attention from people who
don't check.**

**And for the actual aim - someone in India learning to program - the benefit is simpler: the mechanisms have names
in their own tradition, so the concepts are not foreign.**

---

*Draft by Sarvam, 26 October 2026. Sections 2-6 need a Sanskritist's review. Section 1 is a claim about the
Aṣṭhādhyāyī's structure and is checkable. Sections 4 and 5 are checkable and marked as such.*
