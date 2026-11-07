# Sutram — ROUND-143: the installer is fixed. Verify the claim and find the gap.

**Base:** main at v308, with the installer fixes on PR #67 · **Deliver into:** `Muse-to-Sarvam/`

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

## WS1 - and this is the question: is the recovery actually safe?
**The recovery works: killed after 17 files, retry finished in 8.65 s, pending record gone.**

**But: what happens if the interruption lands at a WORSE moment?** **Read the journal design and answer:**

- **killed between the journal write and the first file copy** - does the retry know what to do?
- **killed after the last file but before the journal is deleted** - does it re-copy everything, or recognise completion?
- **killed while the journal itself is being written** - is the journal atomic, or can it be half-written?
- **a user edits a file in the target between the interruption and the retry** - is that file protected or overwritten?

**That last one is the safeguard question. ChatGPT said the journal must not prove every file belongs to the installer. Test whether it does.**

## WS2 - and the CRLF finding
**The Acronis trigger was CRLF line endings in the payload.** **Normalizing them made the same upgrade complete in 21 seconds.**

**So: which files in the payload are text, and which are binary?** **If a `.gitattributes` normalizes some, a Windows checkout changes them and the payload hashes differ from the Linux build.**

**Check: does the payload manifest's recorded hash for a text file match what a Windows checkout produces?** **If not, the installer is comparing hashes across two different line-ending conventions and that is a latent defect even without Acronis.**

## WS3 - and the arithmetic decision
**`k[0:1] + 0` prints a heap address.** **Claude is asked to refuse or define it.**

**Your view: which is right for a beginner?** **And if it should be refused, what should the message say?**
