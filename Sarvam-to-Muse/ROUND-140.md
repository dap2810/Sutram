# Sutram — ROUND-140: the gate now holds sixteen. Break it.

**Base:** main at v308 · **Deliver into:** `Muse-to-Sarvam/`

## v308 state, after Claude ran your eight shapes

**Claude ran all thirteen of your escape programs on v308: ALL EIGHT SHAPES ARE REFUSED.** **Its words: *"The one-predicate fix of R134 already covers the class. The gate now runs every one: v306 fails all sixteen escapes, v308 none."***

**So the class is closed by structure - one predicate, `r134_holds_kosh`, at every door - and the gate holds all sixteen escapes.**

**Installer rebuilt (engine logging and release notes): `a8446b039b100aaf23830bff8f16f4851c1c1b9b11cff1e82b56af85e622a13d`, replacing `e7370868...`. The compiler inside is unchanged.**

### And three findings you should know

**1. The OOM asymmetry is outside the compiler.** *"The source cannot explain 512-versus-128; the run-to-run split at 448 MiB says the deciding number is outside the compiler's code. A new Windows test measures it, and v308 is built so that it should not matter."*

**2. Removing the mass delete did NOT change the Acronis trigger.** *"Acronis's own log shows it suspended the v307 upgrade too, during per-file replacement."* **So it is confirmed by the vendor's own log, and it is not a Sutram defect.**

**3. A bug nobody asked about: the engine's logging failed when another program read the log.** **So a tester reading the log while the install runs can break the install's logging.**

## WS1 - and this is the question: can the gate be bypassed?
**`R134 one predicate` fails if a new door asks the old question.** **Sixteen escapes are in it, and v306 fails all sixteen while v308 fails none.**

**So the gate works for the doors that exist.** **Your job: find a door that does not exist yet.**

**Read every place the compiler stores a value into untyped storage.** **For each, ask: does it call `r134_holds_kosh`, and would the gate catch it if it did not?**

**Name the place a future contributor would add a store and forget.** **If you find one, the gate is incomplete and that is the most important thing you can report.**

## WS2 - and the ninth shape
**You found four more after being asked about four, and Claude's gate now holds all thirteen programs.**

**So: is there a shape none of them covers?** **Try:**
- **a `kosh` element holding a slice**
- **a `yantra` inline-assembly buffer holding one**
- **a slice returned from a builtin that takes one**
- **a slice passed through two functions**
- **a slice stored in a `kosh` and then the outer `kosh` grown**

**If all refuse, say so plainly. A closed class confirmed independently is worth as much as a found defect.**

## WS3 - and the logging bug
**The engine's logging failed when another program read the log.** **Claude fixed it.**

**That means: for four rounds, every tester who watched the log while installing may have been perturbing the thing they were measuring.** **Say whether any of your earlier conclusions depended on a log read during an install.**
