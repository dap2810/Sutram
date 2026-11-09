# Sutram — ROUND-157: the books are missing the memory model. That comes first.

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

**I audited the tree. The finding is not about size.**

---

## The finding

**The English book is 4,975 words in 18 chapters. The Sanskrit book is 3,874.**

**Neither of them contains the memory model.**

| Term | English | Sanskrit |
|---|---|---|
| `kosh` | 18 mentions | 12 |
| **`mandapa`** | **0** | **0** |
| **`parimana`** | **0** | **0** |
| **descriptor** | **0** | **0** |
| **`vibhag` (slice)** | **0** | **0** |
| **`analysis-steps`** | **0** | **0** |

**And chapter 14 is still titled *"New Features: v22"* - 293 versions old.**

**So a student reads the English book, learns `mala` in chapter 8, meets `kosh` eighteen times with no chapter explaining it, and never learns that a block returns memory, that a slice can be refused, or that running out of memory produces a sentence.**

**That is the work of the last two weeks and it is not in the book.**

---

## WS1 - and this is the round
**Add a chapter to the English book and to the Sanskrit book. Same content, each in its own language.**

**It must cover, in this order, in plain language a beginner can follow:**

1. **What a `kosh` is, and why it exists alongside `mala`.** **A `mala` is a fixed row; a `kosh` grows.** **Give one example of each and say when to use which.**
2. **What `mandapa` does.** **A block, and everything made inside it is gone when you leave.** **The measured number: 200,000 allocations cost 52,760 KB without a block and 13,480 KB with one.**
3. **`parimana()` - how much memory am I using?** **With a worked example showing 0, then a value inside a block, then 0 after.**
4. **`mandapa parimita N` - a budget that refuses.** **And why that is better than being killed by the operating system.**
5. **A slice, and the one rule about it.** **`k[0:5]` is a view into a `kosh`. If the `kosh` grows, the slice is refused at compile time rather than reading the old memory.** **The rule in one sentence, and the error a student will see: `E_VIBHAG_ANKA`.**
6. **What happens when memory runs out.** **`Sutram truti: kosh vardhayitum smritih na labdha` - and that the `kosh` is unchanged, which is the thing a student most needs to know.**
7. **And one paragraph on what the language does not have.** **No garbage collector, no manual free, no reuse inside a live block, no threads.** **A student should know the shape of the thing.**

**The Sanskrit book gets the same chapter in Sanskrit.** **It already has 608 Devanagari characters, so the encoding works.**

**And retitle chapter 14.** **"New Features: v22" is 293 versions old. Either bring it current or fold it into the new chapter.**

## WS2 - and the test of whether it is any good
**After writing it, answer one question: could a person who has never programmed read this chapter and write a program that uses a block, a budget and a `kosh`?**

**If not, say what is missing.**

**And: does every code example in the new chapter compile on v315?** **Compile them. A book with an example that does not compile is worse than no example.**

## WS3 - and then the prune, which is second
**331 images totalling 26 MB. `Windows-to-Sarvam` is 67 MB and 60% of the repository.**

**Delete:**
- **any screenshot not cited by a `RESULTS.md` or a round record**
- **raw environment snapshots where the claim does not depend on the full file - replace with a SHA-256 and a one-line description**
- **the `win-v297-2026-11-03/Sutram-Setup-v297.exe` - a six-version-old artifact that cannot be verified against anything current**

**Keep: every round record, every cited screenshot, and every hash.**

**And report: total files and total size before and after.**

**The honest note from the last audit still holds: git does not shrink when files are deleted, so this is about a repository a person can search, not about storage.**

## WS4 - and the four paused language books
**`sutram-book-hindi.html`, `-tamil`, `-telugu`, `-gujarati` - 84 to 95 KB each.**

**We have been Sanskrit-only for weeks. They are now four books describing a language that has moved on without them.**

**Either archive them with a note saying which version they describe, or delete them and say so in the record.** **A stale book in a language we are not maintaining is worse than no book, because a Hindi reader would learn v300 and meet v315.**
