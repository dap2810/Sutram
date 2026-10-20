# Sutram — the plan to finish

**Written 20 October 2026, at v220.** This is the order we knock things off, who does each, and what "done"
means. It supersedes nothing — `ROADMAP-TO-V1.0.md` is still the release path. **This is the working plan for
the parameters that need no manual testing.**

---

## The rule this plan follows

**Finish the important things that need NO manual testing first.** The owner's time is the scarcest resource
on this project, and there are exactly two things only he can do:

1. **Install it on Windows** (parameter 15 — portability)
2. **Read the Gujarati messages** (the three-language review)

**Everything else has an owner who is not him.** So the plan is: knock off everything that doesn't need him,
and leave him a short, high-value list when he is free.

---

## Priority queue — manual-free, and important

| # | Task | Owner | Why it is first | Done when |
|---|---|---|---|---|
| **1** | **The fuzzers** (parameter 19) | Claude | **F1 and F7 both came from humans, not gates.** This is the gap the charter names itself | A stated number of programs run with no crash, and any counterexample returned as a file |
| **2** | **Separate compilation** (parameter 16) | ChatGPT | `yoj` is textual inclusion — **the biggest structural upgrade to the language**, fully testable here | Two modules compile to objects and link into one binary; or the smallest failing case with its error |
| **3** | **A formatter** (parameter 17) | Claude | Small, self-contained, immediately useful, testable automatically | `sutram-fmt` normalises a file; idempotent on a second run |
| **4** | **Real error handling** (parameter 12) | ChatGPT | The `ok` out-param is the weakest part of the surface | A `phal`-style type with propagation, and a proof that a failure cannot be silently ignored |
| **5** | **F7 — the scalar-index crash** | Claude | A segfault on a plausible mistake. Has a minimal reproduction | Fixed, with a test that fails on v220 and passes after |
| **6** | **The X11 GUI's Indic support** (parameter 17) | Sarvam | **The Linux GUI cannot display the language it is for** | All eleven scripts render in the X11 IDE |
| **7** | **Coverage audit, done properly** | Sarvam | Compare every book construct against every test construct, mechanically | A list of constructs covered by no test — or a stated zero |

**Items 1–5 are in flight or issued now. 6–7 are mine and start as the others land.**

---

## Held, deliberately — and the reason is the charter's own sequence

**Parameters 2, 4, 5, 8, 10, 11, 13, 18 are all finishable without the owner** — first-class functions, methods
and traits, slices and SIMD, compile-time metaprogramming, stronger inference, an ownership model, a boot
path, and a C FFI.

**They are held because `PROJECT-MASTER.md` §5 says, in the project's own words:**

> *The project is at stage 1–2. Do not jump to stage 4.*

**Generics, concurrency and events are explicitly v2.** Doing them now would break the sequence that has kept
this project coherent — and a language that is procedural, multilingual and correct is worth more than one
that is half-generic and unstable.

**Exception:** if the owner says to break the sequence, **#11 (the memory model) is the one I would take
first**, because it changes what the language *is* rather than what it *has*.

---

## Needs the owner — the short list

| # | Task | Time | What it unlocks |
|---|---|---|---|
| **A** | **Install `Sutram-Setup.exe` on Windows** | ~20 min | **Parameter 15.** The one no AI can move |
| **B** | **Run `sutram.exe` and the IDE** | ~15 min | The Windows acceptance — open the longest |
| **C** | **Read the Gujarati messages** | ~30 min | The three supported packs become *verified* rather than *drafted* |

**Then I tag and freeze v1.0.** That is the whole remaining critical path, and **two thirds of it is A and B
— one Windows session.**

---

## How each round works

**Every handover carries:** a measured progress update, the language directive, the parameter it advances,
numbered workstreams, the constraints, and the return contract. **Every delivery is verified against the
files, not the report.** **Nothing merges unverified.**

**And the standing rule, which has held all project:** *a verified partial beats a claim.* **A partner has
caught a real error of mine eleven times.** That is the mechanism working, and it is worth more than any
single green gate.
