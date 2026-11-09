# `Sutram-Setup-v297.exe` - removed from the tree in R156 (9 November 2026)

**Sarvam's ROUND-156 instruction:** a six-version-old installer inside an evidence folder, which is not the shipped
package, kept as its hash and a note.

- **SHA-256** `fabece5f0945c938a45f3c379fe5d7dd816647e23a6fe60d5f19aa00859f3b65` (it is also in
  `Sutram-Setup-v297.sha256`, next to this note), **1,946,102 bytes**. It is the v297 Windows build this folder's
  `native-cases.json`, `build-success.log` and `payload-check.log` were made with.
- **It is still in git history:** the last commit carrying it is `e316585c6155e7dcffb83d458944fae36ef45a5b`. To get it
  back: `git show e316585c:Windows-to-Sarvam/win-v297-2026-11-03/Sutram-Setup-v297.exe > Sutram-Setup-v297.exe`, then
  compare its SHA-256 with the line above.
- `REVIEW-V297-2026-11-03.md` (one folder up) links the file; that link now leads here only by name.
