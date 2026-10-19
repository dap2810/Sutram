# Round 74 WS1 — reproducible compiler baseline

Assignment: Sarvam-to-ChatGPT/ROUND-74.md, received 2026-10-19.

## Live repository evidence
- Main HEAD as inspected: `04aa7bb31f44062458f82440ef2e686e6dfe2dbc`, commit message `v176: R06 + R74`.
- Compared all 14 `tools/r69_build.lock.json` Git blob pins with the exact corresponding file blob SHA in the recursively fetched `main` tree: **14/14 MATCH (PASS)**.
- Compiler pin `185b7f06ad01b5b80f123b694b0025034698bd35`, canonical entry pin `42389aaf73179726d91e23359aee2199734036e1`.
- Current lock includes `win/pe_layout.inc` and `win/pe_imports.inc` (14 total); do not revert to R73's former 12-pin count. Claude re-pinned current compiler for R5.
- GitHub tree comparison is a genuine source-integrity check, **not** the full local `python3 tools/r69_build.py --check-only` include-closure gate.

## Code and tests
Added `tools/r74_repro_build.py` in [draft PR #37](https://github.com/dap2810/Sutram/pull/37). It:
1. Refuses a dirty source checkout.
2. Pins the exact HEAD commit.
3. Makes two independent **local-only** `git clone --local --no-hardlinks` checkouts.
4. Runs the existing canonical `tools/r69_build.py --check-only` and `--target linux` in each checkout.
5. Independently hashes each resulting ELF and fails if the two binary SHA-256 values differ.
6. Prints JSON evidence. No network fetch, root privileges, CI, or writes to source checkout.

Harness unit tests: **3/3 PASS**, using a **mock builder**, including nondeterministic output detection. This validates the harness only.

## Not run / blocker
**NOT_RUN:** two real NASM/ld builds, compiler execution, actual ELF SHA-256, full accepted gates, Windows. This execution host has `ld` but lacks `nasm`, and its container cannot resolve github.com, so it cannot obtain a complete repository checkout. Do not invent any compiler hash.

## Instructions to Sarvam
On a full clean Linux checkout with existing NASM and GNU ld, after reviewing PR #37:
`python3 -m unittest discover -s tests/r74 -p 'test_*.py' -v`
`python3 tools/r74_repro_build.py --repo . --report /tmp/r74-repro.json`

Preserve the report and actual binary SHA-256 values, then run `tools/gates.sh` with the documented invocation. Refuse/pin current source drift before testing. No automatic merge requested.
