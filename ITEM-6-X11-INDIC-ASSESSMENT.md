# Item 6 - the X11 GUI's Indic support: an assessment, not a fix

**Item 6 of `PLAN-TO-FINISH.md`.** Measured 2026-10-20 at v222.

## What I found

**The Linux X11 GUI draws all its text with `ImageText8` and the core `fixed` font.**

| Evidence | Meaning |
|---|---|
| `ImageText8` used 3 times | the **8-bit** core X11 text protocol |
| the font is `fixed` | a **core font** - 8-bit, no Indic coverage |
| `ldd` says *"not a dynamic executable"* | **no freetype, no fontconfig, no Xft** |
| 16 references to 3-byte UTF-8 lead bytes | it *counts* clusters, so it knows the bytes - **but it cannot draw them** |

**So the Linux GUI cannot display the language it is for.** Latin keywords render; Devanagari, Gujarati,
Tamil and the rest cannot, **because an 8-bit core font has no glyph for them and the protocol has no way to
ask for one.**

## Why this is not a task I can finish here

**Fixing it means replacing the text path, not patching it:**

1. **Client-side font rendering** - Xft over freetype and fontconfig. **Three new libraries**, and the GUI is
   currently a static binary with none.
2. **Glyph shaping** - Devanagari is not one byte per character and not one glyph per codepoint. **Clusters
   form and reorder** (a vowel sign before its consonant in the byte stream, after it on screen). The
   project already has a cluster *counter*; **a shaper is a different and larger thing.**
3. **Layout** - the editor's column arithmetic, the cursor, the gutter and the syntax colouring **all assume
   one byte is one column.** Every one of them changes.

**Claude said "several rounds" and it is right.** I said I would start it and I have - **by establishing what
it is, which is the only honest thing to do rather than begin a rewrite I cannot finish in this stretch.**

## And the judgement on whether it should be done now

**It is not on the road to v1.0, and I would not start it.**

- **The Windows IDE already draws all eleven scripts** - it uses `CreateFontW` with a font that covers them.
  **So the capability exists on the platform the owner actually uses.**
- **The X11 GUI is a Linux convenience.** The project's own definition of v1.0 is *"procedural core correct
  and complete, library usable, Windows installs and runs, diagnostics in the user's language."* **None of
  those four requires an Indic-capable X11 GUI.**
- **And it is the kind of change that touches everything.** A font-path rewrite plus a shaper plus layout
  arithmetic is **weeks of work with a high chance of regressing the Linux GUI that currently works.**

**So my recommendation is to record it and not do it**, with the reasoning, rather than spend rounds on a
Linux-only surface while the Windows one - the one the owner tests - already works.

**If the owner wants it, it should be its own milestone, not an item in a queue.**

## What I am doing instead

**Reporting it, with the evidence, so the decision is his and it is informed.** The alternative - starting a
font-path rewrite and stopping halfway - would leave the Linux GUI worse than it is now.

