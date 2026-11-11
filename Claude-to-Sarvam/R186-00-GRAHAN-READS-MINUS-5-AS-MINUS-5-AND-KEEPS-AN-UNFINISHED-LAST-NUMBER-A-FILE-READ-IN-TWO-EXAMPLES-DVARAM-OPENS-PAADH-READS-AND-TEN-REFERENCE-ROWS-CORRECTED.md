# R186-00 — `grahan()` read `-5` as 5 and lost a last number with no newline after it. **Both are fixed in v324, and the fix needed a third change you did not ask for:** a typed `-1` is now read as -1, which was `grahan()`'s only end-of-input sign. So `grahan()` now sets `nivesha_anta()` as well. **A file is read in two examples, and the reference's `dvaram` and `paadh` rows said each other's job.** Eight more rows of that table were wrong, measured one by one, and are corrected. **The guard against v323 is 7 DIFFER, not 0:** a fix to `grahan` changes the bytes of every program that calls it. The seven print what they printed on ordinary input.

## Release line

```
main  (the commit carrying this file; SHA in my chat report)   Sutram 1.0 (v315) - sampurna sutra, unchanged
staged r186-grahan-and-files cddc8551   Sutram 1.0 (v324) - sampurna sutra     (on r184-read-a-line f05ddd7e = v323)
     crash corpus: GATES-PENDING
     suite: NO-EXPECTATION=4 PASS=331 (335 run; examples 362 and 363, both with goldens)
     gates: GATES-PENDING
     installer (payload v324): 4caedefd6863a61010393867dd223168624ea2aa9211e81fa6a99651e015741a
     the guard, v324 against v323: 787 programs - 582 byte-identical, 196 refused identically, 7 DIFFER, 2 new
            (Linux executables, and the same line for Windows executables)
            the 7 are every program that compiles and calls grahan (evidence-r186/differ-list.txt)
staged v323 r184-read-a-line f05ddd7e · v322 602b1f10 · v321 c0fdebe8 · v320 fe90a9b1 · v319 4c1159be · ... - unchanged
```

Sanskrit only; no pack touched; `backups/` untouched. `R159 no personal paths`: 0. `vartani_grahan`'s
interface is untouched.

## 1. The two bugs, confirmed, then fixed (`evidence-r186/grahan-v323.txt`, `grahan-v324.txt`)

`g1.sm` is `vitti a = grahan() ; likha(a)`:

| input | v323 | v324 |
|---|---|---|
| `-5` | **5** | **-5** |
| `-1` | **1** | **-1** |
| `-42` and then the end, no newline | **-1** | **-42** |
| `42` and then the end, no newline | **-1** - the number lost | **42** |
| `+5` | 5 | 5 |
| `-9223372036854775808` (the smallest `vitti`) | 9223372036854775808 wrapped to the smallest | **exact** |
| nothing at all | -1 | -1 |

**What the fix is.** A `-` or `+` that comes **before the first digit** sets the sign, and if there are two,
the last one wins (`+-5` is -5). **After the first digit, both are passed over as before** - so `12-34` is
still 1234. I kept that because changing it means deciding what `12-34` should be, and the brief did not ask.
At end of input the digits already read are returned with their sign. -1 means the end only when nothing was
read.

**How.** The `grahan` code was hand-written `db` bytes with hand-counted jump lengths, two copies (Linux and
Windows) differing only in those counts. **It is now ordinary instructions in one NASM macro, used twice.**
The one jump that leaves the tail is computed from the labels and the size of the platform read. Two flags sit
in the stack space it already had: sign, and a digit seen. It still reads one byte per system call.

### And the third change: `grahan()` sets `nivesha_anta()`

**Fixing the minus sign broke the books' end-of-input test.** The book taught:

```
vitti a = grahan()
yadi (a == -1) { likha("Input ended\n") krama }
```

On v323 that was safe only because nobody could type -1: `-1` read as 1. **On v324 a student who types `-1`
ends that loop.** The only way to keep the end and the number apart is a second signal, and one already
exists: `nivesha_anta()`. **So from v324, `grahan()` sets it when it finds the end with nothing read.** The
books and the reference now teach `yadi (nivesha_anta())`. `g3.sm` sums `-1`, `5`, `-4`: v324 counts three
numbers and stops. **On v323 the same loop never ends - `grahan()` never set the flag** (`exit 124`, stopped
after 3 s).

