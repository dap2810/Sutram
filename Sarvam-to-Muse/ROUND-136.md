# Sutram — ROUND-136: run ChatGPT's four escape probes. This is the memory-safety question.

**Base:** main at v306 · **Deliver into:** `Muse-to-Sarvam/`

## ChatGPT's R207: the slice class, the five release conditions, and why a two-hash check fails

**It found a THIRD path to the stale slice - not another spelling of a function-value call, but erasing a slice into untyped storage.**

**Source evidence, four predicates each with a hardcoded kind list:**
- `r126_check_assign .cell` rejects `r126_is_kosh_value`, which recognizes kinds **2, 3 and 6**. **A slice is kind 1.**
- `r127_check_slice_value` rejects a direct kosh slice in named declarations/assignments, **but is not applied by that cell-store branch.**
- `r126_check_untyped_arg` rejects kosh values, **not kind-1 slices.**
- `r23_check_return` recognizes syntactic slices and locally tracked slice variables; **an untyped parameter does not retain that classification.**

**So the rule is not enforced at the call site. It is enforced in four separate places, each with a hardcoded list, and none of them includes the slice's kind.**

**The minimal probe it did NOT run:**
```sutram
mukhya() {
    kosh k[1]
    kosh_kship(k, 7)
    vitti obstacle = nirmmita(16)
    mala box[1]
    box[0] = k[0:1]
    kosh_kship(k, 8)
    likha(box[0])
}
```

### The five finite acceptance conditions for a YES

1. **Slice closure** - reproduce or refute the escape candidates; hazardous cases become compile-time refusals.
2. **Windows setup and OOM** - check exception-handler registration; an injected NULL must stop cleanly before lazy memory is used.
3. **Recoverable interrupted installation** - a forcibly interrupted install can be completed on retry; a genuine user file is still protected.
4. **Exact candidate acceptance** - build and package once fixes land; verify pins, payload hashes and gates.
5. **Truthful release description** - correct the hang history, the recovery behaviour, and the exclusions.

**And it says the unexplained hang need not block release: *"The unexplained historical hang need not force an endless investigation if the replacement candidate has bounded failure, useful diagnostics..."***

### And why Claude's proposed two-hash check is insufficient

*"An intact file matching either the previous or pending payload hash is recognized product content. A half-written file matches neither. The proposed two-hash check still cannot classify the empty 132nd file. A marker for the whole directory does not prove every file in it belongs to the installer."*

**So the transaction needs a journal, created and durably published BEFORE anything is deleted or truncated, in a private directory beside the target on the same volume.**

## WS1 - four probes, one per predicate
**ChatGPT read the source and named four places where the slice rule is not applied.** **It ran none of them.**

**Write and run one probe per predicate:**

1. **the cell store** - the probe above: a slice into `mala box[0]`, then grow the source
2. **the untyped parameter** - a slice passed to a `prakriya` whose parameter is untyped, which grows the source
3. **the untyped return** - a `prakriya` that returns a slice as an untyped result, then the source grows
4. **the function value** - a slice passed to a `prakriya` called through a variable

**For each: does it print the old value, the new value, or crash?**

**A stale read is the worst outcome and it is what we are looking for.**

## WS2 - and if any of them reproduce
**That is a memory-safety defect in a release candidate.** **Say so plainly and say which probe.**

**Then: is the cause the four predicates, or is there a fifth path nobody named?** **You found 8 defects where Claude found 3 by testing independently. Do the same here.**

## WS3 - and the reconstruction
**Claude reconstructed the interrupted v303 copy: 131 matching payload files, five previous installation-state files, and an empty `docs/rounds/PROJECT-OVERVIEW.md` at position 132.**

**Is that reconstruction sound?** **Read the payload manifest and check: is `PROJECT-OVERVIEW.md` plausibly the 132nd file in copy order, and is it large enough that a partial write would leave it empty?**
