# Sutram R75 WS1 — baseline provenance correction (2026-10-19)

Live main when assigned: `05d8bdc8b461080809cdcb1187cabf22c5691001` (v180); before delivery live main advanced to `c94d9369af3c8acc9a390acdedc7549b937f6bc0` (v181). The compiler blob remained `185b7f06ad01b5b80f123b694b0025034698bd35` and the current release lock `tools/r69_build.lock.json` remains blob `a0656e87112c56c47aa3604854f73f9c8012e556`.

### Actually performed
Via connected GitHub interface: fetch recursive `main` Git tree and `tools/r69_build.lock.json`; compare each expected Git blob with actual tree blob. **14/14 PASS**, no drift. Repeated at v181, **14/14 PASS**.

### Crucial correction to Sarvam's ROUND-75 premise
Sarvam wrote “R74 was a reproducible baseline ... genuine PASS.” The R74 source-lock check was a real PASS, but the *two actual NASM binary builds* were explicitly NOT_RUN in our R74 handoff. Unit tests exercised a mocked builder, not real NASM. No `r74-repro.json` with two actual binary SHA-256 hashes exists in this session. Do **not** call compiler binary repeatability PASS without producing that JSON.

Raw commands attempted on current host:
`command -v nasm` -> NOT_FOUND
`command -v ld` -> /usr/bin/ld
`git ls-remote https://github.com/dap2810/Sutram.git HEAD` -> fatal: unable to access ... Could not resolve host: github.com.

`tools/r74_repro_build.py` still lives in draft [PR #37](https://github.com/dap2810/Sutram/pull/37), not main. A clean native checkout with installed NASM and ld must run it and return real JSON before WS1 can be marked an executable baseline PASS.

**WS1 status:** Source identity PASS 14/14; clean native binary build/reproducibility **NOT_RUN**. No compiler binary hash fabricated.
