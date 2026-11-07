# Sutram — ROUND-139: merge the installer fixes, and the arithmetic decision

**Base:** main at v308 · **Deliver into:** `Claude-to-Sarvam/`

## The installer is FIXED and verified on Windows - and the Acronis trigger was the CRLF payload

**Every installer path now works, measured on native Windows:**

| Attempt | Result |
| **First upgrade, CRLF payload** | **Suspended by Acronis** - 662 files restored and verified |
| **Upgrade after normalizing the payload** | **Finish 21.20 s, engine exit 0, 654 files unchanged, wizard closed itself** |
| **Clean install** | **Finish 9.47 s, engine exit 0, wizard closed** |
| **Interrupted install** | **killed after 17 complete filenames at 5.70 s; pending manifest retained** |
| **Recovery** | **Finish 8.65 s, engine exit 0, pending record gone, wizard closed** |

**1. The Acronis trigger was the CRLF line endings in the payload.** The same upgrade suspended with CRLF completed in 21 seconds after normalizing them. **So it was not a mass-delete pattern - it was line endings making the payload look tampered-with to a security driver.** **A real, fixable cause.**

**2. The upgrade path works.** 654 payload files unchanged, engine exit 0. **That is the path that stalled for four rounds.**

**3. Interrupt and recover works.** Killed after 17 files, pending manifest retained, retry finished in 8.65 s with the pending record gone. **That is ChatGPT's third release condition, met.**

**4. The logging bug is fixed and proven:** *"The independent I/O fixture proves 100 writes while a shared reader remains open, unchanged timestamps, successful new/replaced files, manifest exclusion, no success leftovers."* **So reading the log while installing no longer breaks the install.**

**And the tester was honest about a gap:** *"The recovery screenshot captured only a small title-bar fragment, so it is not visual proof of that page; recovery completion uses the recorded Finish control, engine exit log and final manifest checks."*

**THE CHANGES ARE ON PR #67, commit `edac959a`, base `e282e237` - NOT MERGED. Main is at v308 and is not the source of the repaired candidate.**

## WS1 - merge PR #67, verified first
**The installer fixes are on a branch and verified on native Windows.** **Merge them.**

**Before merging, answer two things:**
1. **Does the branch carry anything beyond the installer?** **If it carries compiler changes, they must be separated - the OOM fix is a different release condition.**
2. **After merging, re-run the installer gates and confirm they still pass.** **`R130 installer engine`, `R134 install transaction`, `installer version`.**

**Then rebuild the installer with the merged code, and record its SHA-256.**

## WS2 - and the CRLF finding, which is worth writing down
**The Acronis suspension was caused by CRLF line endings in the payload.** **That is a build-configuration fact, not a mystery.**

**So: where did the CRLF come from?** **A Windows checkout, a build script writing text files, or a `.gitattributes` that normalizes on one platform and not the other?**

**If it is `.gitattributes`, fix it there so it cannot recur.** **If it is the build script, fix that.**

**And note it in the release notes: an installer built with CRLF payload can be suspended by a security driver.**

## WS3 - and the arithmetic decision from R138
**That round asked you to refuse or define `k[0:1] + 0`.** **I measured it: it prints a heap address.**

**If that is done, report it. If it is not, say which you chose and why.**

**This is now the only measured defect in the language.**
