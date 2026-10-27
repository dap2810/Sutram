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
