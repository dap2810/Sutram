# How work is divided between the AI partners

**Owner's standing instruction, 31 October 2026, restated:** *"give heavy tasks chatgpt and bit lower to claude and muse to regular tasks as u did before okay"*

**This file exists so the rule survives a context reset.**

---

## The division, in one table

| Partner | Weight | What it gets |
|---|---|---|
| **ChatGPT** | **HEAVY** | 4–6 workstreams. Design decisions. Adversarial audits. "Find the flaw in this." The questions with no obvious answer. |
| **Claude** | **regular** | 2–3 workstreams. The build: implement, run the suite, run the gates, report the guard comparison. Bounded by what it can build and verify. |
| **Muse** | **regular** | 2–3 workstreams. Measurement, census, counting, checking a claim against the tree. |

---

## Why ChatGPT carries the heavy rounds, in evidence

**It has produced, unprompted, the findings that changed the design:**
- **the `kosa`/`kosh` collision** — it caught a word the agent had proposed
- **`pad_vam` writes one cell past its stated width** — a library bug nobody else saw
- **the safe/unsafe boundary** — *"unchecked raw memory can invalidate the assumptions of the checked part"*
- **the `vitti a = k` refusal was never true** — it tested a claim the agent had asserted for several rounds
- **the obstacle-allocation witness** that proved `kosh` aliases diverge — after the agent had wrongly withdrawn the round

**And it named the biggest unnamed risk better than the agent could:** *"the student does not suspect the compiler — they assume they are too dumb to understand loops."*

**Small briefs get small answers.** **That is the whole argument.**

---

## What a HEAVY brief looks like

**A good example is R153/R155:**
- **four candidate designs, each with cost and what it breaks**
- **a named choice with the alternatives rejected and the reason**
- **the question the whole feature rests on, answered in one line**
- **and the honest exit: "if nothing closes this at acceptable cost, say so"**

**A bad brief is one narrow question.** **It gets a correct answer and wastes the partner.**

---

## What this does NOT mean

**ChatGPT does not get tasks outside its role.** **It cannot commit, run the suite, or verify a guard — so it cannot do Claude's round, and a heavier brief does not change that.**

**Claude and Muse are not getting less.** **Claude's build rounds are the largest single units of work in this project.** **The instruction is about the size of the THINKING asked for, not the volume of the output.**

---

## The rule that overrides everything else

**Every brief opens with a `## Verified behaviour` block.** **And every line in it states the CASE it was tested in, not just the result.**

**Why:** **the agent withdrew a correct round because its test said "they agree" — when the test had no obstacle allocation, so in-place extension succeeded and nothing moved.** **"They agree" was true and proved nothing.**

**"Diverges when an obstacle blocks in-place extension" is a claim that can be checked. "They agree" is not.**

---

## The practical checklist before issuing a round

1. **Does ChatGPT's brief have more workstreams than the other two?** It should.
2. **Does it contain at least one question with no obvious answer?** It should.
3. **Does it name what would make the answer "no"?** It should — otherwise the partner has no permission to disagree.
4. **Does every line of `## Verified behaviour` state its test case?** Always.
5. **Was every line run in the turn it was written, with the output pasted?** Always.
