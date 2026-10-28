# Round 125 — dictionary evidence and lexical method

**Scope:** Read-side Sanskrit vocabulary audit requested in `Sarvam-to-ChatGPT/ROUND-125.md`. The 228-row verdict is in `ROUND-125-VOCAB-VERDICT.tsv`. **This is not formal Sanskritist certification.** Dictionary citations below establish important lexical distinctions; other rows use the stated Sanskrit roots, nominal forms and transparent compound-member analyses rather than a claim that every entire snake_case identifier is independently attested.

## Evaluation method — what Y and N actually mean

- **Y:** Sanskrit dictionary headword, attested verbal root, or a transparent technical compound made of recognizable Sanskrit components; **not** a guarantee that the exact compounded programming identifier occurs in a Sanskrit lexicon.
- **N:** name is English/Hindi or contains an unverified/clipped element **as written**; a conservative "not independently established", never a rigorous proof that a word does not exist in all Sanskrit literature.
- **PASS/FAIL:** does the dictionary sense accurately describe the **actual routine** (read source body, not a previous proposed English label)? Genuine words can FAIL. Technical proper names `fnv1a` and `simpson` can be N for Sanskrit but PASS for reproducible algorithm identification.
- **better_word:** preference, not approved API change; for the owner's established `prati` decision, maintain it.

## Dictionary receipts (source-backed senses; each link is a lexical source)

| ID | Headword/s | Dictionary evidence | Relevance |
|---|---|---|---|
| D01 | `karna` / कर्ण | [Kosha dictionary: diagonal](https://kosha.sanskrit.today/word/en/diagonal) lists `karṇa` as hypotenuse/diagonal | `karna_yog` is accurate: `lib/samanvaya.smlib:110-118` sums `a[i*n+i]` |
| D02 | `tadatmya` / तादात्म्य | [Monier-Williams (तादात्म्य)](https://sanskrit.uohyd.ac.in/SKT/MW/107.html) defines identity/sameness of *nature or character* | Real noun but not a precise identity-*matrix* label; `ekatva` is also abstract |
| D03 | `chay` / चय | [Kosha MW, Apte etc.](https://kosha.sanskrit.today/word/sa/%E0%A4%9A%E0%A4%AF) attests heap, pile, collection | The existing `chay_*` stack-family prefix **is real Sanskrit**, contrary to the draft |
| D04 | `chiti` / चिति | [Kosha MW, Apte etc.](https://kosha.sanskrit.today/word/sa/citi) attests pile, heap, stack and pyre | Proposed `chiti_*` is real too, but not uniquely better than `chay_*` |
| D05 | `kshamata` / क्षमता | [Kosha capacity entry](https://kosha.sanskrit.today/word/en/capacity) gives ability/capacity | `kosh_kshamata` is apt; bare root `ksham` means able/tolerate, not amount of unused room |
| D06 | `ganita` / गणित | [Kosha MW गणित](https://kosha.sanskrit.today/word/sa/%E0%A4%97%E0%A4%A3%E0%A4%BF%E0%A4%A4) attests reckoning/computation/mathematics | Full form real; `ganit` is clipped project transliteration |
| D07 | `ganan` / गणन | [Kosha counting](https://kosha.sanskrit.today/word/en/counting) and [Apte/MW evidence](https://akshara.ru/kosha/w/gaRana) give counting **and calculation** | A valid replacement candidate for plain arithmetic, not automatically a semantic FAIL |
| D08 | `kotijya` / कोटिज्या | [Kosha dictionary](https://kosha.sanskrit.today/word/sa/koTijyA) explicitly gives cosine | Historically genuine technical term, not an ad hoc coinage |
| D09 | `jya` / ज्या | [Mathematical Association of America](https://old.maa.org/node/2702736) documents Indian Sanskrit sine work, and [historical overview](https://graphsearch.epfl.ch/en/concept/26397073) traces `jyā` and `koṭi-jyā` | Historical sine/cosine terminology genuine; **does not** establish `chapsparsh` for arctangent |
| D10 | `samalamb` / समलम्ब | [Kosha](https://kosha.sanskrit.today/word/sa/%E0%A4%B8%E0%A4%AE%E0%A4%B2%E0%A4%AE%E0%A5%8D%E0%A4%AC) attests trapezoid | Correct shape for `kalana_trapiz`, which adds trapezoid areas in source |
| D11 | `ashtak` / अष्टक | [Monier-Williams via Sanskrit dictionary](https://app.sanskritdictionary.in/shabdkosh?search=%E0%A4%85%E0%A4%B7%E0%A5%8D%E0%A4%9F%E0%A4%95) says set of eight/consisting of eight | Both `asht` (eight) and `ashtak` (group of eight) are genuine, but the serializer emits **an 8-byte length followed by n arbitrary bytes** |
| D12 | `nivartan` / निवर्तन | [Kosha related derivation](https://kosha.sanskrit.today/word/sa/%E0%A4%A8%E0%A4%BF%E0%A4%B5%E0%A4%B0%E0%A5%8D%E0%A4%A4%E0%A4%BF%E0%A4%A8%E0%A5%8D) records `nivartana` as turning back; [ni-vṛt](https://kosha.sanskrit.today/word/sa/%E0%A4%A8%E0%A4%BF%E0%A4%B5%E0%A4%B0%E0%A5%8D%E0%A4%A4%E0%A4%A4%E0%A5%87) means return | Valid noun for return; **r is essential**, from √वृत्; this is a *different option*, not a recommendation to reverse the owner's `prati` decision |

### Crucial function-body observations (not dictionary opinion)

- `pehchan(n, out)` in `lib/samanvaya.smlib:31-46` fills diagonal 1, elsewhere 0: **identity matrix**, not recognition.
- `nishan(a,n)` at `:110-118` sums diagonal entries: **trace**, not a marker.
- `samanvaya_akar_na(m,n,len)` at `:20-29` returns **1 for invalid/non-fitting shape**; `samanvaya_akar` removes necessary negative sense.
- `skalar` at `:78-88` multiplies every element of a matrix by c: **scalar multiplication**, not a single digit.
- `kalana_trapiz` at `lib/kalana.smlib:17-30` computes composite trapezoid areas; `simpson` at `:32-52` uses Simpson's 1/3 weights; replacing Simpson with just "parabola" hides rule and historical method.
- `pravan2` at `lib/kalana.smlib:78-95` computes **second derivative**, not "second slope".
- `anukram_khip_ashtak` at `lib/anukram.smlib:85-105` writes an **8-byte length prefix and n payload bytes**; it does not always write an 8-byte payload.
- `bit_gan` at `lib/ganit.smlib:129-138` counts **set bits**; `ansh_gan` is too general.
- `util_chinha` at `lib/sadhan.smlib:40-41` returns `(n>0)-(n<0)`: mathematical **signum**, not general utility sign.
- `gun_tray(a,b,c)` at `examples/05_func_params.sm:5-6` multiplies **three parameters**; it does **not** triple one parameter.

## Important limitations

Not every one of the 228 TSV entries has an independently fetched dictionary page. The table is a full **lexical review with explicit Sanskrit morphology and source-body tests for disputed functions**, not a 228-query corpus-certified dictionary harvest. Preserve this distinction in any release. Native compiler checks: **NOT RUN - no toolchain**; no signatures or APIs changed. Frozen packs, source and backups left untouched.
