# Sutram — ROUND-95: your sentence was right. Send it as written.

**Base:** main at v283 · **Deliver into:** `Muse-to-Sarvam/`

## Verified behaviour - run by me on v283, counting lines not truncating

**`chakra i = 0 tak 3.0` -> REFUSED, `E_CHAKRA_DASHAM`: chakra purnankaih eva ganan...**
**`chakra i = 0 tak 0.5` -> REFUSED.** **`chakra i = 0.0 tak 3` -> REFUSED** (it was right by luck before).
**`chakra i = 0 tak 3` -> 4 lines**, counted with `wc -l`. Still correct.
**v282 had `tak 3.0` print 5,375,137 lines before kill - the bound's bit pattern read as an integer, about 4.6e18.**
**Suite 270, proofs 229/229 and 86/86, 680 programs 0 DIFFER.**

## You were right about the loop and I overrode you twice

**You wrote: *"a loop whose end number is a decimal never stops."*** **That is accurate.**

**I told you to change it, because my own test truncated the output at eight lines and I read that as eight iterations.** **Claude counted 5,375,137 lines and proved you right.**

**So: your sentence stands as written.** **If you have already changed it, change it back.**

## WS1 - and the final census
**v283 refuses decimal loop bounds, decimal `%`, and computed float-to-integer conversion.** **Three classes closed in three versions.**

**Recount, using your method - script, then read every candidate by hand, then run the decisive cases:**

1. **How many programs in the tree can now produce a wrong answer by any arithmetic path?**
2. **How many can fail to terminate?**
3. **And of the 267 examples, how many would a student misread on the first attempt?**

**Three numbers. If all three are zero, that is the release statement and I will use it.**

## WS2 - and the link audit, which nobody has re-run since the move
**`docs/` moved into four folders at R88. Have any links broken since?** **Every `.md` at the root, every file in `docs/`, and the HTML reports.**

**A count of broken links, and the files.**
