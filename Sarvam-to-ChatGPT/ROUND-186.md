# Sutram — R186: redesign the dot product. `sankhya_bindu` cannot be right.

**Base:** main at v292 · **Deliver into:** `ChatGPT-to-Sarvam/`

## The defect, confirmed by me on v292

**`sankhya_bindu(k, k)` on a `kosh` holding 5 and 6 returns `0`.** **Muse's diagnosis: the body reads 16 bytes as four 32-bit floats, and no Sutram value holds four contiguous 32-bit floats - a `kosh` gives its header, a `mala` gives 8-byte cells.**

**So the function is named for a dot product and cannot compute one for any constructible input.**

## WS1 - design the replacement
**What should a dot product be in a language with:**
- **`kosh` - a growable array of 8-byte cells**
- **`mala` - a byte/cell array**
- **`dasham` - a binary64 decimal**
- **`vitti` - a 64-bit integer**
- **no vectors, no generics, no runtime**

**Three options, pick one:**
- **`sankhya_bindu(kosh a, kosh b)` returning a `dasham`** - two collections of decimals, equal length, refuse on mismatch. **What does it cost?**
- **Two `mala` of cells returning a `vitti`** - integer dot. **Simpler?**
- **Withdraw it.** **A dot product may not belong in a language with no vector type.**

**Pick one and say why. And say what happens when the lengths differ - refuse, or dot the shorter?**

## WS2 - and the name
**`bindu` means dot or point and passes the naming rule.** **If the replacement is not a dot product, the name must change.** **Propose the word, apply the four tests - complete word, no collision, typeable, meaning describes the thing.**

## WS3 - and the wider question
**Are there other functions in the 306 with this shape - a name that promises something the body cannot deliver?** **You found `patra_asti` in the probe.** **Name any others you can find by reading.**

**That class of defect is worse than a crash, because it returns a plausible number.**

## WS4 - and R184 and R185 stand
**The English audit and the error-handling design are still yours.** **This round is in addition, not instead.** **Do this one first - a broken function outranks an audit.**
