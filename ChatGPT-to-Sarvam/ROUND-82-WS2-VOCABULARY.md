# Sutram R82 WS2 — old-keyword audit tool corrected, exhaustive run pending

Review branch: [PR #37](https://github.com/dap2810/Sutram/pull/37), `review/r74-reproducibility-audit-20261019`.

**Actual change:** `tools/r74_vocabulary_audit.py` previously reset `block=False` on **every input line**. In a multi-line Sutram `/* ... */` comment, old keyword strings on subsequent lines were therefore reported as active source, a false positive. The updated scanner carries `in_block` from line to line and applies the same masked line to both old-keyword detection and range-`to` detection. Three new tests were added in `tests/r74/test_vocab_audit.py`: obsolete keywords inside multi-line comments must be ignored, active old keywords following the closing delimiter must still be detected, and mixed comment/range cases must be classified correctly. Readback source blob `b900b274225743065cd7f01b782b7ba4aa5713ce`, test blob `0fcd2002fe75ce972e92819d4e5ff05ed63e3331`.

**Five/five static source assertions PASS** against actual GitHub readback: mask takes prior state, returns final block state, scan propagates it, range detection uses the masked line, and three tests are present. **Python unit tests NOT_RUN** in this session; runtime Python/container tools failed at invocation. Never label this change accepted without executing those tests.

**Repository-wide scan NOT_RUN.** This round did not materialize the whole current v213 checkout. To complete, run in a clean complete checkout containing PR #37:

```sh
python3 -m unittest discover -s tests/r74 -p 'test_*.py' -v
python3 tools/r74_vocabulary_audit.py --repo . --output /tmp/r82-vocabulary.json
```

Review counts, excluded files, source-path errors and candidate contexts; manually triage active code, diagnostics and code fences. `pankti` can mean a line number; `to` is ordinary prose unless old range syntax; a literal `\n` can hide a keyword after the n. The scanner deliberately excludes historical handoffs and non-source files, so **even an exit PASS is a completed candidate inventory, not full semantic proof of every tracked file**. Do not rewrite accepted compiler messages, libraries or goldens to force a green status.
