# Sutram — ROUND-134: one predicate for the slice class, and a transaction journal for the installer

**Base:** main at v306 · **Deliver into:** `Claude-to-Sarvam/`

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

## WS1 - the slice class, closed by one predicate
**Four predicates, four hardcoded kind lists, none including kind 1.**

**The fix is not a fifth check. It is ONE predicate - "is this value a `kosh` or a slice of one" - used in all four places.**

**Build it, and make it impossible to add a fifth site that forgets.**

**Then run the probe above and report what it prints before and after.**

## WS2 - and the installer transaction journal
**ChatGPT's argument against the two-hash check is decisive: a half-written file matches neither hash, so the check cannot classify the empty file at 132.**

**So: a private transaction directory beside the target, on the same volume, with a journal durably written BEFORE anything is deleted or truncated.**

**Read its WS3 in full - it gives the ordering. Build that.**

**And one requirement it names that matters: an interrupted install must be completable on retry, while a genuine user file is still protected.**

## WS3 - and the logging
**Its line: *"Logging every 100 completed copies cannot identify an in-progress copy; log a start and finish for each file."***

**Do that. It costs nothing and it would have identified file 132 on the first hang.**
