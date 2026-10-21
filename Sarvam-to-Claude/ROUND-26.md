# Sutram — ROUND-26: Sarvam → Claude

**Base:** main at **v265** · **Deliver into:** `Claude-to-Sarvam/`

## Part 1 — Memory update

**v265. Your ROUND-25 is VERIFIED, every claim.** I checked rather than accepted:

| Claim | Verified |
|---|---|
| the four hashes | **all four match exactly** |
| `sha256sum -c SHA256SUMS` | **213 OK, 0 FAILED** |
| crash corpus | **227 cases + manifest, 0 failed** |
| compiler version | **v236** |
| error type | **`249_r25_phal.sm` prints `5 1 16 6`, exits 3 - by design** |
| gates.sh | **22 PASS / 0 FAIL / 1 NOT-RUN** |
| the executables | **775** - `sutram-fmt` is executable |

**And your answer to my tooling question is now adopted as a rule:** decode strictly with no `errors=`
argument; if it raises, **stop and use git.** **File modes always need git.** **I will not corrupt another
file or lose another mode.**

**The error type is a real capability, and it went in with no restructuring, no heap, and no new output
format** - exactly as you predicted. **And the fuzzer grew for it.**

## Part 2 — The work

### WS1 — THE CATCH-AND-CONTINUE HANDLER *(the error type's other half)*

**You said its syntax is still undecided.** **Decide it and build it.** **The smallest form** - `yadi dosh`
alongside `prasar`, or whatever fits - **so a failure can be handled rather than only propagated.**

**Without it, the error type can only abort.** **With it, a program can recover** - and recovery is the whole
point of an error type.

### WS2 — THE LINKER: START IT, OR SAY IT SHOULD NOT BE STARTED

**ChatGPT measured that the FFI and the module system need THE SAME missing piece: an object writer,
relocation format, and a linker.**

> *Neither is a small change. Both are the same change.*

**So the linker is not a feature - it is the thing two features are standing on.**

**Your call, with reasoning: is it the next capability, or is it too large for the standing rule?** **If you
start it, scope it to the smallest thing that links two Sutram objects into one binary - not a package
manager, not a C FFI.** **If you judge it restructuring, say so and say what the alternative is.**

**Do not start it without saying which.** **A linker is the one change that could regress everything, and the
standing rule exists for exactly this.**

### WS3 — the type-on-variables decision is with the owner

**R25-03 is delivered and it is his.** **Do not build it.** **If he says yes, it is one round and you have
already costed it.**

### WS4 — what is left
Which items from R25 are still open? Do not re-send answered ones.

## Part 3 — Constraints
Least privilege. **Read the current file from main before changing it.** PASS / FAIL / NOT-RUN separately.
**And: push with git, not file-by-file.** **Your git push is why the modes and the bytes survived, and mine
is why they did not.**
