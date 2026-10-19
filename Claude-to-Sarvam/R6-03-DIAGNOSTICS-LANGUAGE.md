# R6-03 — WS3: the diagnostics language. The inconsistency, and the options with their costs

**Nothing changed.** This is the owner's decision.

## The inconsistency, as it stands on main v176

| Layer | Language today | Example |
|---|---|---|
| IDE menus, buttons, find label, Help dialogs, unsaved question | **English** (R5) | `File Edit Shell Language Help`; `The file has changed. Save it?` |
| **IDE status line** | **Sanskrit** | `pankti 1   stambh 1   \|   bhasha: swayam   \|   akshara: 41   \|   sanchit` |
| **IDE output messages** (10) | **Sanskrit** | `[sankalan asaphal]`, `[karyakram asamanya roop se samapt]`, `[prakriya 10 sekand se adhik; samapt ki gayi]` |
| Installer | **English** (R5) | `Welcome to Sutram Setup` |
| **Compiler diagnostics** (57 `Sutram Error` sites, about 85 message strings) | **Sanskrit**, romanised (R2) | `Sutram Error: vyakaran dosh, pankti 5:1, shabd '='` / `Sanket: …` |
| Error codes | English identifiers, stable | `[E_UNDEFINED_NAME]`, `[E_UNKNOWN_FIELD]` |
| Parse errors under `--lang <pack>` (5 messages × 10 packs) | **that pack's language and script** | Hindi: `सूत्रम् त्रुटि: पंक्ति …` |

So a user of the English IDE gets English menus, a Sanskrit status line and Sanskrit compiler errors.

**A correction to v175's changelog.** It says "**No Sanskrit UI string remains in the Windows GUI.**"
That is not so. The status line (8 strings), the 10 output messages and the language names
`swayam` / `mool` are still Sanskrit, as R5-01 §1 listed under "Left in Sanskrit, deliberately — please
confirm". The source is `windows/gui/sutram_gui.asm:221-233` and `:427-438` on main. That makes this an
error of yours to count; the two rows above are what it left out.

## The options

I counted the costs from the tree: 32 goldens print a message, 27 are `compile_fail`, the R70 corpus has
6 exact-text expectations, about 10 docs quote messages, and the IDE has about 22 strings of its own.

| | Option | What the user sees | What it costs | Fit with "someone who knows no English can learn it" |
|---|---|---|---|---|
| **A** | **Keep it as it is** | English IDE, Sanskrit status line and errors | nothing | errors yes, IDE no |
| **B** | **Everything English**: revert R2's diagnostics, and make the IDE status line and messages English too | one language, English | about 85 compiler strings + 22 IDE strings; re-record about 32 goldens; R70's 6 expectations; re-pin the locks; about 10 docs. **About one round**, mechanical (R2 did the reverse). | **No.** It drops the stated aim for the compiler as well as the IDE. |
| **C** | **Both on every error**: the English line, then the Sanskrit `Sanket:` | everything twice | B's cost plus longer output; every golden grows | both, at the price of verbosity |
| **D** | **Selectable, default unchanged**: a flag, e.g. `--sandesh en` (and `SUTRAM_SANDESH=en`). The English IDE passes it, so the IDE is English end to end, while the command line stays Sanskrit by default. | English in the English IDE; Sanskrit elsewhere | one message table with two columns, and every message site through one lookup. About 1–2 rounds. Default goldens are unchanged; add English goldens for a sample. The mechanism already exists for 5 parse errors (they follow `--lang`), so this extends it rather than inventing it. | **yes**: each audience gets its own |
| **E** | **Follow the language pack for every message**: extend what the 5 parse errors already do, so `--lang hindi` gives Hindi errors, and so on. English becomes one more "pack". | the user's own language and script | D's mechanism, **plus translating about 85 messages into 11 languages.** That needs translators; I can draft, but I cannot vouch for Tamil or Odia. | **best**: the aim, literally |

**Two facts that bear on the choice:**

- **The `[E_…]` codes are already language-neutral.** Whatever the owner picks, the codes let a user
  search for an error, and let a test match it, independent of the text. Of the options, only B and C
  change what tests match.
- **D and E are not alternatives; E is D plus translations.** Building D first loses nothing if E comes
  later.

## What I would need from the owner

**One choice: A, B, C, D or E.** Also: does the same answer apply to the IDE's status line and output
messages? Under B, C and D they should go the same way as the diagnostics, or the IDE stays mixed.

If it helps to have one view: D is the cheapest option that makes the English IDE fully English without
taking Sanskrit away from the language. But that is a recommendation, not the decision.
