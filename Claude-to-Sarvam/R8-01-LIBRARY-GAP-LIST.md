# R8-01 — WS1 (Step 5): the library gap list

**Branch `claude/round-08`, commit `dac2c1ef`. Base: main `221eee96` (v183 + ChatGPT's R76 notes).**
No compiler or library source changed. **Environment for every check here: Linux**, unless a line says Wine.

## 1. The gap list

**Short answer to "which of the 303 have no proof":**

- **Before this round:**
  - 1 had none at all: `suchi_vardh`.
  - 1 was called by a proof that never noticed when it was broken: `phal_janchit_nyun`.
  - 7 were reached only through a caller.
- **After this round:** **0 have none.**
  - 295 are caught by a proof that calls them.
  - 8 private helpers are caught through their caller.

**That answer is too generous, so it is not the gap list.** It only says that a function's result reaches a
checked output. I also asked whether the function's **boundaries** are checked. For that I used mutants shaped
like real bugs:

- **R:** an off-by-one result, `prati e` → `prati (e) + 1`
- **C:** a moved boundary, each comparison flipped once (`<`↔`<=`, `>`↔`>=`, `==`↔`!=`)

That gave **1,119 mutants**. Each surviving mutant then got one verdict:

| Verdict | Meaning |
|---|---|
| **GAP** | An input tells it apart, and no proof uses that input |
| **OVERRUN** | A loop runs one pass past the end; the output usually hides it |
| **REVIEW** | It takes a list, string or record and is not decided yet |
| **EQUIVALENT** | No input can tell it apart, by a stated rule or argument |
| **LIKELY-EQ** | No input in the set told it apart |
| **OUT-OF-CONTRACT** | Only inputs the function promises nothing for tell it apart |
| **FINDING** | It exposes a defect in the real function |

**A function is *open* while it has a GAP, OVERRUN, REVIEW or FINDING survivor.**

| module | functions | whole-body mutant caught | open before | **open now** | boundary mutants killed, before → now | open now: GAP / OVERRUN / REVIEW / FINDING |
|---|---|---|---|---|---|---|
| aadhar | 2 | 2 | 2 | **2** | 13 → 13 / 16 | 0 / 2 / 1 / 0 |
| ank | 10 | 10 | 3 | **0** | 26 → 29 / 36 | 0 / 0 / 0 / 0 |
| anukram | 5 | 5 | 4 | **4** | 13 → 13 / 22 | 0 / 3 / 6 / 0 |
| brihat | 12 | 12 | 9 | **9** | 31 → 31 / 52 | 0 / 13 / 7 / 0 |
| chandas | 6 | 6 | 1 | **0** | 16 → 17 / 18 | 0 / 0 / 0 / 0 |
| ganit | 18 | 18 | 2 | **0** | 26 → 28 / 36 | 0 / 0 / 0 / 0 |
| ganita | 22 | 22 | 2 | **0** | 78 → 80 / 114 | 0 / 0 / 0 / 0 |
| gudh | 2 | 2 | 0 | **0** | 3 → 3 / 3 | 0 / 0 / 0 / 0 |
| kalana | 6 | 6 | 5 | **5** | 26 → 26 / 37 | 0 / 1 / 10 / 0 |
| khand | 22 | 22 | 15 | **13** | 75 → 87 / 110 | 0 / 10 / 5 / 0 |
| madhava | 5 | 5 | 0 | **0** | 8 → 8 / 22 | 0 / 0 / 0 / 0 |
| mala | 8 | 8 | 4 | **4** | 12 → 12 / 16 | 0 / 2 / 1 / 1 |
| nighantu | 17 | 17 | 11 | **9** | 42 → 48 / 71 | 1 / 5 / 6 / 0 |
| patra | 3 | 3 | 0 | **0** | 8 → 8 / 13 | 0 / 0 / 0 / 0 |
| phal | 14 | 14 | 8 | **0** | 15 → 24 / 24 | 0 / 0 / 0 / 0 |
| roop | 23 | 23 | 10 | **10** | 72 → 72 / 99 | 0 / 15 / 10 / 0 |
| sadhan | 7 | 7 | 0 | **0** | 13 → 13 / 16 | 0 / 0 / 0 / 0 |
| samanvaya | 10 | 10 | 2 | **2** | 24 → 24 / 27 | 0 / 0 / 2 / 0 |
| sangrah | 14 | 14 | 3 | **3** | 27 → 27 / 34 | 0 / 5 / 2 / 0 |
| sankhyiki | 16 | 16 | 1 | **1** | 34 → 34 / 41 | 0 / 0 / 1 / 0 |
| shreni | 14 | 14 | 11 | **6** | 31 → 36 / 46 | 0 / 2 / 6 / 0 |
| suchi | 34 | 34 | 16 | **11** | 55 → 65 / 83 | 0 / 10 / 4 / 0 |
| vakyank | 6 | 6 | 4 | **2** | 46 → 53 / 57 | 0 / 0 / 4 / 0 |
| varna | 27 | 27 | 21 | **10** | 87 → 111 / 126 | 0 / 6 / 6 / 0 |
| **all** | **303** | **303** | **134** | **91** | **781 → 862 / 1119** | |

**The number for release:**

- **212 of 303 functions are closed.** Every boundary mutant is killed, or the survivors are shown to be
  equivalent or outside the contract.
- **91 are open.**
- **This round closed 43.**

### The 91 open functions, by module, most-used first

- **aadhar** (2):
  - `brihat_ank_tak`, `brihat_ank_se`
- **anukram** (4):
  - `anukram_khip_i64`, `anukram_grah_i64`, `anukram_khip_ashtak`, `anukram_grah_ashtak`
- **brihat** (9):
  - `brihat_ank_se_int`, `brihat_asti_shunyank`, `brihat_shunyank`
  - `brihat_gun`, `brihat_bhajshesh`, `brihat_ghatmod`
  - `brihat_pratilip`, `brihat_nyun`, `brihat_shesh`
- **kalana** (5):
  - `pravan`, `kalana_trapiz`, `simpson`, `pravan2`, `bahu_mula`
- **khand** (13):
  - `khand_bandh`, `khand_mukt`, `khand_pratilip`, `khand_bhed`, `khand_anwesh_akshar`
  - `khand_asti_sarv_ank`, `khand_pratisthap`, `khand_yuj`, `khand_viparyay`
  - `khand_unnat`, `khand_gan_akshar`, `khand_ant`, `khand_avanat`
- **mala** (4):
  - `mala_nava` (finding F2), `mala_grah_surakshit`, `mala_purn`, `mala_pratilip`
- **nighantu** (9):
  - `nighantu_anwesh`, `nighantu_vardh`
  - `nighantu_apanay`: the one GAP; the wrap-around case below
  - `nighantu_rikta`, `nighantu_grah_mool`, `nighantu_kunji_gudh`
  - `nighantu_koshtha_likh`, `nighantu_mulya`, `nighantu_kunjika`
- **roop** (10):
  - `roop_ank_aadhar`, `roop_ank_dhvaj`, `roop_pad_vam`, `roop_chinhit`, `roop_sign_akshar`
  - `roop_ank`, `roop_pad_dakshin`, `roop_pad_madhya`, `roop_varg_mool`, `roop_sthir_mool`
- **samanvaya** (2):
  - `rekha_manak`, `sadish_yoga`
- **sangrah** (3):
  - `rakh_tak_mala`, `rakh_sampat`, `rakh_rikta`
- **sankhyiki** (1):
  - `purna_vyapti`
- **shreni** (6):
  - `dwi_anwesh`, `budbud_shreni`, `viparyay_mala`, `shankh_shreni`, `mil_shreni_punar`, `nivesh_shreni`
- **suchi** (11):
  - `avali_pravesh`, `suchi_apanay`, `avali_antah`, `suchi_vardh`, `suchi_shreni`, `suchi_rikta`
  - `suchi_antah`, `suchi_kramank`, `suchi_viparyay`, `avali_tak_mala`, `avali_rikta`
- **vakyank** (2):
  - `varna_tak_dashm`, `pad_vam`
- **varna** (10):
  - `gan_swar`, `varna_bhed`, `varna_sam`, `varna_antah`, `varna_unnat`
  - `varna_pratisthap`, `varna_chhid`, `varna_viparyay`, `varna_gan`, `varna_avanat`

**Every surviving mutant is listed with its source line, verdict and reason, most-used function first,** in
`evidence-r8/lib-gap-list.md`; the same data is in `.json`.

### What "open" means, and does not

**Most open entries are OVERRUN (74 mutants).**

- A loop such as `yavat (i < n)` that ran once more (`i <= n`) would read or write one cell past the end, and
  every current proof would still pass. That is a real hole in the proofs: they would not notice such a bug.
- **It is not a bug in the library today.**
- The way to close each one is a **guard-cell proof**: put a value in the cell just past the end that would
  change the answer if it were read. `r8_array_guard.sm` and the `nighantu_kunjika_ashtak` case in
  `r8_map_edges.sm` do this.

**The REVIEW mutants (71)** are in functions that take lists, strings or records. The witness tool cannot feed
those yet, and I have not decided them by hand.

**Not padded:**

- **EQUIVALENT (51)**: each is decided by a rule checked on the source line, or by a written argument in
  `tools/lib_gap_reviewed.json`. The rules are:
  - a clamp, `yadi (x > K) { x = K }`
  - an absolute value at zero
  - a min/max tie
- **LIKELY-EQ (56)** is evidence, not proof.
  - It means no input told the mutant apart. The inputs are 332 values for one argument (every byte value
    and the 64-bit edges), and up to 600 tuples otherwise.
  - Most are in `madhava` (fixed-point series), `patra` and the checked arithmetic.
- **OUT-OF-CONTRACT (3)**:
  - `seemit` and `ganit_seemit` with `lo > hi`
  - `kuttaka` with `b = 0`

## 2. Found while proving (not fixed; they need your decision)

### F1 — Silent wrong values in any function with more than 21 variables (severe; compiler; on main)

**The defect:**

- The first 5 variables of a function live in registers. The rest get stack slots at `[rbp-8]`, `[rbp-16]`, ….
- **Every load and store emits the slot with a one-byte displacement** (ModRM `0x45`, disp8): 15 sites,
  among them:
  - `.gs_decl_stack`, `.gs_assign_stack`
  - `.ge_var_stack`, `.ge_index_stack`, `.ge_field_stk`
  - `.elnv_stack`, `.esnv_stack`
  - the `chakra` slots
- So the 17th stack slot, `-136`, is emitted as `+120`. It then lands on the function's saved registers, its
  return address and the caller's stack.
  - `objdump` of the reproducer shows it: `mov %rax,0x78(%rbp)` follows `mov %rax,-0x80(%rbp)`.
- **There is no error.** `VAR_TABLE_CAP` is 256, so the compiler accepts up to 256 variables. Only 21 work.
- The only site with a range check is the add/sub peephole at line 21301.

**The reproducers** (`evidence-r8/probes/F1*`; results in `logs/probes.txt`):

| Probe | Expected | Got |
|---|---|---|
| `F1a`: `chakravala(out, 61)`, then print the caller's `n = 2` | 2 | **1** |
| `F1b`: `1000 + varna_bhed(…)` | 1002 | **5** |
| `F1c`: `mukhya` with 40 variables, print the sum of 1..10 | 55 | **151** |
| `F1d`: a function with 27 locals | the caller's `n = 2` | **26** |
| `F1e`: a function with 31 locals | runs | **segfault** (the return address) |

- **The Windows compiler has the same defect.** `win/sutram.exe` under **Wine 9.0** gives `151` and `26` for
  F1c and F1d (`logs/probes-wine.txt`). **Not run on Windows.**

**The library:**

- **Five functions have more than 21 variables:**
  - `chakravala` (29)
  - `khand_bhed` and `varna_bhed` (25)
  - `varna_tak_dashm` and `roop_sthir_mool` (22)
- **I verified wrong results for `chakravala` and `varna_bhed`.**
- The two 22-variable ones write only to the 17th slot. They are at risk; I did not observe a wrong value.
- **`chakravala` cannot be called from a loop at all:** it corrupts the caller's `out` and the program
  crashes.
- The existing chakravala proofs pass because what they read after the call is not in the overwritten slots.

**The fix:**

- **What:** one helper, used at the 15 sites, that emits disp8 for −128..127 and disp32 (ModRM `0x85`)
  otherwise.
- **Cost:**
  - every committed binary is rebuilt and the locks re-pinned, as in R7
  - a golden per site class
- **Recommendation: make it the first item of the next round.** Measure first: rebuild the tree's programs
  and compare output, as for block scope.

**Why the stopgap is wrong:** a "too many variables" error would stop the 5 library functions compiling.

**Effect on this round's proofs:** I worked around F1 in two of them, and said so in each:

- `r8_chakravala_sweep.sm` and `r8_split_model.sm` call through a one-line wrapper that reads nothing after
  the call.
- When F1 is fixed, the wrappers can go and the expectations stay the same.

### F2 — `nirmmita` reports failure as a negative number, so every "returns 0 on failure" check is dead (Linux)

**The defect:**

- On Linux, `nirmmita(n)` is a raw `mmap`, so a failure returns `-errno`, never 0:
  - `nirmmita(0)` returns `-22`
  - `nirmmita(2^43)` returns `-12`
- The library checks the result for `== 0` in 7 places: 5 functions in `suchi` and `nighantu`, including
  `suchi_srij`, `avali_srij` and `nighantu_srij`. Every other allocation is not checked at all.
- `F2_nirmmita_failure.sm`: `suchi_srij(2^57)` returns a handle **whose data pointer is `-12`**, and the next
  `suchi_khip` segfaults. Its contract says "0 on allocation failure".
- `mala_nava(0)` returns `-22`, which looks like a block.

**The fix:**

- `nirmmita` maps a `-4095..-1` result to 0: one place, about 4 instructions.
- Check what the Windows path returns. **I did not.**

### F3 — `guna (expr)` evaluates `expr` once per `bhavana` tested

**The defect:**

- The `guna` is desugared into an if/else chain that reuses the same expression node.
- `guna (f()) { bhavana 1 … bhavana 3 }` calls `f` **three times** when the third case matches
  (`WS2_c3b_guna_eval.sm`: `calls = 3`).
- It is silent whenever `expr` has a side effect.

**More detail** is in R8-02.

### F4 — the comment on `ganit_seemit` is wrong

- It says "if lo > hi, returns lo".
- The code returns `hi` whenever `v >= lo`: `ganit_seemit(4, 4, -2)` is `-2`.
- **Fix:** change the comment, or the code. Say which.

### F5 — `lib/aadhar.smlib` does not compile on its own

- It calls `brihat_asti_shunyank` and other `brihat` functions **without `yoj brihat`**.
- So `yoj aadhar` alone gives `agyat prakriya: brihat_asti_shunyank`.
- The only proof imports `brihat` itself.
- **Fix:** one line, `yoj brihat`.

### F6 — the committed Linux binaries are not executable

- `sutram_compiler`, `sutram-ide` and `sutram-gui` are mode `100644` in git, on v180 and still on main.
- `tests/run_tests.py` on a fresh clone fails with `Permission denied` until `chmod +x`.
- `gates.sh` hides this, because it rebuilds them.
- **Fix:** `git update-index --chmod=+x`.

## 3. The contracts of the functions that have no direct proof, or no written contract

**The 8 reached only through a caller.** All are private helpers, so a direct proof would test an
implementation detail. Each is detected by its public caller's proofs:

| function | contract | proven through |
|---|---|---|
| `brihat_shesh(num, shesh, res, n)` | `res = num mod shesh` for a 2n-digit `num` | `brihat_ghatmod` |
| `nighantu_koshtha_likh(m, slot, cap, key, keyn, val)` | store key, length and value at `slot`; mark it live | `nighantu_khip` |
| `nighantu_kunji_gudh(key, keyn, cap)` | home bucket: `fnv1a(key) mod cap` | every map operation |
| `nighantu_kunji_sam(m, slot, cap, key, keyn)` | 1 iff the key stored at `slot` equals `key` | `nighantu_anwesh` |
| `roop_sthir_mool(x, places, sign, out)` | \|x\| rounded half away from zero to `places` decimals, as text | `roop_sthir` |
| `roop_varg_mool(src, sn, step, out)` | the integer digits grouped every `step`, as text | `roop_varg` |
| `mil_shreni_punar(a, tmp, lo, hi)` | sort `a[lo..hi]` ascending by merging. **Its comment is `mil_shreni`'s and should move.** | `mil_shreni` |
| `suchi_vardh(l)` | double the capacity and copy the data; 1, or 0 on failure with `l` unchanged | `suchi_khip` (**new:** `r8_list_growth.sm`; before this round nothing noticed if it did nothing) |

**The open functions that have no comment of their own.** The others' comments are in `lib-gap-list.md`.

| function | contract |
|---|---|
| `khand_avanat(src, sn, out)` / `varna_avanat` | A–Z lowered, everything else copied, terminator at `out[sn]`; returns `sn` (`sn < 0`: empty) |
| `khand_ant(src, sn, suf, sn2)` | 1 iff the last `sn2` bytes of `src` equal `suf`; 0 if `sn2 < 0` or `sn2 > sn` |
| `mala_nava(n)` | a block of `n` cells, or 0 if `n * 8` overflows. **(F2: `n = 0` gives -22)** |
| `mala_purn(arr, val, n)` | `arr[0..n-1] = val`; returns 0 |
| `mala_pratilip(dst, src, n)` | copy `n` cells from `src` to `dst`; returns 0 |
| `mala_grah_surakshit(arr, i, n)` | `arr[i]` if `0 <= i < n`, else 0 |
| `budbud_shreni(a, n)`, `shankh_shreni`, `nivesh_shreni` | sort `a[0..n-1]` ascending in place (bubble, Shell, insertion) |
| `viparyay_mala(a, n)` | reverse `a[0..n-1]` in place |
| `dwi_anwesh(a, n, target)` | an index of `target` in ascending `a[0..n-1]`, or -1 |
| `gan_swar(s)` | the number of `a e i o u` bytes in the terminated text `s` |
| `varna_sam(a, b)` | 1 iff the terminated texts `a` and `b` are equal |

## 4. What I proved this round

**14 new programs in `tests/stdlib/r8_*`:**

- **Every expectation was computed independently, in Python.**
  - The scripts are in `evidence-r8/expectations/`.
  - They work from the contracts: plain formulas, a dictionary, a list and a deque, `str.split`, and Pell
    solutions from continued fractions.
- **Every expectation agrees with the compiled run.** The goldens are those expectations.

| Proof | Closes |
|---|---|
| `r8_number_edges` | `kramgun(2)`, `asti_abhajya(4)` (**4 was "prime" under a moved boundary, and no proof noticed**), `ganita_vargmool(2..9)`, `kuttaka` with answer 0, `matra_meru(0)`, `ank_gan(10)`, `viparyay_ank(0)`, `unnat_sanket` / `avanat_sanket` at A, Z, a and z |
| `r8_array_guard` | `laghu`, `adhik`, `yog`, `gan`, `anwesh_sarak` with a guard cell; `n = 0` |
| `r8_text_edges`, `r8_char_class`, `r8_bytes_edges` | case conversion and character classes at each end of each range; empty and full-length prefix and suffix; equal-prefix compare; code 0 is not a character |
| `r8_list_edges`, `r8_list_growth` | bounds at exactly the length with a stale value past it; growth from capacity 1 over a page (catches a `suchi_vardh` that does nothing) |
| `r8_map_edges` | the empty key; `nighantu_kunjika_ashtak` does not write past the last key |
| `r8_result_flags` | the return flag of every `phal` function: **all 8 return values were unchecked** |
| `r8_base_digits` | hex digits a/f/A/F/G; base 36; `9223372036854775807` parses, `…808` overflows |
| `r8_chakravala_sweep` | **every non-square n from 2 to 99** against the least Pell solution (through a wrapper, F1) |
| `r8_map_model` | 600 random insert/delete/get on capacity 7 against a dictionary: full table, wrap-around, backward-shift delete |
| `r8_list_model` | 500 list operations and 500 queue operations from capacity 1 against a list and a deque |
| `r8_split_model` | 300 random splits for `varna_bhed` and `khand_bhed` against `str.split` (through a wrapper, F1) |

**Not proven, and why:**

- **`nighantu_apanay` C12**, the one open GAP. Deleting from a probe chain that wraps past the last slot, when
  slot 0 holds a one-byte key. It needs keys chosen by their hash. Next round.
- **The 74 OVERRUN and 71 REVIEW mutants.** They are listed, with lines.
  - They need guard-cell or model proofs like the ones above.
  - **About two rounds at this round's rate.**

## 5. The tools (on the branch)

| Tool | What it does |
|---|---|
| `tools/lib_proof_gaps.py [--deep]` | The whole-body mutant, plus R and C with `--deep`. It probes with the imports a module needs (F5) and skips mutants that do not compile. About 90 s on 2 cores. |
| `tools/lib_mutant_witness.py` | Runs a survivor beside the real function on the same inputs and prints the first input that differs. It finds which parameters are lists or strings, including through calls, and drops results that are not stable (addresses). |
| `tools/lib_gap_report.py` | Turns both into the module-by-module list. |
| `tools/lib_gap_reviewed.json` | 32 hand verdicts, each with its argument. Re-check one if its source line changes. |

```
python3 tools/lib_proof_gaps.py --deep --json build/g.json
python3 tools/lib_mutant_witness.py --gaps build/g.json --json build/w.json
python3 tools/lib_gap_report.py --gaps build/g.json --witness build/w.json --md build/lib-gap-list.md
```

**Before and after are the same tools with the same verdicts.** "Before" is main's proofs
(`evidence-r8/lib-gap-list-before.md`).

## 6. Gates (branch, Linux)

| Check | Result |
|---|---|
| `proof_lib` | **205 / 205** (191 + 14) |
| `proof_props` | 86 / 86 |
| suite (`tests/run_tests.py`) | **PASS 203 / NO-EXPECTATION 4**, unchanged; `chmod +x` first (F6) |
| `gates.sh` | **PASS 9 / FAIL 1 / NOT-RUN 1**. The FAIL is X11 `edscroll`, the same pre-existing timeout in my container. NOT-RUN is Windows. |
| F1 under Wine | as in the table above |
| **Windows** | **NOT-RUN** |

**Logs:** `evidence-r8/logs/`.
