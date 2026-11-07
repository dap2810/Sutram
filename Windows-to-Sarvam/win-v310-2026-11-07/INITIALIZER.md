# v310 global initializers and syntax probes

Exact compiler/version/hash: [candidate.json](candidate.json). Sources, argv, exit codes, timings, stdout/stderr and output existence: [raw results](expressions/results.json).

## global-direct

Compile exit `1`; executable produced: `False`. Exact compiler output:

```text
Sutram truti [E_KOSH_DVARA]: kosh 'make_kosh(...)' vaishvika-vittau na sthapyate
Sanket: kosh tasya namna eva gacchati - vitti b = k, kosh-tarkah (kosh k), kosh_* prakriyah; mulyani k[i] ityena
```

## global-add

Compile exit `1`; executable produced: `False`. Exact compiler output:

```text
Sutram truti [E_KOSH_GANIT]: kosh-upari ganitam tulana va na sambhavati - kosh sankhya na
Sanket: k[i] tasya mulyam; kosh_gan(k) tasya dirghata - tani tulyantam
```

## valid-global

Compile exit `0`; executable produced: `True`. Exact compiler output:

```text
Siddh: 208 baait sankalit
```

Native output: `7`, exit `0`.

## two-globals-no-main

Compile exit `1`; executable produced: `False`. Exact compiler output:

```text

Sutram truti: vyakaran dosh, pankti 3:1, shabd 'patra-ant'
  
  ^
Sanket: asmin sthane shabdam vyakaranam cha pashyatu.
```

## record-literal

Compile exit `1`; executable produced: `False`. Exact compiler output:

```text

Sutram truti: vyakaran dosh, pankti 1:20, shabd ':'
  rachana Point = { x: 1, y: 2 }
                     ^
Sanket: asmin sthane shabdam vyakaranam cha pashyatu.
```

## default-argument

Compile exit `1`; executable produced: `False`. Exact compiler output:

```text

Sutram truti: vyakaran dosh, pankti 1:12, shabd 'vitti'
  prakriya f(vitti n = 5) { nivartanam n }
             ^
Sanket: asmin sthane shabdam vyakaranam cha pashyatu.
```

## Meaning and controls

Both requested unsafe globals refuse with exit 1 and no executable; the valid global prints 7.
All three literal A2 snippets give syntax errors. However, the two-global snippet fails at end-of-file because it lacks `mukhya`, **not because two globals are forbidden**. Adding `mukhya() { likha(a + b) }` compiles and prints 3. It does not establish a new unchecked path: globals are the path this release now validates. These snippets do not prove class-wide closure.

The supplied default-argument example fails at `vitti`, before the default value. The additional `f(n = 5)` control fails at `=` (exact output in [supplemental results](supplemental/results.json)), directly exercising that syntax.

Local addition of a returned kosh refuses with `E_KOSH_GANIT`. Direct local kosh binding is supported and prints 7; the initial optional probe wrongly expected refusal. Likewise, the initial arithmetic scorer accepted only generic kosh diagnostics and incorrectly marked the valid `E_VIBHAG_ANKA` refusals false. Raw records are unchanged. [Classified verdicts](expressions/classified-verdicts.json) explain these three harness expectation corrections; none is concealed as a product failure or rerun success.
