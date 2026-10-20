# Messages in the language of the pack (ROUND-11)

**The rule (the owner's):** the compiler's messages and the Windows IDE's status line are in the
language of the selected pack. Sanskrit is the default. There is no English: not as a default, not as
a fallback, not behind a switch. `Sutram Error` and the `[E_CODE]` tags stay as they are: they are
identifiers, not prose.

| How it is run | Messages |
|---|---|
| `sutram prog.sm out.bin` (no `--lang`) | the romanised Sanskrit default, as in the compiler source |
| `sutram --lang sanskrit …` | Sanskrit, in Devanagari |
| `sutram --lang hindi …` (and the nine others) | that language, in its own script |
| the IDE | the pack its next run passes: the chosen pack; Auto = the detected one; Core = the default |

The program's own run-time errors (an index past the end, `kosh_pop` on an empty kosh) are chosen
when the program is compiled, so they follow the same `--lang`.

## Where the text lives

- **`lang/<pack>.sandesh`**: one file per pack, eleven files. One line per message:
  `key<TAB>"text"`, the text a JSON string (`\n` is a newline). Above each line, as a comment, is the
  default it translates. `{kw:vitti}` stands for the pack's own word for a keyword (from
  `lang/<pack>.lang`), so a hint shows the word the reader types.
- The keys are the compiler's labels for its messages (`r4_msg_undef`, …), and `ide.<label>` for the
  IDE's.
- **`tools/sandesh.py --write`** turns the eleven files into `src/r11_sandesh.inc` (the compiler) and
  `windows/gui/r11_ide_sandesh.inc` (the IDE). Do not edit those two by hand.
- The compiler looks a message up by its address, in one place (`r11_tr`, called from `print_str_z`
  and from the three places that put a message into the program). No print site names a language, so
  a new message needs one new key and no code.

## The checks (`tools/sandesh.py --check`, also in `tests/sandesh/` and the gate list)

For every entry of every pack:

- the key is a message the compiler or the IDE has;
- `Sutram Error` and the `[E_CODE]` tags are present and unchanged;
- the punctuation the code relies on is kept at both ends: the leading newline or `: `, the opening
  quote the compiler closes after the name, the trailing newline, the brackets of the IDE messages;
- every Latin word is code that the default also has (a keyword, a builtin, a flag, a file name), so
  no English can enter through a translation;
- every other letter is in the pack's own script.

And: every pack has every key (a missing key fails), the two generated files are current, and none of
the English words removed from the defaults in R11 may come back.

**What the checks cannot do:** say whether a translation is good. The eleven sets were written by
Claude in ROUND-11 and **need a native speaker's review**, Sanskrit and Hindi included. A reviewer edits
the `.sandesh` file and runs `--write`, then `tests/sandesh/test_sandesh.py --record`, and reads the
diff of `tests/sandesh/expect/`.
