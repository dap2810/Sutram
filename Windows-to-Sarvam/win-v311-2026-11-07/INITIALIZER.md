# v311 initializer verification

All requested snippets were compiled anew against the pinned v311 compiler. Full argv, outputs and source hashes are in [expressions/results.json](expressions/results.json).

## global-direct

Exit 1; executable produced: False.

```text
Sutram truti [E_KOSH_DVARA]: kosh 'make_kosh(...)' vaishvika-vittau na sthapyate
Sanket: kosh tasya namna eva gacchati - vitti b = k, kosh-tarkah (kosh k), kosh_* prakriyah; mulyani k[i] ityena
```

## global-add

Exit 1; executable produced: False.

```text
Sutram truti [E_KOSH_GANIT]: kosh-upari ganitam tulana va na sambhavati - kosh sankhya na
Sanket: k[i] tasya mulyam; kosh_gan(k) tasya dirghata - tani tulyantam
```

## valid-global

Exit 0; executable produced: True.

```text
Siddh: 208 baait sankalit
```

Native run: exit 0; stdout `7`.

## two-globals-no-main

Exit 1; executable produced: False.

```text

Sutram truti: vyakaran dosh, pankti 3:1, shabd 'patra-ant'
  
  ^
Sanket: asmin sthane shabdam vyakaranam cha pashyatu.
```

## record-literal

Exit 1; executable produced: False.

```text

Sutram truti: vyakaran dosh, pankti 1:20, shabd ':'
  rachana Point = { x: 1, y: 2 }
                     ^
Sanket: asmin sthane shabdam vyakaranam cha pashyatu.
```

## default-argument

Exit 1; executable produced: False.

```text

Sutram truti: vyakaran dosh, pankti 1:12, shabd 'vitti'
  prakriya f(vitti n = 5) { nivartanam n }
             ^
Sanket: asmin sthane shabdam vyakaranam cha pashyatu.
```

## two-globals-with-main

Exit 0; executable produced: True.

```text
Siddh: 230 baait sankalit
```

Native run: exit 0; stdout `3`.

The two-global snippet fails at end-of-file because it lacks `mukhya`. The same globals with main compile and print 3. This is not proof that globals are syntactically absent or that the expression class is closed; global initialization is the known checked path. The supplied default-argument example fails at `vitti`, whereas the additional `f(n = 5)` example fails at `=`. See [supplemental results](supplemental/results.json).

Direct local kosh binding remains a valid positive control and prints 7; local kosh arithmetic refuses. v311's scorer incorporates the disclosed v310 harness corrections: valid local binding expects 7 and slice arithmetic accepts the precise E_VIBHAG_ANKA diagnostic. All 12 primary expression observations meet their scoped expectations. This is not a formal class-wide safety proof.
