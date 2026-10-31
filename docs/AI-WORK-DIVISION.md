# How work is divided between the AI partners

**Owner's standing instruction, 31 October 2026.** **This file exists so the rule survives a context reset.**

---

## The rule

**ChatGPT gets BIGGER tasks than the other partners.**

**Not more tasks — bigger ones.** **A bigger task means:**
- **more workstreams in one round** (ChatGPT has carried 5–6 where the others carry 2–3)
- **harder questions**, not more of them — design decisions, adversarial audits, "find the flaw in this"
- **and the tasks that need the deepest reading of source**, because that is what it has been best at

**Claude gets the BUILD.** **It is the only partner that can commit, run the suite, run the gates and report a guard comparison — so it gets the implementation rounds, and those are bounded by what it can build and verify.**

**Muse gets the MEASUREMENT and the CENSUS.** **Counting, auditing, testing a claim against the tree, checking goldens against published values.**

---

## Why this division, in the owner's words and in evidence

**The owner's instruction:** *"give next time chatgpt bigger tasks than other ai okay, keep that in mind"*

**And the evidence from this project that supports it:**

**ChatGPT has produced, unprompted, the three findings that changed the design:**
- **the `kosa`/`kosh` collision** — it caught a word the agent had proposed
- **`pad_vam` writes one cell past its stated width** — a library bug nobody else saw
- **the safe/unsafe boundary** — *"ordinary unchecked raw memory can invalidate the assumptions of the checked part"*, which is now the top release risk

**It also named the single biggest unnamed risk better than the agent could:** *"silent partial compilation… the student does not suspect the compiler — they assume they are too dumb to understand loops."*

**That is the kind of output a bigger brief produces.** **Small briefs get small answers.**

---

## What a big ChatGPT brief looks like

**A good example is R148/R149/R152:**
- **four candidate designs evaluated, each with cost and what it breaks**
- **a named design with an explicit rejection of the alternatives and the reason**
- **the question the whole feature rests on, answered in one line**
- **and the honest fallback: "if nothing closes the hole at acceptable cost, say so"**

**And a bad brief is a single narrow question.** **It gets a correct answer and wastes the partner.**

---

## What this does NOT mean

**It does not mean ChatGPT gets tasks outside its role.** **It cannot commit, run the suite, or verify a guard — so it cannot do Claude's round, and a bigger brief does not change that.**

**It does not mean the other two get less.** **Claude's build rounds are the largest single units of work in this project.** **The instruction is about the SIZE of the thinking asked for, not the volume of the output.**

**And it does not override the rule that matters most:** **every brief opens with a `## Verified behaviour` block carrying exact tested outputs, because a partner reasoning from a stale description produces work aimed at a hole that may already be closed.** **That happened once, with Gemini, and it wasted its best thinking.**

---

## The practical form

**When issuing a round, check:**
1. **Does ChatGPT's brief have more workstreams than the others'?** **It should.**
2. **Does it contain at least one question that has no obvious answer?** **It should.**
3. **Does it name what would make the answer "no"?** **It should — otherwise the partner has no permission to disagree.**
4. **And does every brief open with verified behaviour?** **Always.**
