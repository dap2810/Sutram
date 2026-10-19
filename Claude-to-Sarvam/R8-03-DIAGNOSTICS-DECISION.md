# R8-03 — WS3: the diagnostics decision, restated (nothing changed)

**Still the owner's decision, and still waiting.** The question is what language the compiler's errors and the
IDE's 22 status words use. The other half of the IDE is already English (R5). The options were counted in
R7-02:

| Option | What | Cost, as counted in R7-02 |
|---|---|---|
| **A** | keep it as it is | 0 |
| **B** | English only | 90 + 22 strings, 41 goldens, 4 R70 cases, 16 tool files, 18 docs |
| **C** | both on every error | as B |
| **D** | **selectable, default unchanged:** `--sandesh en`, which the English IDE passes | one two-column table and one lookup at 90 message sites; the goldens, R70 and the docs are unchanged; about 10 English goldens; 1–2 rounds |
| **E** | follow the `--lang` pack for every message | D plus 900 translations |

**My recommendation is unchanged: D now, E as translations arrive.**

- D makes the English IDE English end to end.
- It takes Sanskrit away from no one.
- It leaves every existing golden alone.
- It builds the table E fills.

**The one choice:** A, B, C, D or E. **And** whether the IDE's 22 strings follow it. I recommend yes.

**New since R7-02: nothing that changes the numbers.**

- No compiler source changed this round, so the counts (90 strings, 41 goldens, …) still hold on v183.
- **If the R8-02 checks are approved,** they add about 3 new messages:
  - assigning to a `sutra`
  - `krama` / `agrim` outside a loop
  - a duplicate `bhavana`
- **If D is chosen first,** those go straight into its table instead of being written once in Sanskrit and
  added again later.
- **That argues for deciding D before the R8-02 step, or in the same round.**
