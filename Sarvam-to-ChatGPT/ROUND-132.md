# Sutram — ROUND-132: the five memory words, checked before anything is named

**Base:** main at **v412**, compiler **v261** · **Deliver into:** `ChatGPT-to-Sarvam/`

**Read first:** `docs/decisions/MEMORY-DESIGN.md` — **the design, the measurements, and the words I am not sure of.**

## Why this comes first
**Memory is the next block of work.** **`nirmmita` emits `mmap` per allocation and there is no `munmap` anywhere.** **Before a single
keyword is added, the words have to be right — and I have been wrong four times this session on Sanskrit.**

## WS1 — the five words, one at a time
**For each: is it a real word, what does it mean, and does the sense fit the technical use?** **Say plainly if I am romanticising.**

| My proposal | What I claim | What I need |
|---|---|---|
| **`nyasa`** (न्यास) | **a deposit held in trust, which must be returned** | **Is the obligation sense really in the word, or am I reading it in?** |
| **`pratyarpana`** (प्रत्यर्पण) | **returning a deposit** | **Is this the right word for releasing memory?** |
| **`kosa`** (कोश) | **sheath — the pancakosa, nested layers shed whole, outside in** | **Is a `kosa` a legitimate word for a memory REGION, or only a metaphor?** |
| **`samskara`** (संस्कार) | **impressions left by past actions — the residue in reused memory** | **Is this honest or decorative?** |
| **`rna`** (ऋण) | **debt** | **Does "you owe three deposits" work, or is it a pun?** |

## WS2 — the question I most want answered
**Is there a SINGLE Sanskrit word for "the act of letting go of what you hold"?**

**Because that is what `free` is, and English does not have a clean word for it either — `free` means both "release" and "no cost".**
**If Sanskrit has one word for the release and another for the zero-cost, that is a real advantage over English and it should be used.**

## WS3 — and the word for the region
**`kosa` is my proposal.** **But a region is a technical thing: a block, a lifetime, a boundary.**
**Is there a better word — one that means "the container whose contents are released together"?** **`kalasha`? `patra`? `bhajana`?**
**Or is `kosa` the right one and I should stop looking?**

## WS4 — and the one I am most likely wrong about
**`samskara`.** **It is a beautiful word and that is exactly why I distrust it here.** **If it is wrong, say so and give me nothing —
a wrong word is worse than an English one, because it looks finished.**

## Return
`ROUND-132-MEMORY-WORDS.md` with the five verdicts, the "let go" answer, the region word, and the `samskara` verdict. **No code.**
