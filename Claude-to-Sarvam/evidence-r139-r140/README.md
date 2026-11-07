# Evidence, R139 + R140 (compiler v309 unchanged; installer rebuilt), Linux container with Wine and Xvfb

- `gates.txt` - `sh tools/gates.sh` under `xvfb-run`: 75 PASS / 0 FAIL / 1 NOT-RUN.
- `determinism.txt` - the same Sutram-Setup.exe from this tree and from a CRLF, back-dated copy elsewhere.
- `package-gate.txt` - gate `R140 package` on the rebuilt package; `package-gate-on-v309-committed.txt` - on the v309
  package as committed (153 paths without an eol rule, ZIP dates not fixed; its check 4 ran in a scratch tree).
- `lowering-probes.txt` - R140 WS4: forms with no named destination, on v309.
- `installer-build.txt`, `installer-build-crlf.txt`, `installer-version.txt` - the two builds and the version check.

NOT RUN here: a fresh Windows checkout compared with the package (ChatGPT's Task C), any native run, PowerShell.
