# R12-01 — WS1: the native-speaker review sheets

**The wording of all eleven message sets is UNVERIFIED.** I wrote every message in ROUND-11. The checks
prove the form (identifiers, punctuation, script, no Latin prose), not the wording. No native speaker has
read any of them, Sanskrit and Hindi included.

## What is delivered

**One sheet per pack** in `review-r12/`: `sanskrit.md`, `hindi.md`, `marathi.md`, `gujarati.md`,
`bengali.md`, `punjabi.md`, `odia.md`, `tamil.md`, `telugu.md`, `kannada.md`, `malayalam.md`.

**Each sheet has all 128 messages of that pack:** the 105 compiler messages and the IDE's 23. For each
message:

- **where it appears:** the compiler, the compiled program at run time, the IDE's status line, or its
  output pane
- **its meaning:** a gloss in English, for the reviewer only. It is never shown to a user.
- **the romanised default** and **this pack's text, as printed:** the whole line, with sample names and
  numbers filled in
  - **Why the whole line:** many messages are pieces of one sentence that the compiler joins in a
    fixed order. A piece alone cannot be judged.
- **the pack-file form,** when it uses `{kw:…}` (the pack's own keyword)
- **my doubt,** if I have one
- **an empty "Correction" line** for the reviewer

**A reviewer returns the sheet edited,** or a list of `number: correction`. The corrections go into
`lang/<pack>.sandesh`. Then: `tools/sandesh.py --write`, `tests/sandesh/test_sandesh.py --record`, and a
read of the diff.

**The sheets are generated from the pack files,** so they show exactly what ships:

- the generator is `evidence-r12/make_review.py`
- the glosses are in `gloss.py`, the doubts in `flags.py`
- **after corrections, rerun it to refresh the sheets**

## Where I am unsure

**Three levels:**

- **LIKELY WRONG:** I think it is wrong, or it must be decided. Correct these first.
- **UNSURE:** a specific doubt, written under the message.
- **DRAFT:** no specific doubt, but still unverified. **DRAFT is not "correct".**

| Pack | Messages | LIKELY WRONG | UNSURE | DRAFT |
|---|---|---|---|---|
| sanskrit | 128 | **1** | 22 | 105 |
| hindi | 128 | 0 | 14 | 114 |
| marathi | 128 | 0 | 15 | 113 |
| gujarati | 128 | 0 | 14 | 114 |
| bengali | 128 | 0 | 16 | 112 |
| punjabi | 128 | **1** (to decide) | 13 | 114 |
| odia | 128 | 0 | 15 | 113 |
| tamil | 128 | 0 | 16 | 112 |
| telugu | 128 | 0 | 15 | 113 |
| kannada | 128 | **1** | 14 | 113 |
| malayalam | 128 | 0 | 15 | 113 |
| **total** | **1,408** | **3** | **169** | **1,236** |

**The three to correct first:**

1. **Sanskrit `msg_namespace_error`.** `अशुद्धः` (masculine) stands before the pack's word for `yoj`,
   `आयोजन`, which is neuter. The adjective should probably be `अशुद्धम्`, or the phrase recast.
2. **Kannada `r7_msg_mod_missing2`.** I used `ಕೋಶ` for "folder". But `ಕೋಶ` is also the pack's keyword
   for `kosh`, so the hint is ambiguous. It needs another word.
3. **Punjabi `msg_shell_bye`.** `ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ` is a Sikh greeting. A neutral `ਨਮਸਤੇ` may suit every
   user better. This is a choice for the owner, not a grammar question.

## Doubts that run through every pack

- **The arity message:**
  - **The number:** it reads `'f' … 1 <arguments> …; … 2`. The noun is plural, but the count printed
    before it is often 1, and a fixed fragment cannot change with the number.
  - **The word for "argument":** in most packs it is a calque, often of the debating or legal sense (युक्तिवाद,
    દલીલ, যুক্তি), and "signature" is a literal calque everywhere.
- **Case suffixes after a quoted name.** In Tamil, Telugu, Kannada and Malayalam, and in Marathi,
  Gujarati, Bengali and Odia, the suffix is printed after a space: `'f' க்கு`, not `'f'க்கு`.
  - **The cause is a check, not the translation:** the R11 check keeps the default's leading `' `.
  - **Fixing it needs that check relaxed for these few messages.** The sheets mark each one.
- **Coined terms** a speaker should confirm:
  - "pack" (भाषा पैक / भाषा-पुटः …)
  - "overflow" (अतिप्रवाह, in all seven trap messages)
  - "syntax tree"
  - "forward declaration"
  - "pipe"
- **The packs' own keywords appear in the messages.** Two of those keywords are questionable in
  `lang/*.lang` itself, not in my files:
  - **Tamil's word for `mala`, `வரிசைப்பட`,** looks like a truncated verb form.
  - **Punjabi's word for `vitti` is `ਵੇਰੀਏਬਲ`,** an English loan in Gurmukhi.
  - A reviewer of those packs should look at the `.lang` file too.

## What I did not do

- **I changed no translation this round.** Where I doubted my own text, I marked it instead of guessing,
  as the brief asked.
- **The three LIKELY WRONG items are the only places I would change today.** Even there a speaker
  should choose the replacement.

**No code changed this round,** so there is no branch and no PR. This delivery is documentation on main.

**Not verified:** the wording, by anyone who speaks these languages.
