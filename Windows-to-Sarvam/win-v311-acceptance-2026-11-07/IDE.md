# B1–B4: installed native v311 IDE

The actual Start Menu shortcut `Sutram/Sutram IDE.lnk` was resolved and launched. Its target and working directory are the canonical installed Sutram folder, not a copied test IDE. The native process and visible controls/screenshots are recorded in [ide.json](ide.json); automation is in [ide-acceptance.ps1](ide-acceptance.ps1). All four screenshots were visually inspected.

The hello example was selected in the IDE and Run invoked. Deliberately invalid programs were opened through the real Open dialog and Run invoked; native button/menu messages automated the interactions. Probe files are outside the installation. The installed `01_hello.sm` hash was identical before and after the test.

## B1 — B1-hello

[B1-hello screenshot](B1-hello.png)

Window title: `01_hello.sm - Sutram sampadak`. Exact output control text:

```text
Namaste, Sutram!
```

## B2 — B2-syntax

[B2-syntax screenshot](B2-syntax.png)

Window title: `syntax.sm - Sutram sampadak`. Exact output control text:

```text
Sutram truti: vyakaran dosh, pankti 2:11, shabd '='
      vitti =
            ^
Sanket: asmin sthane shabdam vyakaranam cha pashyatu.
[sankalan asaphal]
```

## B3 — B3-arithmetic

[B3-arithmetic screenshot](B3-arithmetic.png)

Window title: `arithmetic.sm - Sutram sampadak`. Exact output control text:

```text
Sutram truti [E_VIBHAG_ANKA]: vibhagah 'k' sankhya iva upayujyate - vibhagah ganite, tulanayam, pratibandhe, likha-adau va na sankhya
Sanket: vibhagasya mulyam s[i] ityena pathya; dairghyam pankti_gan(s); vibhagam vibhag-tarke preshaya
[sankalan asaphal]
```

## B4 — B4-large-file

[B4-large-file screenshot](B4-large-file.png)

Window title: `arithmetic.sm - Sutram sampadak`. Exact output control text:

```text
[patram atibrihat; sampadaka-seema 64 KiB]
[patram na udghatitam - sampadake purvam patram eva asti]
```

B2 replaces the prior `Namaste, Sutram!` output with a Sanskrit syntax diagnostic at line 2, column 11. B3 replaces that diagnostic with `E_VIBHAG_ANKA`; no scalar number is produced. The exact requested [arithmetic source](arithmetic.sm) and [syntax source](syntax.sm) are included.

B4 opens [too-large.sm](too-large.sm), exactly **81,000 bytes**. The refusal replaces the previous diagnostic; it does not leave stale arithmetic output. The title and editor content still refer to `arithmetic.sm`, and the new output explicitly says the previous file is retained. This was an open/refusal test, not a new Save-protection test.

The IDE process closed normally, and [final-process-check.json](final-process-check.json) confirms it is gone. These native execution observations do not depend on PE structure validation. No general shell, canonical-icon or release acceptance is implied.
