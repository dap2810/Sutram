# Sutram — ROUND-229: every character the lexer silently swallows. A defect that exists now.

**Base:** main at v315 · **Deliver into:** `ChatGPT-to-Sarvam/`

**Your ROUND-228 said something I have not been able to stop thinking about:**

> *"In `lex .try_operator`, tilde has no branch and reaches 'Unknown char — skip.' ... A standalone tilde before otherwise valid old statements can therefore disappear during lexing."*

**That is a defect that exists in v315 today, and it has nothing to do with the `~` feature.**

**This round is about that defect, not about the feature.**

---

## 1. What I measured

**I wrote the `~` program and compiled it on v315:**

```
mukhya() {
    vitti total = 0
    chakra i = 1 tak 5 {
        ~ {
            kosh temp[1]
            kosh_kship(temp, i)
            total = total + temp[0]
        }
    }
    likha("total=", total)
}
```

**Result:**

```
Sutram truti: vyakaran dosh, pankti 6:13, shabd 'kosh_kship'
```

**Line 6 is `kosh_kship`. The `~` is on line 4.** **The error names a word three lines after the character that caused it, and the character itself is never mentioned.**

**A student would rewrite `kosh_kship`. They would never find the tilde.**

---

## 2. And the question that matters more than the feature

**If `~` is silently skipped, what else is?**

**Name every character that reaches "Unknown char — skip" in `lex`.**

**For each:**
1. **The character.**
2. **Whether it is printable and typeable on a normal keyboard.**
3. **Whether it appears in any language's normal punctuation — a quote mark, a dash, a non-breaking space, a smart quote, a Devanagari sign.**
4. **What a program containing it does today: compile silently, compile with a wrong parse, or fail somewhere confusing.**

**The ones I would check first, because a student typing in an Indian language or pasting from a document would produce them:**

- **the curly quotes `' ' " "` — a word processor produces these, not `'` and `"`**
- **the en dash and em dash `– —` — a word processor produces these**
- **the non-breaking space**
- **the zero-width joiner and non-joiner**
- **`।` and `॥` — these are handled, but confirm**
- **Devanagari digits `०` to `९`**
- **the rupee sign `₹`**
- **`©`, `®`, `°`, `×`, `÷`**

**Every one of those is something a person writing about a Sanskrit language on an Indian keyboard could produce by accident.**

---

## 3. And what the compiler should do

**Two options, and I want your judgement:**

**A. Refuse at the character, with the line and column.** **"Unknown character '—' at line 4, column 9. Did you mean '-'?"**

**B. Keep skipping, on the grounds that a comment or a stray character should not break a build.**

**Option A is a behaviour change: a program that compiles today would fail.** **So the question is whether anything in the tree would break — check the 331 examples and the test suite for characters that currently reach the skip path.**

**If nothing would break, A is clearly right.** **A compiler that silently discards input is a compiler that lies about what it compiled.**

**And there is a third option worth naming: warn and continue.** **The project already has a warning mechanism — `Sutram suchana`, used for the renamed builtins.** **Does that fit here?**

---

## 4. And what it costs

**A refusal at the character is one comparison per character in the lexer's default branch.** **That is a cost on every character of every program.**

**Is that acceptable, or does the lexer need the check only in the paths where a character is not otherwise recognised — which is where it already is?**

**And: does refusing cost anything at runtime?** **No — it is compile time only.** **Say so, so the trade is stated honestly.**

---

## 5. What to return

1. **The list of every character that reaches the skip path**, with what each is and where a user would meet it.
2. **Whether any example or test in the tree would break under a refusal.** **Name them, or say none.**
3. **Refuse, warn, or keep skipping — a judgement with a reason.**
4. **The lexer cost, stated.**

**And if the answer to 2 is "several examples break", say what they contain — because that tells us the skip path is load-bearing, which would be a much more interesting finding than the feature.**
