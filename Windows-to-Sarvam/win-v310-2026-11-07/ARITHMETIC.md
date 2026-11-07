# v310 arithmetic refusals

Both the brief's add/XOR wrappers and the original preserved v307 reproductions refuse with exit 1 and produce no executable. Exact diagnostic for all four:

```text
Sutram truti [E_VIBHAG_ANKA]: vibhagah 'k' sankhya iva upayujyate - vibhagah ganite, tulanayam, pratibandhe, likha-adau va na sankhya
Sanket: vibhagasya mulyam s[i] ityena pathya; dairghyam pankti_gan(s); vibhagam vibhag-tarke preshaya
```

The valid `pankti_gan(k[0:2])` control compiles, exits 0 and prints `2`.

[Brief cases and control](expressions/results.json); [original add/XOR sources and commands](supplemental/results.json). These are new v310 executions, not recycled v309 counts. See INITIALIZER.md for the disclosed initial scorer correction.
