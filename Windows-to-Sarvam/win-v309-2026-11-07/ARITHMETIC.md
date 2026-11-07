# v309 arithmetic verification (Task A)

**7/7 pass on native Windows.** The two original add/XOR reproductions are refused; no executable is emitted. The valid slice-length control prints `2`.

[Exact argv, output streams, exit codes and timings](arithmetic/results.json); [commands and provenance](COMMANDS.md).

| Program | Expected | Actual | Pass? |
| --- | --- | --- | --- |
| `keep(k[0:1] + zero)` | refusal | exit 1, no executable, E_VIBHAG_ANKA | PASS |
| `keep(k[0:1] ^ zero)` | refusal | exit 1, no executable, E_VIBHAG_ANKA | PASS |
| `likha(k[0:1] + 0)` | refusal | exit 1, no executable, E_VIBHAG_ANKA | PASS |
| `yadi (k[0:1])` | refusal | exit 1, no executable, E_VIBHAG_ANKA | PASS |
| `likha(k[0:1])` | refusal | exit 1, no executable, E_KOSH_VIBHAG | PASS |
| `vitti i = k[0:1]` | refusal | exit 1, no executable, E_KOSH_VIBHAG | PASS |
| `pankti_gan(k[0:2])` | 2 | compile 0; native exit 0; stdout `2\n`; empty stderr | PASS |

The six refusals are written to **stdout**, with empty stderr. All six output paths were absent before compilation and remained absent. The prior add/XOR sources are copied without rewriting their reproductions.

## `keep(k[0:1] + zero)`

Source: [add.sm](arithmetic/add.sm). Compiler exit `1`.

Exact compiler stdout:

```text
Sutram truti [E_VIBHAG_ANKA]: vibhagah 'k' sankhya iva upayujyate - vibhagah ganite, tulanayam, pratibandhe, likha-adau va na sankhya
Sanket: vibhagasya mulyam s[i] ityena pathya; dairghyam pankti_gan(s); vibhagam vibhag-tarke preshaya
```

## `keep(k[0:1] ^ zero)`

Source: [xor.sm](arithmetic/xor.sm). Compiler exit `1`.

Exact compiler stdout:

```text
Sutram truti [E_VIBHAG_ANKA]: vibhagah 'k' sankhya iva upayujyate - vibhagah ganite, tulanayam, pratibandhe, likha-adau va na sankhya
Sanket: vibhagasya mulyam s[i] ityena pathya; dairghyam pankti_gan(s); vibhagam vibhag-tarke preshaya
```

## `likha(k[0:1] + 0)`

Source: [add-literal.sm](arithmetic/add-literal.sm). Compiler exit `1`.

Exact compiler stdout:

```text
Sutram truti [E_VIBHAG_ANKA]: vibhagah 'k' sankhya iva upayujyate - vibhagah ganite, tulanayam, pratibandhe, likha-adau va na sankhya
Sanket: vibhagasya mulyam s[i] ityena pathya; dairghyam pankti_gan(s); vibhagam vibhag-tarke preshaya
```

## `yadi (k[0:1])`

Source: [condition.sm](arithmetic/condition.sm). Compiler exit `1`.

Exact compiler stdout:

```text
Sutram truti [E_VIBHAG_ANKA]: vibhagah 'k' sankhya iva upayujyate - vibhagah ganite, tulanayam, pratibandhe, likha-adau va na sankhya
Sanket: vibhagasya mulyam s[i] ityena pathya; dairghyam pankti_gan(s); vibhagam vibhag-tarke preshaya
```

## `likha(k[0:1])`

Source: [direct-print.sm](arithmetic/direct-print.sm). Compiler exit `1`.

Exact compiler stdout:

```text
Sutram truti [E_KOSH_VIBHAG]: kosh-vibhagah 'k' smriti-sthanam iva na upayujyate (likha, pad8, likh8 ...)
Sanket: vibhagah koshasya mulyani tada yatha asan tatha darshayati - tam sakshat vibhag-tarke preshaya (f(k[1:4])); sthapayitum pratilipim kuru
```

## `vitti i = k[0:1]`

Source: [store.sm](arithmetic/store.sm). Compiler exit `1`.

Exact compiler stdout:

```text
Sutram truti [E_KOSH_VIBHAG]: kosh 'k' vibhagah vittau na sthapyate - kosh vardhate cet tasya mulyani anyatra gacchanti
Sanket: kosh-vibhagam sakshat preshaya - f(k[1:4]); vittau kosh eva sthapaya (vitti b = k)
```

## `pankti_gan(k[0:2])`

Source: [length.sm](arithmetic/length.sm). Compiler exit `0`.

Exact compiler stdout:

```text
Siddh: 3584 baait sankalit
```

Native stdout is exactly `2\n` (LF), native exit 0, empty stderr.
