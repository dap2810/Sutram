# R14-02 — WS2: the R5 question, for the owner

**Nothing was changed.** The question, as one paragraph to put to him:

> **In ROUND-05 you chose English for the Windows IDE's menus, buttons and the two Help dialogs** (`File`,
> `Run`, `Load example`, `About Sutram` …). That was before the course change to three languages. **Since
> then the default has become Sanskrit throughout, and the Linux IDEs have no English left.** So the
> Windows IDE is now the only place where the project speaks English. **Should it stay English, or
> should its menus and buttons use the default's romanised Sanskrit, as the Linux IDEs do?** The change
> is the 52 strings in one table at the top of `windows/gui/sutram_gui.asm` and the IDE checks in
> `tools/test_windows_gui.py`, about part of one round. **A one-word answer is enough: "English" or
> "Sanskrit".**

**Two things he may want to know before he answers:**

- **Two of those 52 strings are already not English, but are Hindi grammar:** `sankalan / chalan ka phal`
  and `udaharan (do baar click)`. Whatever he decides, these two would move to Sanskrit grammar, like the
  rest of the default (R13-02).
- **Either answer leaves the menus in one language for every pack.** Making them follow the selected pack
  (Gujarati menus when the pack is Gujarati) is a larger, separate change, and nobody has asked for it.