**This changes what `nivesha_anta()` reports** (from "a `vartani_grahan()` found the end" to "a
`vartani_grahan()` or a `grahan()` found the end"). It does not change `vartani_grahan()`. **If you would
rather keep `nivesha_anta()` to `vartani_grahan()` alone, the book's `-1` test has to go anyway** - there is
no other way to tell the two apart. Say so and it comes out.

### The sibling: `vartani_grahan()` never had the defect

`printf 'one\nlast'` gives `[one]`, `[last]`, then the end (tested in R184, again here on v324). **It does not
share `grahan`'s read path** - it is separate code written in R184, and it returned the partial line from the
start.

### What `grahan()` does with the rest - each reported, not changed

| input | gives | |
|---|---|---|
| `5abc` | 5 | letters after the digits are passed over |
| `12 34` | 1234 | a space inside a number is passed over - **two numbers become one** |
| empty line | 0 | as `0` and as `abc` - the three cannot be told apart |
| `abc` | 0 | a line with no digit is 0, not an error |
| `9223372036854775808` (one past the largest) | -9223372036854775808 | **wraps, with no message** |
| `99999999999999999999` | 7766279631452241919 | wraps |

**You are right that this is the lexer's defect class:** a parser that turns what it cannot read into a
number, silently. **I did not fix it, because each one is a decision, not a repair.** Should `5abc` be refused
(and how - a running program cannot refuse; it can stop, or return a sign)? Should `12 34` be 12, then 34 on the
next call? Should an overflow stop the program as `E_ATIPRAVAH` does at compile time? **All six are now written
in reference section 4d, so a student can find them.** They are a round of their own.

## WS1 - the file example

### What reads a file

**`lib/patra.smlib`**, brought in with `yoj patra`. Its `patra_path_sarv(path, buf, cap)` opens the file, reads
up to `cap` bytes into `buf` (looping until the count is met or the file ends), closes it, and returns the byte
count, or -1. Underneath are four builtins: `dvaram` (open), `paadh` (read), `dvaram_likha` (write), `band` (close).

### What the reference said, and what is wrong

```
| `dvaram` | patra descriptor helper |
| `paadh`  | open a file |
```

**`paadh` does not open a file; `dvaram` does.** The library's own code shows it: `fd = dvaram(p, 0)` and
then `n = paadh(fd, dst + total, c - total)`. **A student who reads the table, calls `paadh("data.txt")` to open
a file, and gets something else is exactly the failure you describe.** Corrected, with each function's
arguments and what it returns.

### The two examples (both in the suite with goldens; fixture `examples/data/r186_sankhya.txt`)

The fixture holds three lines: `10 20` / `ankah 3` / `9`.

1. **`examples/362_r186_patra_sankhya_yoga.sm` - sums every number in a file by its path: `yogah: 42`.**
   `nirmmita`, `patra_path_sarv`, a `chakra` over the bytes with `akshar(buf, i)`. **Thirteen lines of body,
   not ten** - a file has no number reader, so the program builds each number from its digits. It also says so
   when the file is not there (`patra na labdham`, tested).
2. **`examples/363_r186_pankti_ganana_patra.sm` - counts the lines of a file: `panktayah: 3`.** **It reads the
   file as the program's input** (`./prog < file`), with `vartani_grahan()` and `nivesha_anta()`.

**And what that second one shows, which you should know before item 4:** **there is no line reader that takes
a path.** `vartani_grahan()` reads standard input only. To count the lines of a file *by its name*, a program
must read the whole file with `patra_path_sarv` and count the 10s itself. **"Reading a file is the same shape
as reading a line" is true for standard input, not for a named file.** I did not build a path-taking line
reader - WS4 says nothing else, and it would be a new interface.

### Reference and books

- **Reference: "Reading a file (v324, R186)"**, after section 4d. It names `patra_path_sarv`, both
  examples, the `< file` form, the missing path-taking line reader, and the four builtins.
- **Books: no chapter of either book teaches files.** The nearest is the input section where `grahan` and
  `vartani_grahan` are taught. **So I added "Reading a file" there, in both books, after `vartani_grahan`.** The
  English section carries the full summing program; the Sanskrit one describes it and names the example.
  **The `grahan` passage before it is rewritten in both: it reads a sign, and the end is `nivesha_anta()`.**
  **The Sanskrit text is mine and unread by anyone who would catch an error in it.**

## WS2 - the other rows: ten wrong, and the table needs a rewrite, not a paragraph

I ran a program for each row that looked wrong (`evidence-r186/reference-rows.txt`):

| row | it said | measured |
|---|---|---|
| `dvaram` | patra descriptor helper | **opens a file** |
| `paadh` | open a file | **reads** from a descriptor |
| `pad` | read memory | reads **one byte** (`123456789` read back as 21) |
| `likh8` | write 8-bit value | writes **8 bytes** |
| `pad8` | read 8-bit value | reads **8 bytes** |
| `likh8c` | print a character | **a bounds-checked 8-byte write**, `likh8c(addr, val, bound)` - `likh8c(65)` is refused |
| `pad8c` | read a character | **a bounds-checked read**, `pad8c(addr, bound)` - `pad8c()` is refused |
| `aksharank` | character code (note: index currently ignored) | **the index is used**: `aksharank("ABC", 2)` is 67 |
| `vartani_tul` | varna compare | **equal / not equal only**: `ab`/`ac` and `ac`/`ab` both give 1 |
| `vartani_aayam`, `vartani_pratilip` | varna length / varna copy | right job, wrong word - `varna` is a letter; these take strings |

**Every one of these is corrected in the table, with its arguments.** The rows I ran that are right:
`smaran`, `sthagita`, `pankti_gan`, `akshar`, `akshar_guru`/`akshar_laghu`, `vartani_aayam`'s count.

**My answer to your question: the built-in table needs rewriting, not the file section alone.** Of the 13
rows I ran, **8 were wrong about what the function does** (and two more used the wrong word). Most rows are a
few words with no arguments - "read memory", "fill memory", "copy memory" - which cannot be checked by reading
them. **I did not run the other ~40 rows.** That is the reference audit your plan gives ChatGPT; this is
evidence it is needed. **Every corrected row now gives the arguments, and so can be tested by a gate -
none of them is tested yet.**

## WS3 - the tests

**Gate `R186 grahan and files`** - `tests/r186/test_grahan_and_files.py`, **24 checks, 0 failed on v324; 10
of them fail on v323.** Each feeds exact bytes and compares exact bytes: the minus sign, the plus sign, a sign
after a letter, two signs, a sign after a digit, the smallest and largest `vitti`, an unfinished last number
(with and without a sign), the read after it, the typed `-1` loop, no input, empty lines, the six behaviours
left as they are (pinned, so a later change is seen), `vartani_grahan`'s unfinished line, both file examples,
and a missing file.

**The fixture is in the tree** (`examples/data/r186_sankhya.txt`), so the goldens are reproducible.

**The guard: 7 DIFFER against v323, not 0.** You expected 0 because you priced this round as "an example and
a paragraph". **The `grahan` fix is a change to code that seven programs contain**, so their bytes must
change. **The seven are every program that compiles and calls `grahan`** - the other six files that mention
it are refused, before and after. **Each was compiled with both compilers and run on seven inputs**
(`differ-run.txt`): **the same output on the five ordinary ones** (`5`, `7 3 2`, `20 4`, `12 30 1`, no input);
**different on `-5 3` and on `42` with no newline, which is the fix.** By the guard's own rule (R180: 0 for
the rest, a stated list for the changed), that is the stated list.

## WS4 - kept out

No memory work, no Windows run, no benchmark work. `vartani_grahan`'s interface is unchanged. **What I did
add that you did not list:** `grahan` setting `nivesha_anta`, and the eight measured rows of the table beyond
`dvaram`/`paadh`. Both are above, with the reason.

## Not done, and why

- **Windows: not run.** WINE-PENDING
- **`grahan`'s other six behaviours are reported, not changed** - each needs a decision.
- **No line reader that takes a path** - a new interface, not asked for.
- **The rest of the built-in table is not checked** - about 40 rows.
- **ROUND-187 (the Windows acceptance checklist) is next.**
