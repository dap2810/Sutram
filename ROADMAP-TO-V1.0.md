# Sutram — the road to v1.0

**The single source of truth for what we are finishing, in what order, and why.**
Every round brief points here. If a task is not on this list, it is not on the critical path.

Last updated: 2026-10-19 · v176

---

## What v1.0 is

**v1.0 is: the procedural core is correct and complete, the standard library is usable, Windows installs
and runs, and the diagnostics are in the user's language.**

**v1.0 is NOT:** generics, structured concurrency, event-driven programming, the freestanding/kernel
demonstration, separate compilation, or the remaining language packs. Those are v2, and every one of them
sits on a foundation this list is still measuring.

**A v1.0 user can:** install on Windows without admin rights, write a program in their own Indian language
and script, compile it to native machine code with no runtime, use a documented standard library, and read
an error message in their own language.

---

## The order, and why it is this order

Each step is placed by **what it unblocks**, not by importance.

| # | Step | Owner | Done when |
|---|---|---|---|
| **0** | **Define v1.0** | Sarvam | This page. **Done.** |
| **1** | **Close the silent-wrong-answer class** | Claude | Every name-resolution path — variables, functions, fields, array indices, module aliases, builtins — errors on a wrong name, with a test per path |
| **2** | **Decide and apply the diagnostics language** | Owner decides, Claude applies | Interface and diagnostics are in the same language |
| **3** | **Make Windows a gate, then pass it** | Claude builds, **owner runs** | `tools/accept-windows.ps1` exists and every check passes on real Windows |
| **4** | **Fix the `kosh` leak** | ChatGPT | Mapping count returns to baseline, measured before/after |
| **5** | **Prove the library is complete** | Muse (paused) | Every module has a contract, a passing proof, and a running example |
| **6** | **Compile every code sample in every document** | Sarvam | All books, the reference and the stdlib page: every block compiled and passing |
| **7** | **Measure performance** | Sarvam | A benchmark gate in `gates.sh`, with the machine recorded |
| **8** | **Security and least-privilege audit** | Sarvam + Claude | A checklist with evidence, not a claim |
| **9** | **Install / upgrade / uninstall on clean Windows** | **Owner** | All three work and leave nothing behind |
| **10** | **Freeze and release v1.0** | Sarvam | Tagged, `gates.sh` green including Windows, CHANGELOG records it |

### Why this order

- **1 is first because everything rests on it.** Three rounds in a row found *more* instances of a wrong
  name silently succeeding — undefined names reading 0, `p.w` reading `p.x`, an 8-byte field comparison, an
  undeclared array crashing. **That pattern means we have been finding cases, not the cause.** A language
  for beginners cannot ever return a wrong answer with no diagnostic.
- **2 comes before 3** because it touches 83 strings and 28 goldens. Do it after acceptance and you run
  acceptance twice.
- **3 is the gate that has never closed.** It must be run against a compiler that is finished on 1–2.
- **4 is measured and real** — about 15.3 bytes per item, `mmap` with no `munmap`, and **no free primitive
  in the language**. That may be a *language* decision, not a library fix.
- **5 and 6 come after the compiler stops moving**, because a proof and a code sample are only true against
  a fixed compiler.
- **7, 8 and 9 are the release conditions.** Nothing ships without them.
- **10 is a ceremony, not work** — it is only reached when 1–9 are done.

---

## Who can do what, and the honest limits

- **Sarvam** (this agent) owns the repo, verifies every delivery by rebuilding and re-running the gates,
  syncs to main, and works its own steps (0, 6, 7, 8, 10).
- **Claude** — compiler correctness, the Windows interface and the acceptance script.
- **ChatGPT** — compiler internals, the baseline, the `kosh` reclamation, module design.
- **Muse** — the standard library and proofs. **Paused.**
- **The owner** — the two things nobody else can do: **run the Windows acceptance on a real machine**, and
  **make the language decisions** (the diagnostics language, and whether a wrong name is always an error).

**The limit that shapes this list:** Sarvam cannot execute Windows. It can verify a binary is a valid
PE32+, that hashes match, that the source is correct, and that it cross-builds — **but it cannot run it.**
Every Windows claim therefore rests on a log, and **the owner's own run is the only fully independent
check.**

---

## The rule for every round

Every brief opens with **a memory update** — the current version, the gates, and what changed since the
partner last worked — **then names the step this round advances**, then the workstreams.

**A verified partial beats a claim.** PASS, FAIL and NOT-RUN are reported separately, with the environment
named per check. Nothing is accepted on the strength of a report; it is rebuilt and re-measured first.

---

## What is explicitly not on this list

Generics · structured concurrency · event-driven programming · the freestanding/kernel demonstration ·
separate compilation · the remaining language packs · a compatibility alias layer for the rename.

**These are v2.** `yoj` being textual inclusion is a scalability limit, not a correctness one — a learner
will never reach it. **Every one of these is the interesting part, and every one sits on a foundation this
list is still measuring.**
