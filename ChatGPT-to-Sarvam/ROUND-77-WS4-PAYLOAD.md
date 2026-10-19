# R77 WS4 — Windows installer carries old compiler
Confirmed by independently SHA-256 hashing actual decoded GitHub binary content, after validating the SHA-256 helper against published abc vector:
* win/sutram.exe — Git blob b38f7408a046bb3e5b6bea774e386d3a16f11941 — SHA-256 b6e2bb342e75600a3e67b9263a27725f15494384804edbfa4c72234ec8b93b1b — embedded v160.
* sutram.exe — Git blob 9af5c4806e6c5e3c6ee0ed3cc7ee63b1a6400626 — SHA-256 ffc2368cb82f113c4dd48842752a60e36ecd5d28a85c7783befd9296a8e061f8 — embedded v182.
* sutram_compiler (Linux) — SHA-256 219d1cf043fa7039ec9ef3e0755b720dc998a92aaf058d173184c5e8518dbbc8 — embedded v160.
* Current main NASM msg_version text reads v182. The current installer builder copies win/sutram.exe into BOTH payload compiler locations.

**Code delivered:** draft PR #43 modifies windows/native-installer/build-installer.ps1. It parses expected version from current source, runs the Windows payload compiler --version with the already bounded runner, rejects stale output and verifies SHA-256 of BOTH staged compiler copies. Direct stale packaging should now refuse rather than create a misleading setup.

**New Sutram-Setup.exe NOT BUILT** here (no Windows PowerShell or NASM). The hashes above are stale/current input hashes, NOT a rebuilt installer payload hash. Rebuild on standard-user Windows:
powershell -NoProfile -File windows/build-windows-setup.ps1
Run the finished installer self-test; record SHA-256 of generated payload and installed compiler, perform actual --version test and installer acceptance. No installer binary uploaded as completed.
