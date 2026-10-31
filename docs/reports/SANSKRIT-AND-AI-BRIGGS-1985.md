# Sanskrit and AI: what the NASA paper actually says

**Why this document exists.** A claim circulates widely in India: *"NASA declared Sanskrit the most suitable
language for computer software."* It is repeated in newspapers, by politicians, and in project proposals. **It is
false, and this project must not repeat it.** This page records what the source actually says, so that any AI or
person working on Sutram can cite it accurately - and so that our documentation is more rigorous than the claim it
declines to repeat.

---

## 1. The paper is real

- **Title:** *Knowledge Representation in Sanskrit and Artificial Intelligence*
- **Author:** Rick Briggs, then at **NASA's Ames Research Centre**
- **Published:** *AI Magazine*, Spring 1985

So the phrase "a NASA researcher wrote a paper on Sanskrit" is **true**. Everything that follows from it usually
is not.

## 2. What the paper actually argues

**It is about Natural Language Processing - making a human language digestible to a computer as *input*. It is not
about programming languages, and it is not about Sanskrit being a better language to write programs in.**

Briggs' claim is narrower and more interesting: that the method the ancient Indian grammarians used to analyse a
sentence is **structurally equivalent to the semantic networks** AI researchers were independently building.

In his own words:

> *"This article demonstrates that a natural language can serve as an artificial language also, and that much work
> in Artificial Intelligence has been reinventing a wheel millennia old."*

> *"Among the accomplishments of the grammarians can be reckoned a method for paraphrasing Sanskrit in a manner
> that is identical not only in essence but in form with current work in Artificial Intelligence."*

**The worked example is a sentence**, not a program:

> *"Maitrah sauhardyat Devadattaya odanam ghate agnina pacati."*
> "Out of friendship, Maitra cooks rice for Devadatta in a pot over a fire."

Briggs shows this analysed into an agent, an object, an instrument and a location - **a knowledge-representation
exercise.** The engineering content is in the *analysis of meaning*, not in code generation.

## 3. The claim that is false

**"NASA said Sanskrit is the most suitable language for computer software."**

| Claim | Status |
|---|---|
| Briggs was at NASA and wrote a paper on Sanskrit and AI | **TRUE** |
| The paper argues Sanskrit grammar parallels AI knowledge representation | **TRUE** |
| The paper says Sanskrit is the best language for programming | **FALSE - it says no such thing** |
| NASA endorsed Sanskrit for software | **FALSE - no endorsement exists** |
| A 1987 *Forbes* report said this | **FALSE - no such report exists in any year** |

**It is worth being precise about how the myth works**, because the mechanism recurs:

- **The paper is real, so the citation looks verifiable.**
- **The paper's actual subject (natural language *input*) is quietly swapped for a different one (programming
  language *choice*).**
- **A second-hand attribution (a magazine report) is added, and it is never checked.**
- **Repetition does the rest.**

**And the practical objection settles it:** if Sanskrit were the most suitable language for software, **software
would have been written in it by now.** None has been, in forty years.

## 4. What IS genuinely useful to this project

**Three things, and none of them is "Sanskrit is faster" or "Sanskrit is better for computers."**

### 4.1 Pāṇini's grammar as a rule system

The *Aṣṭādhyāyī* is roughly **3,976 rules** describing Sanskrit's morphology and syntax. It is a rule-based,
composable, generative system - **which is a real and defensible observation about its structure**, and it is
echoed by modern descriptions of it as functioning algorithmically.

**Where this bears on Sutram:** the keyword vocabulary. **Sutram's 303 functions are renamed with Sanskrit roots
chosen to be regular, composable and easy to type** - `ganita_janchit_yuj` is "math-checked-add". **A vocabulary
built from roots that compose predictably is easier to learn than one built from arbitrary English words, and that
is an argument from structure, not from mysticism.**

### 4.2 The kāraka model - six roles

Later grammarians analysed a sentence as **an Agent and a set of other participants: Recipient, Goal, Instrument,
Location, Source.** The meaning of a sentence is then representable in those roles **independently of the actual
words used.**

**This is the part of the tradition with real engineering content**, and it is the part Briggs' paper is actually
about.

**Where this could bear on Sutram:** if the project ever builds natural-language *input* - reading a problem
statement in Hindi or Gujarati and generating Sutram - **the kāraka model is a serious starting point.** It is
**not** relevant to the language's syntax, its compiler, or its performance.

### 4.3 A citation we can use honestly

**This is defensible:**

> *"A 1985 paper by a NASA Ames researcher argued that the ancient Indian grammarians' analysis of a sentence is
> structurally equivalent to the semantic networks used in AI knowledge representation (Briggs, AI Magazine,
> Spring 1985)."*

**This is not:**

> *"NASA said Sanskrit is the best language for computers."*

## 5. Why Sutram uses Sanskrit - the honest reason

**It is not because of this paper, and it does not need to be.**

**Sutram uses Sanskrit keywords for one reason: accessibility.** The aim, set by the project owner, is that
**someone in India who does not read English can learn to program in it.** That is why the keywords, and the
compiler's error messages, are in Indian languages rather than English.

**That argument is stronger than a computational one, because it is testable.** You can measure whether a
non-English speaker learns `yadi`/`anya`/`yavat` faster than `if`/`else`/`while`. **You cannot measure "Sanskrit is
more scientific."**

**So the project's justification stands on its own, and it does not borrow authority from a paper that does not
say what people claim it says.**

## 6. The rule this document is an instance of

**This project's standard is: performance is measured, not assumed.** **The same standard applies to claims about
the language's heritage.**

**A claim that is repeated often enough stops being checked.** This document exists so that the next person - or
the next AI - who hears "NASA said Sanskrit is the best language for computers" can find, in this repository, what
the source says, what it does not say, and what is actually useful in it.

**Declining a false claim costs nothing. Repeating one costs the credibility of every true claim beside it.**

---

## Sources

- Briggs, Rick. "Knowledge Representation in Sanskrit and Artificial Intelligence." *AI Magazine*, Spring 1985.
- D'Souza, Dilip. "How Sanskrit came to be considered the most suitable language for computer software." *Scroll.in*, 25 August 2015.
- "Speakeasy: Mind your language." *The Indian Express*, 29 April 2018.
- "'Most scientific language': Delhi CM Rekha Gupta claims Sanskrit is 'NASA-approved' for coding - Is that true?" *WION*, 5 May 2025.
- "Did NASA Accept That Sanskrit Is The Best Suited Language For Computer Programming?" *Eurasian Times*, 30 October 2020.
- Ramachandran, Sanjana. *Fifty Two*, on the origin of the myth; discussed in *Mint*, 15 September 2022.
