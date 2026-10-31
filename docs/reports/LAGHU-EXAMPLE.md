# `laghu` — a worked example

**Two functions, one pair of words:**

| Function | Sanskrit | Direction |
|---|---|---|
| `brihat_ank_se_laghu(val, arr, n)` | *a small one, from a big number* | **machine integer → digit array** |
| `brihat_ank_tak_laghu(arr, n)` | *a big number, until a small one* | **digit array → machine integer** |

**`brihat` = great, `laghu` = light/small — the conventional pair.** **`ank` = digit.** **So the name says what moves and
in which direction.**

## The program

```sutram
yoj brihat

mukhya()
    vitti digits[8]
    brihat_ank_se_laghu(1234, digits, 4)

    likha("digits: ")
    likha(digits[0])
    likha(digits[1])
    likha(digits[2])
    likha(digits[3])
    likha("\n")

    likha("back: ")
    likha(brihat_ank_tak_laghu(digits, 4))
    likha("\n")
    nivartanam 0
```

## What it prints

```
digits: 4
3
2
1

back: 1234
```

**Note the order: `4 3 2 1`, not `1 2 3 4`.** **The array is filled LSB first** - the least significant digit in
`digits[0]` - **which is what the library's own comment says.** **And `brihat_ank_tak_laghu` reads it back in the same
order, which is why it returns `1234` and not `4321`.**

## Why the words are right, seen in use

- **`brihat_ank` is the big-number form** - an array of digits, one per cell, no size limit.
- **`laghu` is the machine integer** - 64 bits, and it can overflow.
- **So the pair names a real distinction**: **the big form has no ceiling, the small form does.** **The library's comment
  says it plainly: *"Only correct if the value fits in an int."***

**And `se` (from) and `tak` (until) give the direction, which the English `int` never did.** **`brihat_ank_se_int` read
as "big digits, from, int" - three nouns and a preposition. `brihat_ank_se_laghu` reads as a movement.**

## Verified

**Compiled with `Sutram 1.0 (v253)`, run, output captured with `od -c`.** **Exit 0.**
**The `yoj` line is required: without it the compiler says `Sutram Error: agyat prakriya: brihat_ank_se_laghu` - "unknown
function".**

---

*Run by Sarvam, 27 October 2026, on main at compiler v253.*
