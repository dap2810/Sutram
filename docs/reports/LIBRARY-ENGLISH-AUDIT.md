# The English in the library: what it actually is

**Question:** five English words appear in `lib/` - `char`, `int`, `div`, `len`, `slice` - and the language has Sanskrit
for all of them. **So should they be renamed?**

**Measured answer: mostly no, and the reason matters.**

## 1. The builtins are ALREADY Sanskrit

**From the compiler's own builtin table:**

| Internal name | The name a user types |
|---|---|
| `bn_charat` | **`akshar`** |
| `bn_setchar` | **`akshar_rakh`** |
| `bn_charcd` | **`aksharank`** |
| `bn_vartlen` | **`vartani_aayam`** |
| `bn_vartcmp` | **`vartani_tul`** |

**So `char`, `char_at`, `char_code` and `set_char` are INTERNAL assembler labels for builtins whose public names are
already Sanskrit.** **Renaming them would change nothing a user sees.** **The internal label is a comment, not an API.**

## 2. Most of the `len` uses are LOCAL VARIABLES

**The 30 occurrences are:**

`len`, `len0`, `len1`, `lens`, `flen`, `hlen`, `keylen`, `keylens`, `nlen`, `plen`, `rlen`, `seglen`, `sflen`, `slen`,
`splen`

**These are local variable names inside library function bodies.** **A user never types them.** **`slen` means "source
length" and `plen` means "pattern length" - renaming them to `saayam` and `paayam` would make the code harder to read,
not more Sanskrit**, because the meaning is in the prefix, not the word.

**And the public length function is already `vartani_aayam`.** **The library's own API is Sanskrit.**

## 3. What IS a real problem - three public function names

| Name | What it is | Should be |
|---|---|---|
| **`sat_div`** | saturating divide - **a public library function** | **`sat_bhaj`** |
| **`brihat_ank_se_int`** | **a public function with `int` in it** | needs a Sanskrit word |
| **`brihat_ank_tak_int`** | same | same |

**These three are what a user actually calls.** **So the honest list is three names, not 55.**

## 4. And `slice`

**Not a keyword - the keyword is `vibhag`.** **It appears in compiler labels (`r23_msg_slice_base`) and in our prose.**
**The labels are fine; my prose should say `vibhag`.**

## The correction to the round

**I told the partners to rename `char`->`akshar`, `int`->`anka`, `div`->`bhaj`, `len`->`aayam` across `lib/`.**

**That was wrong in scale and partly wrong in kind:**

- **`char` and `int` are internal labels for builtins that are already Sanskrit** - **no change**
- **the `len` occurrences are local variables** - **no change, and renaming them would hurt readability**
- **three public function names genuinely need it** - **`sat_div`, `brihat_ank_se_int`, `brihat_ank_tak_int`**

**So the job is three renames, not fifty-five.** **And the caution I built into the round - "report what each name
actually does before you rename it" - is what produced this answer.**

## The lesson

**"English in the library" and "English a user sees" are different sets.** **A grep counts both; only the second one
matters.** **I counted the first and called it a vocabulary problem.**

---

*Measured by Sarvam, 27 October 2026, on main at compiler v253, by reading the compiler's builtin table and the `lib/`
sources.*

---

## Corrected again: TWO names, and they are a design question rather than a translation

**I read the three names I proposed to rename. The result is smaller and less obvious than I said.**

### `sat_div` does not appear where I said it did
**A tree-wide search finds `sat_div` only inside old evidence JSON files, never in `lib/`.** **My earlier list came from
a loose regex over `lib/*.smlib` and I did not confirm the hit.** **So: not a name to rename - a name I mis-reported.**

### The two `brihat` functions are real, and they are not simple renames
```
# brihat_ank_se_int(val, arr, n) - convert int to digit array (LSB first)
# brihat_ank_tak_int(arr, n) - convert digit array back to int
```

**So `int` in these two names means the NATIVE MACHINE INTEGER**, and the project's keyword for that type is `anka`.
**But `ank` is already in the name, meaning "digit".** **So `brihat_ank_se_anka` would use the same word in two senses in
one identifier** - which is worse than the English it replaces.

**That is not a missing translation. It is a naming question:** the pair is *big number* against *machine integer*, and
the project has no single word for the second that is distinct from `ank`.

**My proposal, and it needs the owner:**
| Now | Becomes | Why |
|---|---|---|
| `brihat_ank_se_int` | **`brihat_ank_se_laghu`** | *from a big number, a small one* - `laghu` is the natural opposite of `brihat` |
| `brihat_ank_tak_int` | **`brihat_ank_tak_laghu`** | *a big number, until a small one* |

**`laghu` (light, small) is the conventional opposite of `brihat` (great).** **It avoids reusing `ank`, and the pair reads
as a pair - which the English does not, because `int` says nothing about being the smaller of two representations.**

### And a caution about my own evidence
**This check ran against a tarball that has already served me a stale file once this session.** **So the absence of
`sat_div` from `lib/` should be confirmed against the API before anyone acts on it.** **A finding of absence is the
kind that a stale tree produces for free.**

---

## Resolved: `sat_div` is a stale comment, and the answer took three passes

**I said it did not exist. Then the API search said it did, in `ganita.smlib`. Then I read the context.**

**It appears once, inside a comment:**

> *"b == 0 returns 0 (same sentinel as sat_div)"*

**There is no function called `sat_div` in `lib/`.** **The comment refers to one as though it exists.**

**So the three passes were:**
1. **a loose regex put `sat_div` in a list of identifiers** - it was a comment hit I did not check
2. **a tarball search found nothing, and I concluded "does not exist"** - which happened to be right for the function, for the wrong reason, on a tree that has already served me a stale file once
3. **an API search found it in `ganita.smlib`** - correctly, because the comment is there

**Only reading the context gave the actual answer.**

### So it is a documentation defect, not a rename
**A comment naming a function that does not exist is the same class as the 35 descriptions ChatGPT corrected: text that
describes something other than the code.** **A reader would look for `sat_div` and not find it.**

**And what it probably means:** the comment is describing the saturating-divide behaviour, **whose real name is
`ganita_paripurna_bhaj`** - the `paripurna` family that the saturating operations use. **So the fix is to name the real
function, not to rename a missing one.**

## The final tally

| Item | Verdict |
|---|---|
| `char`, `int`, `len` in `lib/` | **internal labels and local variables - not API, no change** |
| `slice` in prose | **should say `vibhag`; compiler labels are fine** |
| **`sat_div`** | **a stale comment naming a function that does not exist** - fix the comment |
| **`brihat_ank_se_int`** | **real, public, needs `laghu`** |
| **`brihat_ank_tak_int`** | **real, public, needs `laghu`** |

**Two renames and one comment fix.** **That is the whole vocabulary task, after four measurements that each shrank it.**
