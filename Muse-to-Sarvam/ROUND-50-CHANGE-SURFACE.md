# ROUND-50 — change surface (exact file and line list)

Base: origin/main at 0f82b257 (v390; ROUND-50 issued in e0448ae7, compiler v254).
Scope: code files only — examples/**/*.sm, tests/**/*.sm (live tests), lib/*.smlib, src/*.asm, src/*.inc.
Counts in the TSV are LIVE sites. Files under tests/negative/ are frozen historical
test inputs and are NOT to be renamed; their counts are given per rename as DO-NOT-TOUCH.
Comment-only lines are excluded from the lists below; they do not affect compilation,
but a rename that leaves a comment naming the old function will leave stale documentation.
For builtins, the compiler table line in src/sutram_compiler.asm is itself a site:
changing only call sites without the bn_* string leaves the old name working and the
new name unknown. For kosh_* renames, also change the error-message strings at
src/sutram_compiler.asm:373-375 (kosh_pop, kosh_peek, kosh_dequeue) and :377 (kosh_push),
or tests expecting those error texts will fail and users will see old names in errors.

## likh -> likha (keyword/builtin merge - REJECT as rename, see notes)
Live sites: 10. DO-NOT-TOUCH in tests/negative/: 1.
- src/r71_unsafe_tokens.inc:128 — cmp rax,1                  ; likh
- src/sutram_compiler.asm:258 — db 2,2               ; 1 likh
- src/sutram_compiler.asm:737 — bn_likh      db "likh", 0
- src/sutram_compiler.asm:11548 — ; or machine-code emission, including special sthagita/likh nodes.
- src/sutram_compiler.asm:11633 — ; Previous code read call_args and could crash the compiler for likh().
- tests/r52_check/likh_missing_value.sm:2 — likh(5)
- tests/r52_check/likh_no_args.sm:2 — likh()
- tests/r52_check/likh_valid.sm:3 — likh(b, 300)
- tests/r52_check/likh_valid.sm:5 — likh(b + 8, 66)
- tests/r54_check/raw_valid.sm:7 — likh(b + 8, 66)

## shabda -> likha (keyword/builtin merge - REJECT as rename, see notes)
Live sites: 8. DO-NOT-TOUCH in tests/negative/: 1.
- examples/44_shabda.sm:9 — shabda(greeting)
- examples/44_shabda.sm:12 — shabda(msg)
- examples/44_shabda.sm:14 — shabda("and literals work directly")
- examples/46_language_reference.sm:33 — shabda(s)                       # print a varna variable
- src/sutram_compiler.asm:213 — BN_SHABDA   equ 35   ; shabda = print a NUL-terminated string (variable)
- src/sutram_compiler.asm:292 — db 1,1               ; 35 shabda
- src/sutram_compiler.asm:784 — bn_shabda    db "shabda", 0
- src/sutram_compiler.asm:16150 — ; shabda(s): print the NUL-terminated string whose address is in s

## paadh -> REMOVE (keyword/builtin removal - REJECT, see notes)
Live sites: 4. DO-NOT-TOUCH in tests/negative/: 0.
- lib/patra.smlib:39 — vitti n = paadh(fd, dst + total, c - total)
- src/sutram_compiler.asm:263 — db 3,3               ; 6 paadh
- src/sutram_compiler.asm:741 — bn_paadh     db "paadh", 0
- src/sutram_compiler.asm:16050 — ; paadh(fd, buf, count) -> bytes_read (sys_read=0)

## vartani_cat -> vartani_yuj (builtin)
Live sites: 4. DO-NOT-TOUCH in tests/negative/: 0.
- src/sutram_compiler.asm:275 — db 2,2               ; 18 vartani_cat
- src/sutram_compiler.asm:756 — bn_vartcat   db "vartani_cat", 0
- src/sutram_compiler.asm:17188 — ; vartani_cat(dst, src) → strcat, returns dst
- tests/r54_check/raw_valid.sm:20 — vartani_cat(b + 48, "!")

## pankti_len -> mala_aayam (builtin)
Live sites: 23. DO-NOT-TOUCH in tests/negative/: 0.
- examples/246_r23_comparator_sort.sm:26 — vitti n = pankti_len(s)
- examples/246_r23_comparator_sort.sm:50 — chakra i = 0 tak pankti_len(s) - 1 {
- examples/248_r23_slices.sm:8 — chakra i = 0 tak pankti_len(s) - 1 {
- examples/248_r23_slices.sm:15 — chakra i = 0 tak pankti_len(s) - 1 {
- examples/248_r23_slices.sm:23 — vitti n = pankti_len(s)
- examples/248_r23_slices.sm:42 — likha(pankti_len(madhya))
- examples/248_r23_slices.sm:55 — likha(pankti_len(a[4:4]))
- examples/249_r25_phal.sm:16 — yadi (i < 0 || i >= pankti_len(s)) {
- examples/249_r25_phal.sm:31 — vitti n = pankti_len(s)
- examples/254_r42_alias_pankti_len.sm:12 — likha(pankti_len(b))
- examples/67_array_len_bounds.sm:6 — likha(pankti_len(a))
- examples/72_array_variable_index.sm:6 — likha(pankti_len(a))
- examples/74_array_highest_valid.sm:5 — likha(pankti_len(a))
- examples/75_array_dynamic_length.sm:5 — likha(pankti_len(a))
- examples/76_array_function_scope.sm:4 — prati pankti_len(a) + a[1]
- examples/76_array_function_scope.sm:10 — prati pankti_len(a) + a[3]
- examples/90_b9_short_circuit_bounds.sm:6 — likha(i < pankti_len(a) && a[i] > 0)
- examples/90_b9_short_circuit_bounds.sm:7 — likha(i >= pankti_len(a) || a[i] > 0)
- src/sutram_compiler.asm:214 — BN_PANKTILEN equ 36   ; pankti_len = array length for declared arrays
- src/sutram_compiler.asm:293 — db 1,1               ; 36 pankti_len
- src/sutram_compiler.asm:764 — bn_panktilen db "pankti_len", 0
- src/sutram_compiler.asm:16992 — ; Preserve historical behavior for arbitrary/raw pointers: pankti_len(p)
- src/sutram_compiler.asm:16995 — call r23_expr_is_slice    ; R23 WS3: pankti_len(s), pankti_len(a[lo:hi]): the slice's length

## sankhya_dot -> sankhya_bindu (builtin)
Live sites: 3. DO-NOT-TOUCH in tests/negative/: 0.
- src/sutram_compiler.asm:278 — db 2,2               ; 21 sankhya_dot
- src/sutram_compiler.asm:759 — bn_vecdot    db "sankhya_dot", 0
- src/sutram_compiler.asm:17412 — ; sankhya_dot(src1, src2) — dot product via dpps

## likha_fmt -> likha_roop (builtin)
Live sites: 8. DO-NOT-TOUCH in tests/negative/: 0.
- examples/format_demo.sm:5 — likha_fmt("x = ", x)
- examples/format_demo.sm:7 — likha_fmt("y = ", y)
- examples/format_demo.sm:9 — likha_fmt("Sum = ", x + y)
- examples/full_demo.sm:32 — likha_fmt("x=", 42)
- examples/multable.sm:7 — likha_fmt("", i * j)
- src/sutram_compiler.asm:279 — db 2,2               ; 22 likha_fmt
- src/sutram_compiler.asm:760 — bn_lkfmt     db "likha_fmt", 0
- src/sutram_compiler.asm:17949 — ; likha_fmt(fmt, arg1) — simple format: prints fmt string,

## kosh_push -> kosh_khip (builtin)
Live sites: 343. DO-NOT-TOUCH in tests/negative/: 89.
- examples/100_t18_kosh_bounds.sm:4 — kosh_push(a, 42)
- examples/100_t18_kosh_devanagari.sm:6 — kosh_push(b, 7)
- examples/109_t18_kosh_dasham.sm:5 — likha(kosh_push(a, 1.5))
- examples/109_t18_kosh_dasham.sm:6 — likha(kosh_push(a, 2))
- examples/110_t18_kosh_dasham_devanagari.sm:4 — kosh_push(b, 0.5)
- examples/111_t18_kosh_dasham_function_return.sm:4 — kosh_push(values, 2.5)
- examples/111_t18_kosh_dasham_function_return.sm:10 — kosh_push(values, 1.25)
- examples/112_t18_kosh_integer_conversion.sm:4 — kosh_push(a, 2.9)
- examples/118_t18_kosh_param.sm:14 — kosh_push(values, 1.5)
- examples/118_t18_kosh_param.sm:15 — kosh_push(values, 2.5)
- examples/118_t18_kosh_param.sm:16 — kosh_push(values, 2.0)
- examples/118_t18_kosh_param.sm:21 — kosh_push(nums, 3)
- examples/118_t18_kosh_param.sm:22 — kosh_push(nums, 7)
- examples/119_t18_kosh_param_forward.sm:17 — kosh_push(values, 1.25)
- examples/119_t18_kosh_param_forward.sm:18 — kosh_push(values, 2.75)
- examples/120_t18_kosh_param_mismatch.sm:8 — kosh_push(raw, 7)
- examples/121_t18_kosh_param_push_reject.sm:4 — kosh_push(a, 1.0)
- examples/122_t18_kosh_param_devanagari.sm:8 — kosh_push(values, 2.25)
- examples/123_t18_kosh_param_statement_call.sm:8 — kosh_push(values, 1.5)
- examples/126_numeric_pipeline.sm:13 — kosh_push(values, 2)
- examples/126_numeric_pipeline.sm:14 — kosh_push(values, 4)
- examples/126_numeric_pipeline.sm:15 — kosh_push(values, 4)
- examples/126_numeric_pipeline.sm:16 — kosh_push(values, 4)
- examples/126_numeric_pipeline.sm:17 — kosh_push(values, 5)
- examples/126_numeric_pipeline.sm:18 — kosh_push(values, 5)
- examples/126_numeric_pipeline.sm:19 — kosh_push(values, 7)
- examples/126_numeric_pipeline.sm:20 — kosh_push(values, 9)
- examples/126_numeric_pipeline.sm:23 — kosh_push(u, 3)
- examples/126_numeric_pipeline.sm:24 — kosh_push(u, 4)
- examples/126_numeric_pipeline.sm:26 — kosh_push(v, 1)
- examples/126_numeric_pipeline.sm:27 — kosh_push(v, 2)
- examples/134_perf_float_complex_fallback.sm:8 — kosh_push(data, 3.0)
- examples/134_perf_float_complex_fallback.sm:9 — kosh_push(data, 8.0)
- examples/135_r30_float_index_scalar.sm:8 — kosh_push(xs, 2.0)
- examples/135_r30_float_index_scalar.sm:9 — kosh_push(xs, 4.0)
- examples/136_r30_float_complex_left.sm:7 — kosh_push(data, 4.0)
- examples/136_r30_float_complex_left.sm:8 — kosh_push(data, 6.0)
- examples/137_r30_float_literal_rhs.sm:7 — kosh_push(values, 3.0)
- examples/137_r30_float_literal_rhs.sm:8 — kosh_push(values, 5.0)
- examples/138_r30_float_comparison_index.sm:5 — kosh_push(data, 3.0)
- examples/138_r30_float_comparison_index.sm:6 — kosh_push(data, 9.0)
- examples/139_r30_float_mixed_fallback.sm:4 — kosh_push(v, 7.0)
- examples/140_r30_index_side_effect.sm:11 — kosh_push(arr, 2.0)
- examples/144_xmm_cache_fallback.sm:9 — kosh_push(xs, 2.5)
- examples/148_stage2_array_mutation_call.sm:9 — kosh_push(xs, 2.0)
- examples/203_meru_with_kosh.sm:11 — kosh_push(row, meru(n, i))
- examples/205_madhava_pi_kosh.sm:10 — kosh_push(terms, util_chinha / denom)
- examples/206_sankhyiki.sm:8 — kosh_push(xs, 2)
- examples/206_sankhyiki.sm:9 — kosh_push(xs, 4)
- examples/206_sankhyiki.sm:10 — kosh_push(xs, 4)
- examples/206_sankhyiki.sm:11 — kosh_push(xs, 4)
- examples/206_sankhyiki.sm:12 — kosh_push(xs, 5)
- examples/206_sankhyiki.sm:13 — kosh_push(xs, 5)
- examples/206_sankhyiki.sm:14 — kosh_push(xs, 7)
- examples/206_sankhyiki.sm:15 — kosh_push(xs, 9)
- examples/207_sankhyiki_vector.sm:9 — kosh_push(a, 3)
- examples/207_sankhyiki_vector.sm:10 — kosh_push(a, 4)
- examples/207_sankhyiki_vector.sm:13 — kosh_push(b, 1)
- examples/207_sankhyiki_vector.sm:14 — kosh_push(b, 2)
- examples/207_sankhyiki_vector.sm:20 — kosh_push(c, 1)
- examples/207_sankhyiki_vector.sm:21 — kosh_push(c, 1)
- examples/207_sankhyiki_vector.sm:22 — kosh_push(c, 1)
- examples/208_kalana.sm:16 — kosh_push(xs, x)
- examples/208_kalana.sm:17 — kosh_push(ys, x * x)
- examples/208_kalana.sm:31 — kosh_push(c, -2.0)
- examples/208_kalana.sm:32 — kosh_push(c, 0.0)
- examples/208_kalana.sm:33 — kosh_push(c, 1.0)
- examples/208_kalana.sm:38 — kosh_push(ok, 0.0)
- examples/209_samanvaya.sm:10 — kosh_push(a, 1.0)
- examples/209_samanvaya.sm:11 — kosh_push(a, 2.0)
- examples/209_samanvaya.sm:12 — kosh_push(a, 3.0)
- examples/209_samanvaya.sm:13 — kosh_push(a, 4.0)
- examples/209_samanvaya.sm:16 — kosh_push(b, 5.0)
- examples/209_samanvaya.sm:17 — kosh_push(b, 6.0)
- examples/209_samanvaya.sm:18 — kosh_push(b, 7.0)
- examples/209_samanvaya.sm:19 — kosh_push(b, 8.0)
- examples/209_samanvaya.sm:23 — yavat (z < 4) { kosh_push(c, 0.0); z = z + 1 }
- examples/209_samanvaya.sm:35 — kosh_push(d, 6.0)
- examples/209_samanvaya.sm:36 — kosh_push(d, 1.0)
- examples/209_samanvaya.sm:37 — kosh_push(d, 1.0)
- examples/209_samanvaya.sm:38 — kosh_push(d, 4.0)
- examples/209_samanvaya.sm:39 — kosh_push(d, -2.0)
- examples/209_samanvaya.sm:40 — kosh_push(d, 5.0)
- examples/209_samanvaya.sm:41 — kosh_push(d, 2.0)
- examples/209_samanvaya.sm:42 — kosh_push(d, 8.0)
- examples/209_samanvaya.sm:43 — kosh_push(d, 7.0)
- examples/209_samanvaya.sm:48 — yavat (w < 9) { kosh_push(id, 0.0); w = w + 1 }
- examples/209_samanvaya.sm:53 — kosh_push(e, 1.0)
- examples/209_samanvaya.sm:54 — kosh_push(e, 2.0)
- examples/209_samanvaya.sm:55 — kosh_push(e, 3.0)
- examples/209_samanvaya.sm:56 — kosh_push(e, 4.0)
- examples/209_samanvaya.sm:57 — kosh_push(e, 5.0)
- examples/209_samanvaya.sm:58 — kosh_push(e, 6.0)
- examples/209_samanvaya.sm:61 — yavat (y < 6) { kosh_push(t, 0.0); y = y + 1 }
- examples/237_many_variables.sm:66 — kosh_push(k, 9)
- examples/237_many_variables.sm:67 — kosh_push(k, 11)
- examples/248_r23_slices.sm:51 — kosh_push(k, 10)
- examples/248_r23_slices.sm:52 — kosh_push(k, 20)
- examples/248_r23_slices.sm:53 — kosh_push(k, 30)
- examples/252_r38_alias_kosh_oob.sm:4 — kosh_push(v, 1.5)
- examples/252_r38_alias_kosh_oob.sm:5 — kosh_push(v, 2.5)
- examples/255_r42_alias_kosh_push.sm:5 — kosh_push(v, 3)
- examples/255_r42_alias_kosh_push.sm:8 — kosh_push(w, 4)
- examples/257_r48_kosh_empty.sm:8 — kosh_push(v, 7)
- examples/96_t18_kosh.sm:6 — likha(kosh_push(a, 10))
- examples/96_t18_kosh.sm:7 — likha(kosh_push(a, 20))
- examples/96_t18_kosh.sm:9 — likha(kosh_push(a, 30))
- examples/97_t18_kosh_devanagari.sm:6 — kosh_push(b, 7)
- examples/99_t18_kosh.sm:6 — likha(kosh_push(a, 10))
- examples/99_t18_kosh.sm:7 — likha(kosh_push(a, 20))
- examples/99_t18_kosh.sm:9 — likha(kosh_push(a, 30))
- src/r11_sandesh.inc:1730 — r11_bengali_50 db "Sutram Error: ",224,166,149,224,167,139,224,166,182," ",224,166,175,224,167,129,2
- src/r11_sandesh.inc:2004 — r11_hindi_50 db "Sutram Error: ",224,164,149,224,165,139,224,164,182," ",224,164,164,224,164,176,224
- src/r11_sandesh.inc:2141 — r11_kannada_50 db "Sutram Error: ",224,178,149,224,179,139,224,178,182," ",224,178,170,224,179,141,2
- src/r11_sandesh.inc:2278 — r11_malayalam_50 db "Sutram Error: ",224,180,149,224,181,139,224,180,182," ",224,180,170,224,181,141
- src/r11_sandesh.inc:2415 — r11_marathi_50 db "Sutram Error: ",224,164,149,224,165,139,224,164,182," ",224,164,175,224,165,129,2
- src/r11_sandesh.inc:2552 — r11_odia_50 db "Sutram Error: ",224,172,149,224,173,139,224,172,182," ",224,172,175,224,173,129,224,
- src/r11_sandesh.inc:2689 — r11_punjabi_50 db "Sutram Error: ",224,168,149,224,169,139,224,168,184,224,168,188," ",224,168,164,2
- src/r11_sandesh.inc:2826 — r11_tamil_50 db "Sutram Error: ",224,174,149,224,175,139,224,174,154," ",224,174,133,224,174,179,224
- src/r11_sandesh.inc:2963 — r11_telugu_50 db "Sutram Error: ",224,176,149,224,177,139,224,176,182," ",224,176,170,224,177,141,22
- src/sutram_compiler.asm:215 — BN_KOSHPUSH equ 37   ; kosh_push(k, value) -> new length
- src/sutram_compiler.asm:294 — db 2,2               ; 37 kosh_push
- src/sutram_compiler.asm:377 — msg_kosh_param_push db "Sutram Error: kosh-tarke kosh_push asamarthitam", 10, 0
- src/sutram_compiler.asm:765 — bn_koshpush db "kosh_push", 0
- src/sutram_compiler.asm:772 — bn_koshenqueue db "kosh_enqueue", 0  ; FIFO append = kosh_push
- src/sutram_compiler.asm:15613 — ; callee's pointer without updating the caller, so kosh_push is rejected on
- tests/r33/kinds.sm:9 — kosh_push(xs, 10)
- tests/r33/kinds.sm:10 — kosh_push(xs, 20)
- tests/r33/kinds.sm:11 — kosh_push(xs, 30)
- tests/r33/kinds.sm:17 — kosh_push(ys, 0.25)
- tests/r33/kinds.sm:18 — kosh_push(ys, 0.5)
- tests/r35/winffi.sm:26 — kosh_push(xs, 10)
- tests/r35/winffi.sm:27 — kosh_push(xs, 20)
- tests/r35/winffi.sm:28 — kosh_push(xs, 30)
- tests/r35/winffi.sm:34 — kosh_push(ys, 0.25)
- tests/r35/winffi.sm:35 — kosh_push(ys, 0.5)
- tests/r63_check/kosh_native_core.sm:10 — likha(kosh_push(a, 20))
- tests/r63_check/kosh_native_float.sm:12 — likha(kosh_push(v, 2.25))
- tests/r64_check/kosh_nonempty.sm:4 — likha(kosh_push(k, 10))
- tests/r64_check/kosh_nonempty.sm:5 — likha(kosh_push(k, 20))
- tests/stdlib/kalana_bahu_ganana.sm:4 — kosh_push(c, 1.0)
- tests/stdlib/kalana_bahu_ganana.sm:5 — kosh_push(c, 2.0)
- tests/stdlib/kalana_bahu_ganana.sm:6 — kosh_push(c, 1.0)
- tests/stdlib/kalana_bahu_mula.sm:4 — kosh_push(c, -2.0)
- tests/stdlib/kalana_bahu_mula.sm:5 — kosh_push(c, 0.0)
- tests/stdlib/kalana_bahu_mula.sm:6 — kosh_push(c, 1.0)
- tests/stdlib/kalana_bahu_mula.sm:8 — kosh_push(ok, 0.0)
- tests/stdlib/kalana_bahu_mula.sm:14 — kosh_push(c2, 1.0)
- tests/stdlib/kalana_bahu_mula.sm:15 — kosh_push(c2, 1.0)
- tests/stdlib/kalana_bahu_mula.sm:17 — kosh_push(ok2, 0.0)
- tests/stdlib/kalana_simpson.sm:5 — kosh_push(xs, 0.0)
- tests/stdlib/kalana_simpson.sm:6 — kosh_push(xs, 1.0)
- tests/stdlib/kalana_simpson.sm:7 — kosh_push(xs, 2.0)
- tests/stdlib/kalana_simpson.sm:8 — kosh_push(ys, 0.0)
- tests/stdlib/kalana_simpson.sm:9 — kosh_push(ys, 1.0)
- tests/stdlib/kalana_simpson.sm:10 — kosh_push(ys, 4.0)
- tests/stdlib/kalana_simpson.sm:15 — kosh_push(xs2, 0.0)
- tests/stdlib/kalana_simpson.sm:16 — kosh_push(xs2, 1.0)
- tests/stdlib/kalana_simpson.sm:17 — kosh_push(xs2, 2.0)
- tests/stdlib/kalana_simpson.sm:18 — kosh_push(xs2, 3.0)
- tests/stdlib/kalana_simpson.sm:19 — kosh_push(xs2, 4.0)
- tests/stdlib/kalana_simpson.sm:20 — kosh_push(ys2, 0.0)
- tests/stdlib/kalana_simpson.sm:21 — kosh_push(ys2, 1.0)
- tests/stdlib/kalana_simpson.sm:22 — kosh_push(ys2, 8.0)
- tests/stdlib/kalana_simpson.sm:23 — kosh_push(ys2, 27.0)
- tests/stdlib/kalana_simpson.sm:24 — kosh_push(ys2, 64.0)
- tests/stdlib/kalana_slope.sm:5 — kosh_push(xs, 0.0)
- tests/stdlib/kalana_slope.sm:6 — kosh_push(xs, 1.0)
- tests/stdlib/kalana_slope.sm:7 — kosh_push(xs, 2.0)
- tests/stdlib/kalana_slope.sm:8 — kosh_push(ys, 0.0)
- tests/stdlib/kalana_slope.sm:9 — kosh_push(ys, 1.0)
- tests/stdlib/kalana_slope.sm:10 — kosh_push(ys, 4.0)
- tests/stdlib/kalana_slope2.sm:5 — kosh_push(xs, 0.0)
- tests/stdlib/kalana_slope2.sm:6 — kosh_push(xs, 1.0)
- tests/stdlib/kalana_slope2.sm:7 — kosh_push(xs, 2.0)
- tests/stdlib/kalana_slope2.sm:8 — kosh_push(ys, 0.0)
- tests/stdlib/kalana_slope2.sm:9 — kosh_push(ys, 1.0)
- tests/stdlib/kalana_slope2.sm:10 — kosh_push(ys, 4.0)
- tests/stdlib/kalana_trapezoid.sm:5 — kosh_push(xs, 0.0)
- tests/stdlib/kalana_trapezoid.sm:6 — kosh_push(xs, 1.0)
- tests/stdlib/kalana_trapezoid.sm:7 — kosh_push(xs, 2.0)
- tests/stdlib/kalana_trapezoid.sm:8 — kosh_push(ys, 0.0)
- tests/stdlib/kalana_trapezoid.sm:9 — kosh_push(ys, 1.0)
- tests/stdlib/kalana_trapezoid.sm:10 — kosh_push(ys, 4.0)
- tests/stdlib/kalana_trapezoid.sm:15 — kosh_push(xs2, 0.0)
- tests/stdlib/kalana_trapezoid.sm:16 — kosh_push(xs2, 2.0)
- tests/stdlib/kalana_trapezoid.sm:17 — kosh_push(ys2, 0.0)
- tests/stdlib/kalana_trapezoid.sm:18 — kosh_push(ys2, 4.0)
- tests/stdlib/kosh_reuse.sm:11 — kosh_push(v, round * 10 + i)
- tests/stdlib/r11_kalana_edges.sm:6 — kosh_push(xs, 0.0)
- tests/stdlib/r11_kalana_edges.sm:7 — kosh_push(xs, 2.0)
- tests/stdlib/r11_kalana_edges.sm:9 — kosh_push(ys, 1.0)
- tests/stdlib/r11_kalana_edges.sm:10 — kosh_push(ys, 5.0)
- tests/stdlib/r11_kalana_edges.sm:12 — kosh_push(xs, 3.0)
- tests/stdlib/r11_kalana_edges.sm:13 — kosh_push(ys, 7.0)
- tests/stdlib/r11_kalana_edges.sm:17 — kosh_push(c, -1.0)
- tests/stdlib/r11_kalana_edges.sm:18 — kosh_push(c, 1.0)
- tests/stdlib/r11_kalana_edges.sm:20 — kosh_push(ok, 0.0)
- tests/stdlib/r37_bounds.sm:40 — kosh_push(a, 1.5)
- tests/stdlib/r37_bounds.sm:41 — kosh_push(b, 2.0)
- tests/stdlib/r37_bounds.sm:42 — kosh_push(o, 0.0)
- tests/stdlib/samanvaya_mat_gunana.sm:4 — kosh_push(a, 1.0)
- tests/stdlib/samanvaya_mat_gunana.sm:5 — kosh_push(a, 2.0)
- tests/stdlib/samanvaya_mat_gunana.sm:6 — kosh_push(a, 3.0)
- tests/stdlib/samanvaya_mat_gunana.sm:7 — kosh_push(a, 4.0)
- tests/stdlib/samanvaya_mat_gunana.sm:9 — kosh_push(b, 5.0)
- tests/stdlib/samanvaya_mat_gunana.sm:10 — kosh_push(b, 6.0)
- tests/stdlib/samanvaya_mat_gunana.sm:11 — kosh_push(b, 7.0)
- tests/stdlib/samanvaya_mat_gunana.sm:12 — kosh_push(b, 8.0)
- tests/stdlib/samanvaya_mat_gunana.sm:14 — kosh_push(out, 0.0)
- tests/stdlib/samanvaya_mat_gunana.sm:15 — kosh_push(out, 0.0)
- tests/stdlib/samanvaya_mat_gunana.sm:16 — kosh_push(out, 0.0)
- tests/stdlib/samanvaya_mat_gunana.sm:17 — kosh_push(out, 0.0)
- tests/stdlib/samanvaya_mat_yoga.sm:4 — kosh_push(a, 1.0)
- tests/stdlib/samanvaya_mat_yoga.sm:5 — kosh_push(a, 2.0)
- tests/stdlib/samanvaya_mat_yoga.sm:6 — kosh_push(a, 3.0)
- tests/stdlib/samanvaya_mat_yoga.sm:7 — kosh_push(a, 4.0)
- tests/stdlib/samanvaya_mat_yoga.sm:9 — kosh_push(b, 5.0)
- tests/stdlib/samanvaya_mat_yoga.sm:10 — kosh_push(b, 6.0)
- tests/stdlib/samanvaya_mat_yoga.sm:11 — kosh_push(b, 7.0)
- tests/stdlib/samanvaya_mat_yoga.sm:12 — kosh_push(b, 8.0)
- tests/stdlib/samanvaya_mat_yoga.sm:14 — kosh_push(out, 0.0)
- tests/stdlib/samanvaya_mat_yoga.sm:15 — kosh_push(out, 0.0)
- tests/stdlib/samanvaya_mat_yoga.sm:16 — kosh_push(out, 0.0)
- tests/stdlib/samanvaya_mat_yoga.sm:17 — kosh_push(out, 0.0)
- tests/stdlib/samanvaya_nirnaya2.sm:4 — kosh_push(a, 1.0)
- tests/stdlib/samanvaya_nirnaya2.sm:5 — kosh_push(a, 2.0)
- tests/stdlib/samanvaya_nirnaya2.sm:6 — kosh_push(a, 3.0)
- tests/stdlib/samanvaya_nirnaya2.sm:7 — kosh_push(a, 4.0)
- tests/stdlib/samanvaya_nirnaya2.sm:11 — kosh_push(ident, 1.0)
- tests/stdlib/samanvaya_nirnaya2.sm:12 — kosh_push(ident, 0.0)
- tests/stdlib/samanvaya_nirnaya2.sm:13 — kosh_push(ident, 0.0)
- tests/stdlib/samanvaya_nirnaya2.sm:14 — kosh_push(ident, 1.0)
- tests/stdlib/samanvaya_nirnaya3.sm:4 — kosh_push(ident, 1.0)
- tests/stdlib/samanvaya_nirnaya3.sm:5 — kosh_push(ident, 0.0)
- tests/stdlib/samanvaya_nirnaya3.sm:6 — kosh_push(ident, 0.0)
- tests/stdlib/samanvaya_nirnaya3.sm:7 — kosh_push(ident, 0.0)
- tests/stdlib/samanvaya_nirnaya3.sm:8 — kosh_push(ident, 1.0)
- tests/stdlib/samanvaya_nirnaya3.sm:9 — kosh_push(ident, 0.0)
- tests/stdlib/samanvaya_nirnaya3.sm:10 — kosh_push(ident, 0.0)
- tests/stdlib/samanvaya_nirnaya3.sm:11 — kosh_push(ident, 0.0)
- tests/stdlib/samanvaya_nirnaya3.sm:12 — kosh_push(ident, 1.0)
- tests/stdlib/samanvaya_nirnaya3.sm:16 — kosh_push(sing, 1.0)
- tests/stdlib/samanvaya_nirnaya3.sm:17 — kosh_push(sing, 2.0)
- tests/stdlib/samanvaya_nirnaya3.sm:18 — kosh_push(sing, 3.0)
- tests/stdlib/samanvaya_nirnaya3.sm:19 — kosh_push(sing, 4.0)
- tests/stdlib/samanvaya_nirnaya3.sm:20 — kosh_push(sing, 5.0)
- tests/stdlib/samanvaya_nirnaya3.sm:21 — kosh_push(sing, 6.0)
- tests/stdlib/samanvaya_nirnaya3.sm:22 — kosh_push(sing, 7.0)
- tests/stdlib/samanvaya_nirnaya3.sm:23 — kosh_push(sing, 8.0)
- tests/stdlib/samanvaya_nirnaya3.sm:24 — kosh_push(sing, 9.0)
- tests/stdlib/samanvaya_nishan.sm:4 — kosh_push(a, 1.0)
- tests/stdlib/samanvaya_nishan.sm:5 — kosh_push(a, 2.0)
- tests/stdlib/samanvaya_nishan.sm:6 — kosh_push(a, 3.0)
- tests/stdlib/samanvaya_nishan.sm:7 — kosh_push(a, 4.0)
- tests/stdlib/samanvaya_pehchan.sm:4 — kosh_push(out, 0.0)
- tests/stdlib/samanvaya_pehchan.sm:5 — kosh_push(out, 0.0)
- tests/stdlib/samanvaya_pehchan.sm:6 — kosh_push(out, 0.0)
- tests/stdlib/samanvaya_pehchan.sm:7 — kosh_push(out, 0.0)
- tests/stdlib/samanvaya_rekha_manak.sm:4 — kosh_push(a, 1.0)
- tests/stdlib/samanvaya_rekha_manak.sm:5 — kosh_push(a, -2.0)
- tests/stdlib/samanvaya_rekha_manak.sm:6 — kosh_push(a, 3.0)
- tests/stdlib/samanvaya_rekha_manak.sm:7 — kosh_push(a, -4.0)
- tests/stdlib/samanvaya_sadish_yoga.sm:4 — kosh_push(u, 1.0)
- tests/stdlib/samanvaya_sadish_yoga.sm:5 — kosh_push(u, 2.0)
- tests/stdlib/samanvaya_sadish_yoga.sm:6 — kosh_push(u, 3.0)
- tests/stdlib/samanvaya_sadish_yoga.sm:8 — kosh_push(v, 4.0)
- tests/stdlib/samanvaya_sadish_yoga.sm:9 — kosh_push(v, 5.0)
- tests/stdlib/samanvaya_sadish_yoga.sm:10 — kosh_push(v, 6.0)
- tests/stdlib/samanvaya_skalar.sm:4 — kosh_push(a, 1.0)
- tests/stdlib/samanvaya_skalar.sm:5 — kosh_push(a, 2.0)
- tests/stdlib/samanvaya_skalar.sm:6 — kosh_push(a, 3.0)
- tests/stdlib/samanvaya_skalar.sm:7 — kosh_push(a, 4.0)
- tests/stdlib/samanvaya_skalar.sm:9 — kosh_push(out, 0.0)
- tests/stdlib/samanvaya_skalar.sm:10 — kosh_push(out, 0.0)
- tests/stdlib/samanvaya_skalar.sm:11 — kosh_push(out, 0.0)
- tests/stdlib/samanvaya_skalar.sm:12 — kosh_push(out, 0.0)
- tests/stdlib/samanvaya_vivartana.sm:4 — kosh_push(a, 1.0)
- tests/stdlib/samanvaya_vivartana.sm:5 — kosh_push(a, 2.0)
- tests/stdlib/samanvaya_vivartana.sm:6 — kosh_push(a, 3.0)
- tests/stdlib/samanvaya_vivartana.sm:7 — kosh_push(a, 4.0)
- tests/stdlib/samanvaya_vivartana.sm:8 — kosh_push(a, 5.0)
- tests/stdlib/samanvaya_vivartana.sm:9 — kosh_push(a, 6.0)
- tests/stdlib/samanvaya_vivartana.sm:11 — kosh_push(out, 0.0)
- tests/stdlib/samanvaya_vivartana.sm:12 — kosh_push(out, 0.0)
- tests/stdlib/samanvaya_vivartana.sm:13 — kosh_push(out, 0.0)
- tests/stdlib/samanvaya_vivartana.sm:14 — kosh_push(out, 0.0)
- tests/stdlib/samanvaya_vivartana.sm:15 — kosh_push(out, 0.0)
- tests/stdlib/samanvaya_vivartana.sm:16 — kosh_push(out, 0.0)
- tests/stdlib/sankhyiki_adhikatama.sm:4 — kosh_push(a, 3.0)
- tests/stdlib/sankhyiki_adhikatama.sm:5 — kosh_push(a, 1.0)
- tests/stdlib/sankhyiki_adhikatama.sm:6 — kosh_push(a, 2.0)
- tests/stdlib/sankhyiki_adhikatama.sm:10 — kosh_push(b, -5.0)
- tests/stdlib/sankhyiki_adhikatama.sm:11 — kosh_push(b, -1.0)
- tests/stdlib/sankhyiki_bindu.sm:4 — kosh_push(a, 1.0)
- tests/stdlib/sankhyiki_bindu.sm:5 — kosh_push(a, 2.0)
- tests/stdlib/sankhyiki_bindu.sm:6 — kosh_push(a, 3.0)
- tests/stdlib/sankhyiki_bindu.sm:8 — kosh_push(b, 4.0)
- tests/stdlib/sankhyiki_bindu.sm:9 — kosh_push(b, 5.0)
- tests/stdlib/sankhyiki_bindu.sm:10 — kosh_push(b, 6.0)
- tests/stdlib/sankhyiki_bindu.sm:14 — kosh_push(c, 1.5)
- tests/stdlib/sankhyiki_bindu.sm:15 — kosh_push(c, 2.5)
- tests/stdlib/sankhyiki_bindu.sm:17 — kosh_push(d, 2.0)
- tests/stdlib/sankhyiki_bindu.sm:18 — kosh_push(d, 4.0)
- tests/stdlib/sankhyiki_laghutama.sm:4 — kosh_push(a, 3.0)
- tests/stdlib/sankhyiki_laghutama.sm:5 — kosh_push(a, 1.0)
- tests/stdlib/sankhyiki_laghutama.sm:6 — kosh_push(a, 2.0)
- tests/stdlib/sankhyiki_laghutama.sm:10 — kosh_push(b, -5.0)
- tests/stdlib/sankhyiki_laghutama.sm:11 — kosh_push(b, 5.0)
- tests/stdlib/sankhyiki_madhya.sm:4 — kosh_push(a, 1.0)
- tests/stdlib/sankhyiki_madhya.sm:5 — kosh_push(a, 2.0)
- tests/stdlib/sankhyiki_madhya.sm:6 — kosh_push(a, 3.0)
- tests/stdlib/sankhyiki_madhya.sm:7 — kosh_push(a, 4.0)
- tests/stdlib/sankhyiki_madhya.sm:11 — kosh_push(b, 10.0)
- tests/stdlib/sankhyiki_madhya.sm:12 — kosh_push(b, 20.0)
- tests/stdlib/sankhyiki_manak.sm:4 — kosh_push(a, 3.0)
- tests/stdlib/sankhyiki_manak.sm:5 — kosh_push(a, 4.0)
- tests/stdlib/sankhyiki_manak.sm:9 — kosh_push(b, 1.0)
- tests/stdlib/sankhyiki_manak.sm:10 — kosh_push(b, 2.0)
- tests/stdlib/sankhyiki_manak.sm:11 — kosh_push(b, 2.0)
- tests/stdlib/sankhyiki_prasaran.sm:4 — kosh_push(a, 1.0)
- tests/stdlib/sankhyiki_prasaran.sm:5 — kosh_push(a, 2.0)
- tests/stdlib/sankhyiki_prasaran.sm:6 — kosh_push(a, 3.0)
- tests/stdlib/sankhyiki_prasaran.sm:7 — kosh_push(a, 4.0)
- tests/stdlib/sankhyiki_prasaran.sm:8 — kosh_push(a, 5.0)
- tests/stdlib/sankhyiki_prasaran.sm:12 — kosh_push(b, 7.0)
- tests/stdlib/sankhyiki_vichalan.sm:4 — kosh_push(a, 1.0)
- tests/stdlib/sankhyiki_vichalan.sm:5 — kosh_push(a, 2.0)
- tests/stdlib/sankhyiki_vichalan.sm:6 — kosh_push(a, 3.0)
- tests/stdlib/sankhyiki_vichalan.sm:7 — kosh_push(a, 4.0)
- tests/stdlib/sankhyiki_vichalan.sm:8 — kosh_push(a, 5.0)
- tests/stdlib/sankhyiki_vichalan.sm:12 — kosh_push(b, 5.0)
- tests/stdlib/sankhyiki_vichalan.sm:13 — kosh_push(b, 5.0)
- tests/stdlib/sankhyiki_vyapti.sm:4 — kosh_push(a, 1.0)
- tests/stdlib/sankhyiki_vyapti.sm:5 — kosh_push(a, 5.0)
- tests/stdlib/sankhyiki_vyapti.sm:6 — kosh_push(a, 3.0)
- tests/stdlib/sankhyiki_vyapti.sm:10 — kosh_push(b, 2.0)
- tests/stdlib/sankhyiki_vyapti.sm:11 — kosh_push(b, 2.0)
- tests/stdlib/sankhyiki_yoga.sm:4 — kosh_push(a, 1.0)
- tests/stdlib/sankhyiki_yoga.sm:5 — kosh_push(a, 2.0)
- tests/stdlib/sankhyiki_yoga.sm:6 — kosh_push(a, 3.0)
- tests/stdlib/sankhyiki_yoga.sm:7 — kosh_push(a, 4.0)
- tests/stdlib/sankhyiki_yoga.sm:11 — kosh_push(b, 5.5)

## kosh_pop -> kosh_apanay (builtin)
Live sites: 31. DO-NOT-TOUCH in tests/negative/: 14.
- examples/100_t18_kosh_bounds.sm:5 — kosh_pop(a)
- examples/101_t18_kosh_empty.sm:4 — likha(kosh_pop(a))
- examples/109_t18_kosh_dasham.sm:12 — dasham p = kosh_pop(a)
- examples/110_t18_kosh_dasham_devanagari.sm:8 — likha(kosh_pop(b))
- examples/111_t18_kosh_dasham_function_return.sm:5 — prati kosh_pop(values)
- examples/112_t18_kosh_integer_conversion.sm:7 — likha(kosh_pop(a))
- examples/119_t18_kosh_param_forward.sm:12 — prati kosh_pop(a)
- examples/257_r48_kosh_empty.sm:14 — likha(kosh_pop(v))
- examples/257_r48_kosh_empty.sm:19 — likha(kosh_pop(v))
- examples/96_t18_kosh.sm:15 — likha(kosh_pop(a))
- examples/98_t18_kosh_empty.sm:4 — likha(kosh_pop(a))
- examples/99_t18_kosh.sm:15 — likha(kosh_pop(a))
- src/r11_sandesh.inc:1726 — r11_bengali_46 db "Sutram Error: ",224,166,150,224,166,190,224,166,178,224,166,191," ",224,166,149,2
- src/r11_sandesh.inc:2000 — r11_hindi_46 db "Sutram Error: ",224,164,150,224,164,190,224,164,178,224,165,128," ",224,164,149,224
- src/r11_sandesh.inc:2137 — r11_kannada_46 db "Sutram Error: ",224,178,150,224,178,190,224,178,178,224,178,191," ",224,178,149,2
- src/r11_sandesh.inc:2274 — r11_malayalam_46 db "Sutram Error: ",224,180,182,224,181,130,224,180,168,224,181,141,224,180,175,224
- src/r11_sandesh.inc:2411 — r11_marathi_46 db "Sutram Error: ",224,164,176,224,164,191,224,164,149,224,164,190,224,164,174,224,1
- src/r11_sandesh.inc:2548 — r11_odia_46 db "Sutram Error: ",224,172,150,224,172,190,224,172,178,224,172,191," ",224,172,149,224,
- src/r11_sandesh.inc:2685 — r11_punjabi_46 db "Sutram Error: ",224,168,150,224,168,188,224,168,190,224,168,178,224,169,128," ",2
- src/r11_sandesh.inc:2822 — r11_tamil_46 db "Sutram Error: ",224,174,149,224,174,190,224,174,178,224,174,191," ",224,174,149,224
- src/r11_sandesh.inc:2959 — r11_telugu_46 db "Sutram Error: ",224,176,150,224,176,190,224,176,179,224,177,128," ",224,176,149,22
- src/sutram_compiler.asm:216 — BN_KOSHPOP  equ 38   ; kosh_pop(k) -> removed value
- src/sutram_compiler.asm:295 — db 1,1               ; 38 kosh_pop
- src/sutram_compiler.asm:373 — msg_kosh_empty db "Sutram Error: riktat koshat kosh_pop", 10, 0
- src/sutram_compiler.asm:766 — bn_koshpop  db "kosh_pop", 0
- src/sutram_compiler.asm:15496 — ; generated conditional branch. Existing kosh_pop bytes stay unchanged.
- src/sutram_compiler.asm:15537 — ; is established by the common checked kosh_pop/kosh_peek prologue.
- tests/r63_check/kosh_native_core.sm:12 — likha(kosh_pop(a))
- tests/r64_check/kosh_nonempty.sm:9 — likha(kosh_pop(k))
- tests/r64_check/kosh_pop_empty.sm:4 — likha(kosh_pop(k))
- tests/sandesh/cases/kosh_empty.sm:4 — likha(kosh_pop(a))

## kosh_len -> kosh_aayam (builtin)
Live sites: 60. DO-NOT-TOUCH in tests/negative/: 74.
- examples/100_t18_kosh_devanagari.sm:4 — likha(kosh_len(b))
- examples/100_t18_kosh_devanagari.sm:7 — likha(kosh_len(b))
- examples/109_t18_kosh_dasham.sm:4 — likha(kosh_len(a))
- examples/109_t18_kosh_dasham.sm:14 — likha(kosh_len(a))
- examples/110_t18_kosh_dasham_devanagari.sm:9 — likha(kosh_len(b))
- examples/118_t18_kosh_param.sm:5 — prati total / kosh_len(a)
- examples/118_t18_kosh_param.sm:9 — prati a[0] + a[1] + kosh_len(a)
- examples/119_t18_kosh_param_forward.sm:20 — likha(kosh_len(values))
- examples/121_t18_kosh_param_push_reject.sm:5 — prati kosh_len(a)
- examples/203_meru_with_kosh.sm:17 — likha(kosh_len(row))
- examples/203_meru_with_kosh.sm:20 — yavat (j < kosh_len(row)) {
- examples/205_madhava_pi_kosh.sm:14 — likha(kosh_len(terms))
- examples/205_madhava_pi_kosh.sm:17 — yavat (i < kosh_len(terms)) {
- examples/206_sankhyiki.sm:17 — likha(kosh_len(xs))
- examples/208_kalana.sm:20 — likha(kosh_len(xs))
- examples/255_r42_alias_kosh_push.sm:9 — likha(kosh_len(v))
- examples/257_r48_kosh_empty.sm:18 — likha(kosh_len(v))
- examples/96_t18_kosh.sm:4 — likha(kosh_len(a))
- examples/96_t18_kosh.sm:16 — likha(kosh_len(a))
- examples/97_t18_kosh_devanagari.sm:4 — likha(kosh_len(b))
- examples/97_t18_kosh_devanagari.sm:7 — likha(kosh_len(b))
- examples/99_t18_kosh.sm:4 — likha(kosh_len(a))
- examples/99_t18_kosh.sm:16 — likha(kosh_len(a))
- lib/kalana.smlib:19 — vitti n = kosh_len(xs)
- lib/kalana.smlib:20 — yadi (kosh_len(ys) < n) { n = kosh_len(ys) }
- lib/kalana.smlib:35 — vitti n = kosh_len(xs)
- lib/kalana.smlib:36 — yadi (kosh_len(ys) < n) { n = kosh_len(ys) }
- lib/kalana.smlib:60 — vitti n = kosh_len(xs)
- lib/kalana.smlib:61 — yadi (kosh_len(ys) < n) { n = kosh_len(ys) }
- lib/kalana.smlib:80 — vitti n = kosh_len(xs)
- lib/kalana.smlib:81 — yadi (kosh_len(ys) < n) { n = kosh_len(ys) }
- lib/kalana.smlib:103 — vitti n = kosh_len(c)
- lib/samanvaya.smlib:68 — yadi (samanvaya_akar_na(m, n, kosh_len(a)) == 1) { prati 0 - 1 }
- lib/samanvaya.smlib:69 — yadi (samanvaya_akar_na(m, n, kosh_len(b)) == 1) { prati 0 - 1 }
- lib/samanvaya.smlib:70 — yadi (samanvaya_akar_na(m, n, kosh_len(out)) == 1) { prati 0 - 1 }
- lib/samanvaya.smlib:81 — yadi (samanvaya_akar_na(m, n, kosh_len(a)) == 1) { prati 0 - 1 }
- lib/samanvaya.smlib:82 — yadi (samanvaya_akar_na(m, n, kosh_len(out)) == 1) { prati 0 - 1 }
- lib/samanvaya.smlib:136 — vitti n = kosh_len(u)
- lib/samanvaya.smlib:137 — yadi (kosh_len(v) < n) { n = kosh_len(v) }
- lib/sankhyiki.smlib:19 — yavat (i < kosh_len(xs)) {
- lib/sankhyiki.smlib:28 — vitti n = kosh_len(xs)
- lib/sankhyiki.smlib:35 — vitti n = kosh_len(xs)
- lib/sankhyiki.smlib:48 — vitti n = kosh_len(xs)
- lib/sankhyiki.smlib:66 — vitti n = kosh_len(xs)
- lib/sankhyiki.smlib:100 — vitti na = kosh_len(a)
- lib/sankhyiki.smlib:101 — vitti nb = kosh_len(b)
- src/sutram_compiler.asm:217 — BN_KOSHLEN  equ 39   ; kosh_len(k) -> logical length
- src/sutram_compiler.asm:296 — db 1,1               ; 39 kosh_len
- src/sutram_compiler.asm:767 — bn_koshlen  db "kosh_len", 0
- tests/r63_check/kosh_fifo_core.sm:10 — likha(kosh_len(q))
- tests/r63_check/kosh_fifo_core.sm:16 — likha(kosh_len(q))
- tests/r63_check/kosh_native_core.sm:9 — likha(kosh_len(a))
- tests/r63_check/kosh_native_core.sm:13 — likha(kosh_len(a))
- tests/r63_check/kosh_native_core.sm:16 — likha(kosh_len(a))
- tests/r63_check/kosh_native_core.sm:20 — likha(kosh_len(a))
- tests/r63_check/kosh_native_float.sm:7 — likha(kosh_len(v))
- tests/r63_check/kosh_native_float.sm:14 — likha(kosh_len(v))
- tests/r64_check/kosh_nonempty.sm:7 — likha(kosh_len(k))
- tests/stdlib/kosh_reuse.sm:17 — likha(kosh_len(v))
- tests/stdlib/kosh_reuse.sm:25 — likha(kosh_len(v))

## kosh_cap -> kosh_kshamata (builtin)
Live sites: 20. DO-NOT-TOUCH in tests/negative/: 0.
- examples/100_t18_kosh_devanagari.sm:5 — likha(kosh_cap(b))
- examples/100_t18_kosh_devanagari.sm:8 — likha(kosh_cap(b))
- examples/109_t18_kosh_dasham.sm:7 — likha(kosh_cap(a))
- examples/96_t18_kosh.sm:5 — likha(kosh_cap(a))
- examples/96_t18_kosh.sm:8 — likha(kosh_cap(a))
- examples/96_t18_kosh.sm:10 — likha(kosh_cap(a))
- examples/96_t18_kosh.sm:17 — likha(kosh_cap(a))
- examples/97_t18_kosh_devanagari.sm:5 — likha(kosh_cap(b))
- examples/97_t18_kosh_devanagari.sm:8 — likha(kosh_cap(b))
- examples/99_t18_kosh.sm:5 — likha(kosh_cap(a))
- examples/99_t18_kosh.sm:8 — likha(kosh_cap(a))
- examples/99_t18_kosh.sm:10 — likha(kosh_cap(a))
- examples/99_t18_kosh.sm:17 — likha(kosh_cap(a))
- src/sutram_compiler.asm:218 — BN_KOSHCAP  equ 40   ; kosh_cap(k) -> current capacity
- src/sutram_compiler.asm:297 — db 1,1               ; 40 kosh_cap
- src/sutram_compiler.asm:768 — bn_koshcap  db "kosh_cap", 0
- tests/r63_check/kosh_native_core.sm:17 — likha(kosh_cap(a))
- tests/r63_check/kosh_native_float.sm:11 — likha(kosh_cap(v))
- tests/stdlib/kosh_reuse.sm:15 — likha(kosh_cap(v))
- tests/stdlib/kosh_reuse.sm:27 — likha(kosh_cap(v))

## kosh_clear -> kosh_shodh (builtin)
Live sites: 8. DO-NOT-TOUCH in tests/negative/: 0.
- src/sutram_compiler.asm:220 — BN_KOSHCLEAR equ 42 ; R63 kosh_clear(k) -> 0; reset logical length in place
- src/sutram_compiler.asm:299 — db 1,1               ; 42 kosh_clear
- src/sutram_compiler.asm:769 — bn_koshclear db "kosh_clear", 0
- tests/r63_check/kosh_invalid_non_kosh.sm:4 — likha(kosh_clear(a))
- tests/r63_check/kosh_native_core.sm:5 — likha(kosh_clear(a))
- tests/r63_check/kosh_native_core.sm:14 — likha(kosh_clear(a))
- tests/r63_check/kosh_native_float.sm:9 — likha(kosh_clear(v))
- tests/stdlib/kosh_reuse.sm:24 — kosh_clear(v)

## kosh_empty -> kosh_rikt (builtin)
Live sites: 14. DO-NOT-TOUCH in tests/negative/: 0.
- examples/257_r48_kosh_empty.sm:11 — yadi (kosh_empty(v)) {
- src/sutram_compiler.asm:221 — BN_KOSHEMPTY equ 43 ; R63 kosh_empty(k) -> 1 when length=0
- src/sutram_compiler.asm:300 — db 1,1               ; 43 kosh_empty
- src/sutram_compiler.asm:770 — bn_koshempty db "kosh_empty", 0
- tests/r63_check/kosh_fifo_core.sm:4 — likha(kosh_empty(q))
- tests/r63_check/kosh_fifo_core.sm:13 — likha(kosh_empty(q))
- tests/r63_check/kosh_fifo_float.sm:9 — likha(kosh_empty(q))
- tests/r63_check/kosh_invalid_arity.sm:4 — likha(kosh_empty(a, 2))
- tests/r63_check/kosh_native_core.sm:4 — likha(kosh_empty(a))
- tests/r63_check/kosh_native_core.sm:6 — likha(kosh_empty(a))
- tests/r63_check/kosh_native_core.sm:15 — likha(kosh_empty(a))
- tests/r63_check/kosh_native_float.sm:4 — likha(kosh_empty(v))
- tests/r63_check/kosh_native_float.sm:10 — likha(kosh_empty(v))
- tests/r64_check/kosh_nonempty.sm:10 — likha(kosh_empty(k))

## kosh_peek -> kosh_iksh (builtin)
Live sites: 26. DO-NOT-TOUCH in tests/negative/: 0.
- src/r11_sandesh.inc:1727 — r11_bengali_47 db "Sutram Error: ",224,166,150,224,166,190,224,166,178,224,166,191," ",224,166,149,2
- src/r11_sandesh.inc:2001 — r11_hindi_47 db "Sutram Error: ",224,164,150,224,164,190,224,164,178,224,165,128," ",224,164,149,224
- src/r11_sandesh.inc:2138 — r11_kannada_47 db "Sutram Error: ",224,178,150,224,178,190,224,178,178,224,178,191," ",224,178,149,2
- src/r11_sandesh.inc:2275 — r11_malayalam_47 db "Sutram Error: ",224,180,182,224,181,130,224,180,168,224,181,141,224,180,175,224
- src/r11_sandesh.inc:2412 — r11_marathi_47 db "Sutram Error: ",224,164,176,224,164,191,224,164,149,224,164,190,224,164,174,224,1
- src/r11_sandesh.inc:2549 — r11_odia_47 db "Sutram Error: ",224,172,150,224,172,190,224,172,178,224,172,191," ",224,172,149,224,
- src/r11_sandesh.inc:2686 — r11_punjabi_47 db "Sutram Error: ",224,168,150,224,168,188,224,168,190,224,168,178,224,169,128," ",2
- src/r11_sandesh.inc:2823 — r11_tamil_47 db "Sutram Error: ",224,174,149,224,174,190,224,174,178,224,174,191," ",224,174,149,224
- src/r11_sandesh.inc:2960 — r11_telugu_47 db "Sutram Error: ",224,176,150,224,176,190,224,176,179,224,177,128," ",224,176,149,22
- src/sutram_compiler.asm:222 — BN_KOSHPEEK equ 44  ; R63 kosh_peek(k) -> last element (without popping)
- src/sutram_compiler.asm:301 — db 1,1               ; 44 kosh_peek
- src/sutram_compiler.asm:374 — msg_kosh_peek_empty db "Sutram Error: riktat koshat kosh_peek", 10, 0
- src/sutram_compiler.asm:771 — bn_koshpeek db "kosh_peek", 0
- src/sutram_compiler.asm:15537 — ; is established by the common checked kosh_pop/kosh_peek prologue.
- tests/r63_check/kosh_fifo_core.sm:9 — likha(kosh_peek(q))
- tests/r63_check/kosh_fifo_float.sm:7 — likha(kosh_peek(q))
- tests/r63_check/kosh_native_core.sm:8 — likha(kosh_peek(a))
- tests/r63_check/kosh_native_core.sm:11 — likha(kosh_peek(a))
- tests/r63_check/kosh_native_core.sm:19 — likha(kosh_peek(a))
- tests/r63_check/kosh_native_float.sm:6 — likha(kosh_peek(v))
- tests/r63_check/kosh_native_float.sm:8 — likha(kosh_peek(v))
- tests/r63_check/kosh_native_float.sm:13 — likha(kosh_peek(v))
- tests/r63_check/kosh_peek_empty.sm:4 — likha(kosh_peek(a))
- tests/r64_check/kosh_nonempty.sm:6 — likha(kosh_peek(k))
- tests/r64_check/kosh_peek_empty.sm:4 — likha(kosh_peek(k))
- tests/r83/cases/empty_kosh_peek.sm:4 — likha(kosh_peek(a))

## kosh_dequeue -> kosh_purva_apanay (builtin)
Live sites: 23. DO-NOT-TOUCH in tests/negative/: 0.
- src/r11_sandesh.inc:1728 — r11_bengali_48 db "Sutram Error: ",224,166,150,224,166,190,224,166,178,224,166,191," ",224,166,149,2
- src/r11_sandesh.inc:2002 — r11_hindi_48 db "Sutram Error: ",224,164,150,224,164,190,224,164,178,224,165,128," ",224,164,149,224
- src/r11_sandesh.inc:2139 — r11_kannada_48 db "Sutram Error: ",224,178,150,224,178,190,224,178,178,224,178,191," ",224,178,149,2
- src/r11_sandesh.inc:2276 — r11_malayalam_48 db "Sutram Error: ",224,180,182,224,181,130,224,180,168,224,181,141,224,180,175,224
- src/r11_sandesh.inc:2413 — r11_marathi_48 db "Sutram Error: ",224,164,176,224,164,191,224,164,149,224,164,190,224,164,174,224,1
- src/r11_sandesh.inc:2550 — r11_odia_48 db "Sutram Error: ",224,172,150,224,172,190,224,172,178,224,172,191," ",224,172,149,224,
- src/r11_sandesh.inc:2687 — r11_punjabi_48 db "Sutram Error: ",224,168,150,224,168,188,224,168,190,224,168,178,224,169,128," ",2
- src/r11_sandesh.inc:2824 — r11_tamil_48 db "Sutram Error: ",224,174,149,224,174,190,224,174,178,224,174,191," ",224,174,149,224
- src/r11_sandesh.inc:2961 — r11_telugu_48 db "Sutram Error: ",224,176,150,224,176,190,224,176,179,224,177,128," ",224,176,149,22
- src/sutram_compiler.asm:223 — BN_KOSHDEQUEUE equ 45 ; R63 kosh_dequeue(k) -> first element (FIFO)
- src/sutram_compiler.asm:302 — db 1,1               ; 45 kosh_dequeue
- src/sutram_compiler.asm:375 — msg_kosh_dequeue_empty db "Sutram Error: riktat koshat kosh_dequeue", 10, 0
- src/sutram_compiler.asm:773 — bn_koshdequeue db "kosh_dequeue", 0 ; FIFO removal of first
- tests/r63_check/kosh_dequeue_empty.sm:4 — likha(kosh_dequeue(q))
- tests/r63_check/kosh_fifo_core.sm:8 — likha(kosh_dequeue(q))
- tests/r63_check/kosh_fifo_core.sm:11 — likha(kosh_dequeue(q))
- tests/r63_check/kosh_fifo_core.sm:12 — likha(kosh_dequeue(q))
- tests/r63_check/kosh_fifo_core.sm:15 — likha(kosh_dequeue(q))
- tests/r63_check/kosh_fifo_float.sm:6 — likha(kosh_dequeue(q))
- tests/r63_check/kosh_fifo_float.sm:8 — likha(kosh_dequeue(q))
- tests/r64_check/kosh_dequeue_empty.sm:4 — likha(kosh_dequeue(k))
- tests/r64_check/kosh_nonempty.sm:8 — likha(kosh_dequeue(k))
- tests/r83/cases/empty_kosh_dequeue.sm:4 — likha(kosh_dequeue(a))

## kosh_enqueue -> kosh_purva_yuj (builtin - REJECT, direction wrong, see notes)
Live sites: 10. DO-NOT-TOUCH in tests/negative/: 0.
- src/sutram_compiler.asm:772 — bn_koshenqueue db "kosh_enqueue", 0  ; FIFO append = kosh_push
- tests/r63_check/kosh_fifo_core.sm:5 — likha(kosh_enqueue(q, 11))
- tests/r63_check/kosh_fifo_core.sm:6 — likha(kosh_enqueue(q, 22))
- tests/r63_check/kosh_fifo_core.sm:7 — likha(kosh_enqueue(q, 33))
- tests/r63_check/kosh_fifo_core.sm:14 — likha(kosh_enqueue(q, 44))
- tests/r63_check/kosh_fifo_float.sm:4 — likha(kosh_enqueue(q, 1.25))
- tests/r63_check/kosh_fifo_float.sm:5 — likha(kosh_enqueue(q, 2.5))
- tests/r63_check/kosh_native_core.sm:7 — likha(kosh_enqueue(a, 10))
- tests/r63_check/kosh_native_core.sm:18 — likha(kosh_enqueue(a, 30))
- tests/r63_check/kosh_native_float.sm:5 — likha(kosh_enqueue(v, 1.5))

## netsock -> jala_sutra (builtin)
Live sites: 5. DO-NOT-TOUCH in tests/negative/: 0.
- examples/245_r18_netsock.sm:9 — vitti s = netsock()
- examples/245_r18_netsock.sm:11 — vitti t = netsock()
- src/sutram_compiler.asm:266 — db 0,0               ; 9 netsock
- src/sutram_compiler.asm:747 — bn_netsock   db "netsock", 0
- src/sutram_compiler.asm:16676 — ; netsock() → socket(AF_INET=2, SOCK_STREAM=1, 0)

## netbind -> jala_bandh (builtin)
Live sites: 4. DO-NOT-TOUCH in tests/negative/: 0.
- examples/245_r18_netsock.sm:13 — likha(netbind(0 - 1, 0))
- src/sutram_compiler.asm:267 — db 2,2               ; 10 netbind
- src/sutram_compiler.asm:748 — bn_netbind   db "netbind", 0
- src/sutram_compiler.asm:16720 — ; netbind(fd, port) → bind(fd, sockaddr_in, 16)

## netlisten -> jala_shravan (builtin)
Live sites: 4. DO-NOT-TOUCH in tests/negative/: 0.
- examples/245_r18_netsock.sm:14 — likha(netlisten(0 - 1))
- src/sutram_compiler.asm:268 — db 1,1               ; 11 netlisten
- src/sutram_compiler.asm:749 — bn_netlist   db "netlisten", 0
- src/sutram_compiler.asm:16864 — ; netlisten(fd) → listen(fd, 5)

## netaccept -> jala_grahan (builtin)
Live sites: 3. DO-NOT-TOUCH in tests/negative/: 0.
- src/sutram_compiler.asm:269 — db 1,1               ; 12 netaccept
- src/sutram_compiler.asm:750 — bn_netacc    db "netaccept", 0
- src/sutram_compiler.asm:16901 — ; netaccept(fd) → accept(fd, 0, 0)

## ganit -> ganan (module (file + yoj lines; ganit_* functions are separate, see notes))
Live sites: 41. DO-NOT-TOUCH in tests/negative/: 8.
- examples/07_module.sm:3 — yoj ganit
- examples/102_ast_multimodule_capacity.sm:2 — yoj ganit
- examples/10_mathlib.sm:1 — yoj ganit
- examples/61_stdlib_math.sm:2 — yoj ganit
- examples/66_module_dedupe.sm:1 — yoj ganit
- examples/66_module_dedupe.sm:2 — yoj ganit
- examples/70_module_collision.sm:1 — yoj ganit
- examples/79_ayojan_cwd.sm:1 — yoj ganit
- examples/86_b8_multi_modules.sm:1 — yoj ganit
- examples/87_b8_all_modules.sm:1 — yoj ganit
- examples/87_b8_func_params_capacity.sm:1 — yoj ganit
- examples/87_b8_math_sort_string.sm:1 — yoj ganit
- examples/99_ast_multimodule_capacity.sm:2 — yoj ganit
- examples/func_demo.sm:6 — likha("Calling ganit()...\n")
- examples/func_demo.sm:7 — ganit()
- examples/func_demo.sm:18 — prakriya ganit()
- examples/import_demo.sm:2 — yoj ganit
- tests/stdlib/breadth26.sm:1 — yoj ganit
- tests/stdlib/math_abs_val.sm:1 — yoj ganit
- tests/stdlib/math_bit_count.sm:1 — yoj ganit
- tests/stdlib/math_cube.sm:1 — yoj ganit
- tests/stdlib/math_double.sm:1 — yoj ganit
- tests/stdlib/math_fact.sm:1 — yoj ganit
- tests/stdlib/math_gcd.sm:1 — yoj ganit
- tests/stdlib/math_gcd_lcm_edge.sm:1 — yoj ganit
- tests/stdlib/math_inc.sm:1 — yoj ganit
- tests/stdlib/math_is_prime.sm:1 — yoj ganit
- tests/stdlib/math_lcm.sm:1 — yoj ganit
- tests/stdlib/math_max2.sm:1 — yoj ganit
- tests/stdlib/math_min2.sm:1 — yoj ganit
- tests/stdlib/math_power.sm:1 — yoj ganit
- tests/stdlib/math_sq.sm:1 — yoj ganit
- tests/stdlib/math_square.sm:1 — yoj ganit
- tests/stdlib/math_sum_to.sm:1 — yoj ganit
- tests/stdlib/math_triple.sm:1 — yoj ganit
- tests/stdlib/numeric29.sm:2 — yoj ganit
- tests/stdlib/numeric_hangfix.sm:2 — yoj ganit
- tests/stdlib/r8_list_model.sm:6 — yoj ganit
- tests/stdlib/r8_map_model.sm:6 — yoj ganit
- tests/stdlib/r8_number_edges.sm:5 — yoj ganit
- tests/stdlib/r8_split_model.sm:9 — yoj ganit

## fib -> meru_sankhya (lib ank)
Live sites: 8. DO-NOT-TOUCH in tests/negative/: 3.
- examples/81_stdlib_num2.sm:5 — likha(fib(10))
- examples/81_stdlib_num2.sm:7 — likha(fib(0))
- lib/ank.smlib:70 — prakriya fib(n) {
- tests/stdlib/num_fib.sm:3 — likha(fib(10))
- tests/stdlib/num_fib.sm:5 — likha(fib(0))
- tests/stdlib/num_fib.sm:7 — likha(fib(1))
- tests/stdlib/num_fib.sm:9 — likha(fib(2))
- tests/stdlib/numeric29.sm:36 — likha(fib(93))

## skalar -> ekank (lib samanvaya)
Live sites: 4. DO-NOT-TOUCH in tests/negative/: 0.
- lib/samanvaya.smlib:79 — prakriya skalar(kosh dasham a, dasham c, m, n, kosh dasham out) {
- tests/stdlib/r37_bounds.sm:49 — likha(skalar(a, 2.0, 4611686018427387905, 4, o))
- tests/stdlib/r37_bounds.sm:56 — likha(skalar(a, 2.0, 1, 4, o))
- tests/stdlib/samanvaya_skalar.sm:13 — likha(skalar(a, 2.5, 2, 2, out))

## util_chinha -> upayog_chinha (lib sadhan - see variable note)
Live sites: 22. DO-NOT-TOUCH in tests/negative/: 3.
- examples/200_madhava_series.sm:15 — vitti util_chinha = 1
- examples/200_madhava_series.sm:18 — yadi (util_chinha > 0) {
- examples/200_madhava_series.sm:24 — util_chinha = 0 - util_chinha
- examples/205_madhava_pi_kosh.sm:6 — dasham util_chinha = 1.0
- examples/205_madhava_pi_kosh.sm:10 — kosh_push(terms, util_chinha / denom)
- examples/205_madhava_pi_kosh.sm:11 — util_chinha = util_chinha * -1.0
- examples/95_t12_madhava_functions.sm:14 — vitti util_chinha = 1
- examples/95_t12_madhava_functions.sm:17 — yadi (util_chinha > 0) {
- examples/95_t12_madhava_functions.sm:23 — util_chinha = 0 - util_chinha
- lib/madhava.smlib:31 — vitti util_chinha = 1
- lib/madhava.smlib:34 — yadi (util_chinha > 0) {
- lib/madhava.smlib:40 — util_chinha = 0 - util_chinha
- lib/madhava.smlib:111 — vitti util_chinha = 1
- lib/madhava.smlib:114 — yadi (util_chinha > 0) {
- lib/madhava.smlib:120 — util_chinha = 0 - util_chinha
- lib/sadhan.smlib:40 — prakriya util_chinha(n)
- tests/stdlib/r18_sign_digits_kramgun.sm:7 — likha(util_chinha(1))
- tests/stdlib/r18_sign_digits_kramgun.sm:9 — likha(util_chinha(0 - 1))
- tests/stdlib/r18_sign_digits_kramgun.sm:11 — likha(util_chinha(0))
- tests/stdlib/util_sign.sm:3 — likha(util_chinha(5))
- tests/stdlib/util_sign.sm:5 — likha(util_chinha(-5))
- tests/stdlib/util_sign.sm:7 — likha(util_chinha(0))

## bit_gan -> ansh_gan (lib ganit - sequence with module rename)
Live sites: 5. DO-NOT-TOUCH in tests/negative/: 0.
- lib/ganit.smlib:129 — prakriya bit_gan(n) {
- tests/stdlib/math_bit_count.sm:3 — likha(bit_gan(7))
- tests/stdlib/math_bit_count.sm:5 — likha(bit_gan(8))
- tests/stdlib/math_bit_count.sm:7 — likha(bit_gan(0))
- tests/stdlib/math_bit_count.sm:9 — likha(bit_gan(15))

## asti_sorted -> asti_shrenit (lib shreni)
Live sites: 8. DO-NOT-TOUCH in tests/negative/: 0.
- examples/83_stdlib_sort.sm:12 — likha(asti_sorted(a, 6))
- examples/83_stdlib_sort.sm:22 — likha(asti_sorted(a, 6))
- examples/85_stdlib_shellsort.sm:14 — likha(asti_sorted(a, 8))
- examples/85_stdlib_shellsort.sm:24 — likha(asti_sorted(a, 8))
- lib/shreni.smlib:91 — prakriya asti_sorted(a, n) {
- lib/suchi.smlib:268 — prati asti_sorted(l[2], l[0])
- tests/stdlib/sort_is_sorted.sm:7 — likha(asti_sorted(a, 3))
- tests/stdlib/sort_is_sorted.sm:13 — likha(asti_sorted(b, 3))

## suchi_asti_sorted -> suchi_asti_shrenit (lib suchi)
Live sites: 3. DO-NOT-TOUCH in tests/negative/: 0.
- lib/suchi.smlib:267 — prakriya suchi_asti_sorted(l) {
- tests/stdlib/containers23.sm:12 — likha(suchi_asti_sorted(l))
- tests/stdlib/containers23.sm:15 — likha(suchi_asti_sorted(l))

## roop_sign_akshar -> roop_chinha_akshar (lib roop)
Live sites: 4. DO-NOT-TOUCH in tests/negative/: 0.
- lib/roop.smlib:633 — prakriya roop_sign_akshar(v, signch, out) {
- tests/stdlib/fmt_signed.sm:15 — n = roop_sign_akshar(42, 32, out)
- tests/stdlib/fmt_signed.sm:18 — n = roop_sign_akshar(0 - 42, 32, out)
- tests/stdlib/fmt_signed.sm:22 — n = roop_sign_akshar(7, 42, out)

## pehchan -> abhigyan (lib samanvaya)
Live sites: 3. DO-NOT-TOUCH in tests/negative/: 0.
- examples/209_samanvaya.sm:49 — likha(pehchan(3, id))
- lib/samanvaya.smlib:32 — prakriya pehchan(n, kosh dasham out) {
- tests/stdlib/samanvaya_pehchan.sm:8 — likha(pehchan(2, out))

## nishan -> chinha (lib samanvaya)
Live sites: 4. DO-NOT-TOUCH in tests/negative/: 0.
- examples/209_samanvaya.sm:30 — likha(nishan(a, 2))
- examples/209_samanvaya.sm:50 — likha(nishan(id, 3))
- lib/samanvaya.smlib:111 — prakriya nishan(kosh dasham a, n) {
- tests/stdlib/samanvaya_nishan.sm:8 — likha(nishan(a, 2))

## chay_khip -> chiti_khip (lib suchi (stack family))
Live sites: 4. DO-NOT-TOUCH in tests/negative/: 0.
- lib/suchi.smlib:325 — prakriya chay_khip(l, v) {
- tests/stdlib/list_stack.sm:7 — likha(chay_khip(s, 1))
- tests/stdlib/list_stack.sm:9 — likha(chay_khip(s, 2))
- tests/stdlib/list_stack.sm:11 — likha(chay_khip(s, 3))

## chay_apanay -> chiti_apanay (lib suchi)
Live sites: 5. DO-NOT-TOUCH in tests/negative/: 0.
- lib/suchi.smlib:331 — prakriya chay_apanay(l, ok) {
- tests/stdlib/list_stack.sm:21 — likha(chay_apanay(s, ok))
- tests/stdlib/list_stack.sm:23 — likha(chay_apanay(s, ok))
- tests/stdlib/list_stack.sm:25 — likha(chay_apanay(s, ok))
- tests/stdlib/list_stack.sm:30 — likha(chay_apanay(s, ok))

## chay_avalok -> chiti_avalok (lib suchi)
Live sites: 4. DO-NOT-TOUCH in tests/negative/: 0.
- lib/suchi.smlib:348 — prakriya chay_avalok(l, ok) {
- tests/stdlib/list_stack.sm:14 — likha(chay_avalok(s, ok))
- tests/stdlib/list_stack.sm:18 — likha(chay_avalok(s, ok))
- tests/stdlib/list_stack.sm:34 — likha(chay_avalok(s, ok))

## chay_rikta -> chiti_rikta (lib suchi)
Live sites: 3. DO-NOT-TOUCH in tests/negative/: 0.
- lib/suchi.smlib:362 — prakriya chay_rikta(l) {
- tests/stdlib/list_stack.sm:5 — likha(chay_rikta(s))
- tests/stdlib/list_stack.sm:27 — likha(chay_rikta(s))

## avali_nishkas -> avali_apanay (lib suchi (queue family))
Live sites: 14. DO-NOT-TOUCH in tests/negative/: 0.
- lib/suchi.smlib:437 — prakriya avali_nishkas(q, ok) {
- tests/stdlib/containers21.sm:52 — avali_nishkas(q, ok)
- tests/stdlib/containers23.sm:26 — avali_nishkas(q, nirmmita(8))
- tests/stdlib/containers_clear.sm:39 — avali_nishkas(q, ok)
- tests/stdlib/containers_clear.sm:43 — likha(avali_nishkas(q, ok))
- tests/stdlib/containers_clear.sm:51 — likha(avali_nishkas(q, ok))
- tests/stdlib/list_queue.sm:11 — likha(avali_nishkas(q, ok))
- tests/stdlib/list_queue.sm:26 — likha(avali_nishkas(q, ok))
- tests/stdlib/list_queue.sm:28 — likha(avali_nishkas(q, ok))
- tests/stdlib/list_queue.sm:30 — likha(avali_nishkas(q, ok))
- tests/stdlib/list_queue.sm:35 — likha(avali_nishkas(q, ok))
- tests/stdlib/r48_srij_fill.sm:30 — s = s + avali_nishkas(q, ok)
- tests/stdlib/r8_list_model.sm:40 — likha(avali_nishkas(q, ok))
- tests/stdlib/r9_guard_cells2.sm:35 — likha(avali_nishkas(qq, ok))

## samanvaya_akar_na -> samanvaya_akar (lib samanvaya - see predicate note)
Live sites: 6. DO-NOT-TOUCH in tests/negative/: 0.
- lib/samanvaya.smlib:23 — prakriya samanvaya_akar_na(m, n, len) {
- lib/samanvaya.smlib:68 — yadi (samanvaya_akar_na(m, n, kosh_len(a)) == 1) { prati 0 - 1 }
- lib/samanvaya.smlib:69 — yadi (samanvaya_akar_na(m, n, kosh_len(b)) == 1) { prati 0 - 1 }
- lib/samanvaya.smlib:70 — yadi (samanvaya_akar_na(m, n, kosh_len(out)) == 1) { prati 0 - 1 }
- lib/samanvaya.smlib:81 — yadi (samanvaya_akar_na(m, n, kosh_len(a)) == 1) { prati 0 - 1 }
- lib/samanvaya.smlib:82 — yadi (samanvaya_akar_na(m, n, kosh_len(out)) == 1) { prati 0 - 1 }

## laghu2 -> laghutar (lib ganit - sequence with module rename)
Live sites: 6. DO-NOT-TOUCH in tests/negative/: 0.
- examples/61_stdlib_math.sm:9 — likha(laghu2(3, 9))
- lib/ganit.smlib:25 — prakriya laghu2(a, b) {
- tests/stdlib/math_min2.sm:3 — likha(laghu2(3, 7))
- tests/stdlib/math_min2.sm:5 — likha(laghu2(9, 2))
- tests/stdlib/math_min2.sm:7 — likha(laghu2(4, 4))
- tests/stdlib/math_min2.sm:9 — likha(laghu2(-5, -1))

## adhik2 -> adhikatar (lib ganit - sequence with module rename)
Live sites: 6. DO-NOT-TOUCH in tests/negative/: 0.
- examples/61_stdlib_math.sm:11 — likha(adhik2(3, 9))
- lib/ganit.smlib:32 — prakriya adhik2(a, b) {
- tests/stdlib/math_max2.sm:3 — likha(adhik2(3, 7))
- tests/stdlib/math_max2.sm:5 — likha(adhik2(9, 2))
- tests/stdlib/math_max2.sm:7 — likha(adhik2(4, 4))
- tests/stdlib/math_max2.sm:9 — likha(adhik2(-5, -1))

## pravan2 -> pravan_dwi (lib kalana)
Live sites: 6. DO-NOT-TOUCH in tests/negative/: 0.
- examples/208_kalana.sm:27 — likha(pravan2(xs, ys, 5))
- lib/kalana.smlib:79 — prakriya pravan2(kosh dasham xs, kosh dasham ys, i) {
- tests/stdlib/kalana_slope2.sm:11 — likha(pravan2(xs, ys, 1))
- tests/stdlib/kalana_slope2.sm:13 — likha(pravan2(xs, ys, 0))
- tests/stdlib/r11_kalana_edges.sm:14 — likha(pravan2(xs, ys, 2))
- tests/stdlib/r11_kalana_edges.sm:15 — likha(pravan2(xs, ys, 1))

## roop_ank_aadhar2 -> roop_ank_aadhar_dwi (lib roop)
Live sites: 14. DO-NOT-TOUCH in tests/negative/: 0.
- lib/roop.smlib:150 — prakriya roop_ank_aadhar2(v, base, out) {
- lib/roop.smlib:213 — prati roop_ank_aadhar2(v, 10, out)
- lib/roop.smlib:217 — prati roop_ank_aadhar2(v, 16, out)
- lib/roop.smlib:225 — prati roop_ank_aadhar2(v, 8, out)
- lib/roop.smlib:229 — prati roop_ank_aadhar2(v, 2, out)
- lib/roop.smlib:453 — vitti n = roop_ank_aadhar2(v, 10, tmp)
- lib/roop.smlib:606 — n = roop_ank_aadhar2(val, 10, tmp)
- lib/roop.smlib:644 — n = roop_ank_aadhar2(val, 10, tmp)
- tests/stdlib/fmt_int_base.sm:37 — n = roop_ank_aadhar2(35, 36, out)
- tests/stdlib/fmt_int_base.sm:40 — n = roop_ank_aadhar2(36, 36, out)
- tests/stdlib/fmt_int_base.sm:46 — n = roop_ank_aadhar2(255, 1, out)
- tests/stdlib/fmt_min.sm:5 — vitti n = roop_ank_aadhar2(minv, 10, out)
- tests/stdlib/fmt_min.sm:14 — vitti m = roop_ank_aadhar2(minv, 16, out)
- tests/stdlib/fmt_min.sm:46 — vitti b = roop_ank_aadhar2(minv, 2, out)

## nirnaya2 -> nirnaya_dwi (proposed here from the body, table gives no name)
Live sites: 4.
- lib/samanvaya.smlib:122 — prakriya nirnaya2(kosh dasham a) {
- examples/209_samanvaya.sm:31 — likha(nirnaya2(a))
- tests/stdlib/samanvaya_nirnaya2.sm:8 — likha(nirnaya2(a))
- tests/stdlib/samanvaya_nirnaya2.sm:15 — likha(nirnaya2(ident))
Body: prati a[0] * a[3] - a[1] * a[2] — the 2x2 determinant. _dwi follows the existing
roop_dwi / dwi_anwesh pattern.

## nirnaya3 -> nirnaya_tri (proposed here from the body, table gives no name)
Live sites: 4.
- lib/samanvaya.smlib:127 — prakriya nirnaya3(kosh dasham a) {
- examples/209_samanvaya.sm:44 — likha(nirnaya3(d))
- tests/stdlib/samanvaya_nirnaya3.sm:13 — likha(nirnaya3(ident))
- tests/stdlib/samanvaya_nirnaya3.sm:25 — likha(nirnaya3(sing))
Body: cofactor expansion of a 3x3 matrix — the 3x3 determinant. _tri is the parallel
of _dwi for three; no _tri suffix exists yet in lib, but dwi_anwesh shows the pattern.

## Devanagari fixes (10 rows, 1 line each, plus 1 baseline line each)
All in lang/sanskrit.lang only. Other packs use their own scripts, not Devanagari,
so they are not affected. No .sm file uses the old Devanagari words directly.
- anya: lang/sanskrit.lang: अन्यत्र anya -> अन्य anya; tests/r66/baseline_packs.json:7
- chakra: lang/sanskrit.lang: पुनरावर्तन chakra -> चक्र chakra; tests/r66/baseline_packs.json:9
- prati: lang/sanskrit.lang: प्रतियाति prati -> प्रति prati; tests/r66/baseline_packs.json:10
- agrim: lang/sanskrit.lang: उद्देश्य agrim -> अग्रिम agrim; tests/r66/baseline_packs.json:17
- mala: lang/sanskrit.lang: पङ्क्ति mala -> माला mala; tests/r66/baseline_packs.json:20
- ganana: lang/sanskrit.lang: सृजन ganana -> गणना ganana; tests/r66/baseline_packs.json:21
- abhava: lang/sanskrit.lang: निषेध abhava -> अभाव abhava; tests/r66/baseline_packs.json:22
- satya: lang/sanskrit.lang: परिग्रह satya -> सत्य satya; tests/r66/baseline_packs.json:25
- tak: lang/sanskrit.lang: पर्यन्त tak -> तक् tak; tests/r66/baseline_packs.json:27
- yantra: lang/sanskrit.lang: निष्क्रिय yantra -> यन्त्र yantra; tests/r66/baseline_packs.json:32
Table section 1 says 8 Devanagari rows, section 2 lists 10, section 7 counts 10.
The list has 10. The 8 is a miscount in the table, not a missing row.

## ganit -> ganan: what the module rename actually touches
- Rename the file lib/ganit.smlib -> lib/ganan.smlib (no other module file changes).
- Change every `yoj ganit` line to `yoj ganan` (live sites listed under ganit above,
  41 live; 8 more in tests/negative/ are DO-NOT-TOUCH).
- The module's functions are mostly BARE names (varg, ghan, ghat, kramgun, vardh,
  yog_tak, mahattam, laghuttam, dvigun, trigun, bit_gan, laghu2, adhik2, kuttaka).
  They do NOT change with the module rename. Only two functions carry the module
  prefix and would be left stale if the module renames and they do not:
  ganit_yadricch (lib/ganit.smlib:148, calls in tests/stdlib/breadth26.sm,
  r8_list_model.sm, r8_map_model.sm, r8_split_model.sm) and ganit_seemit
  (lib/ganit.smlib:157, calls in tests/stdlib/breadth26.sm). If the prefix convention
  is to hold, they become ganan_yadricch and ganan_seemit in the same commit.
  Note ganit_seemit is a byte-identical duplicate of ank.seemit (both clamp);
  the module rename does not fix that duplication.
- bit_gan, laghu2, adhik2 live in this module, so their renames must be applied
  in the same commit as the module rename, or the intermediate tree will have
  ganit.ansh_gan / ganan.bit_gan confusion in docs and tests.

## yog shadowing in examples/05_func_params.sm (not a rename, a break)
- examples/05_func_params.sm:2 defines prakriya yog(a, b) (scalars, returns a+b).
- lib/shreni.smlib:62 defines prakriya yog(a, n) (array + count, returns the sum).
- The file currently has no yoj line, so it compiles. Adding `yoj shreni` breaks it:
  measured on this main: `Sutram Error: punah prakriya paribhasha: yog`, exit 1.
  Sutram imports by inlining (yoj expands the module into the program), so there is
  no module qualification and no shadowing: two functions with one name are a
  duplicate definition, regardless of different arity. If the example is ever to
  import shreni, its local yog must be renamed first (e.g. yog_dwi for two scalars,
  or the example must call shreni.yog by a different name — which does not exist
  in the language). Until then, the example is safe only because it does not import
  shreni, and that fragility should be a comment in the file, not assumed knowledge.

## blend -> mishr, mixed -> mishrit (examples 92/93/94)
- blend function sites (6): examples/93_t12_float_functions.sm:12 (definition), :25, :29;
  examples/94_t12_float_functions.sm:12, :30, :36. Renaming both files' blend to mishr
  compiles and outputs are identical (measured on this main by renaming the full file).
- mixed function sites (6): examples/93:16, :26, :27; examples/94:16, :31, :32.
  Renaming mixed to mishrit in the same files also compiles with identical output.
- examples/92_t12_dasham_float.sm has a VARIABLE named mixed (lines 21, 22, 24), not a
  function. It is a different namespace and does not need renaming; a mechanical sed
  would rename it harmlessly but pointlessly.
- mishrit follows the existing -it participle pattern in lib: seemit, vargit,
  surakshit, chinhit. mishr (blend, verb/noun) vs mishrit (mixed, participle) are
  distinct strings, so the two functions do not collide. The CHANGELOG v389 claim
  that these renames were applied is NOT in the tree: examples 92/93/94 still use
  blend/mixed on this main. The rename is still to be done, not already done.

## Notes that change a verdict (read before applying)

1. likh / shabda -> likha are merges, not renames. likh is raw write (arity 2,2,
   address+byte, .pp_writemem in src/sutram_compiler.asm); likha is print (arity
   1-3, dispatch by type); shabda is print-a-string-variable (arity 1,1). likha(s)
   for a string variable prints its ADDRESS (measured in R46 and again in R49: s =
   4196833 for "hello"), while shabda(s) prints hello. Merging shabda into likha
   without first fixing likha's string dispatch breaks every string print
   (examples/44_shabda.sm, examples/46_language_reference.sm). Merging likh into
   likha requires an arity/type dispatch for raw write that does not exist.
   Verdict: do not apply as renames; design the dispatch first.

2. paadh does not duplicate pad. pad is arity 1,1; paadh is arity 3,3 (fd, buf,
   count, sys_read) and is the only read path used by lib/patra.smlib:39. Their
   Devanagari forms also differ (pad = पाद, paadh = पाठ). Removing paadh breaks
   patra's read. If the goal is one read word, pad must take over paadh's 3-arg
   semantics in the compiler, which is a compiler change, not a deletion.

3. kosh_enqueue -> kosh_purva_yuj is backwards. Compiler source says it plainly:
   `bn_koshenqueue db "kosh_enqueue", 0 ; FIFO append = kosh_push` and dequeue is
   `first element (FIFO)`. Enqueue appends to the BACK (tail); dequeue removes from
   the FRONT. purva means front, so kosh_purva_yuj would promise front-insertion
   and deliver back-append. kosh_purva_apanay for dequeue is correct (front removal).
   For enqueue, the direction-consistent name is kosh_ant_yuj (ant = end) or
   kosh_pashchat_yuj (pashchat = after/behind). Do not apply kosh_purva_yuj.

4. maap vs aayam. The lib length convention is maap: anukram_maap_ashtak,
   khand_maap, nighantu_maap, rakh_maap, suchi_maap, avali_maap, varna_maap
   (7 functions). vartani_aayam is the outlier that uses aayam for string length.
   mala_aayam and kosh_aayam follow the outlier, not the convention. If maap is
   the convention, the consistent names are mala_maap and kosh_maap; if aayam is
   adopted as the builtin length word, say so explicitly, because it creates two
   length words across the builtin/lib boundary. aayam does not collide with
   anything in the mala module (mala has no aayam function), so this is a
   convention question, not a collision.

5. kosh_rikt / chiti_rikta spelling. Existing empty words are rakh_rikta and
   suchi_rikta (rikta, with final a). kosh_rikt and chiti_rikta drop the final a,
   following chay_rikta, which already has the dropped form. Under the table's
   own complete-word rule, the consistent forms are kosh_rikta and chiti_rikta.
   Applying kosh_rikt as proposed perpetuates the fragment in a new name.

6. kosh_khip / kosh_apanay do NOT clash with suchi_ / chay_ families. Full names
   differ (kosh_khip vs suchi_khip vs chay_khip; kosh_apanay vs suchi_apanay vs
   chay_apanay vs rakh_apanay), and sharing the stem across prefixes is the
   established pattern (khip = insert/append, apanay = remove, maap = measure).
   kosh_* are builtins in the compiler table, not lib functions, but call sites
   use the same bare-name form, so the distinction does not create a clash — it
   only means the compiler table must change in the same commit as the call sites.

7. ganan vs ganana: NO compiler collision, with a human-confusion caveat. ganan
   as a bare identifier compiles and runs (measured: prakriya ganan(a,b) -> 7),
   `yoj ganan` with a lib/ganan.smlib file compiles and runs (varg(5) = 25), and
   a program using BOTH `yoj ganan` and the `ganana` enum keyword compiles and
   runs (RED = 1, varg(5) = 25). The lexer distinguishes the exact token from its
   prefix (see R43). The remaining risk is human: ganan (गणन) and ganana (गणना)
   differ by one letter / one matra, and a reader can misread one for the other.
   vyavahar avoids that risk but is 8 letters and says 'everyday practice', not
   'elementary arithmetic' as directly as ganan says 'counting'. ganan is the
   better name; the confusion risk should be a comment in the module header,
   not a reason to reject it.

8. util_chinha: the 22 live sites are NOT all call sites. The function is defined
   at lib/sadhan.smlib:40; true calls are in tests/stdlib/r18_sign_digits_kramgun.sm
   and tests/stdlib/util_sign.sm (6 lines). The rest are local VARIABLES named
   util_chinha in lib/madhava.smlib and examples 200/205/95 (a sign variable,
   1 / -1), plus comment mentions. Renaming the function does not require
   renaming those variables; a mechanical sed would rename them harmlessly
   (they are locals), but they are not sites to change for compilation.

9. samanvaya_akar_na -> samanvaya_akar is misleading as proposed. The function
   returns 1 for a BAD shape and 0 for a good one (lib/samanvaya.smlib:23); it does
   not return a shape. Under the asti_ convention for booleans, the consistent
   name is asti_samanvaya_akar or samanvaya_akar_dosh (shape-error). Applying
   samanvaya_akar as-is gives a predicate the name of a value.

10. nishan -> chinha reuses a word with a different meaning. chinha already means
    sign in roop_chinha_akshar and (proposed) upayog_chinha. nishan's body is a
    matrix trace (sum of the diagonal, lib/samanvaya.smlib:111), not a sign.
    There is no exact collision (no function named chinha exists), but the bare
    name chinha in samanvaya would sit beside roop's sign functions with a
    different meaning. That is a homonym across modules, not a collision, and
    it should be decided as a Sanskrit/semantic question, not hidden in a rename.

11. laghu2 / adhik2 are min/max, not predicates. Bodies return the smaller /
    larger value (lib/ganit.smlib:25,32), not a boolean. laghutar (smaller) and
    adhikatar (greater) fit the bodies exactly; the table's gloss 'less-than,
    greater-than' understates them, but the proposed names are right.

12. pravan2 is the second derivative, not a second slope. pravan_dwi follows the
    _dwi pattern (roop_dwi, dwi_anwesh), but _dwi alone does not say 'derivative'.
    Apply it with a comment in lib/kalana.smlib stating that dwi here means the
    second derivative, or the name will be read as 'the second point's slope'.

13. kunji / kunjika and seemit / seema have no proposal in the table, so they
    cannot be given a collision verdict for a name that does not exist yet.
    What the code shows: kunji_* (nighantu_kunji_gudh, nighantu_kunji_sam) are
    INTERNAL helpers in lib/nighantu.smlib, while kunjika_* (nighantu_kunjika,
    nighantu_kunjika_ashtak) are PUBLIC and called from lib/sangrah.smlib as well.
    Unifying them by renaming the public side would touch external call sites;
    unifying by renaming the internal side is small and internal-only. seemit
    (ank.seemit, a clamp) and seema (a bound, as in yog_seema and 'seema atikram'
    errors) are different parts of speech (participle vs noun), not duplicates;
    the real duplication is ganit_seemit, byte-identical to ank.seemit (see ganit note).

## Splitting: one commit or several?

- Library renames with live sites under 20 (every library rename except
  util_chinha's variable noise) are safe as one commit each, or grouped by module,
  with a suite + gates run after. No library rename needs splitting by file: a
  half-renamed function is a compile error in every file that still uses the old
  name, so splitting by file only works if both names are kept as aliases, which
  defeats the rename.
- Builtin renames must NOT be split by file for the same reason, and kosh_push
  (343 live sites) and kosh_len (60 live) are the largest. They are still safe as
  one mechanical commit each (compiler table + call sites + error strings),
  because the change is identifier-only and the compiler will reject any missed
  site as an unknown builtin. Splitting kosh_* by file would require keeping both
  the old and new builtin names in the compiler table during the transition.
- The kosh_* family (9 renames) can go in one commit or nine; one family commit is
  safer than nine partial ones, because tests use several kosh builtins together
  and a partial family leaves mixed old/new names in the same test files.
- ganit -> ganan must go with bit_gan, laghu2, adhik2 (same module) in one commit,
  and with ganit_yadricch / ganit_seemit if their prefixes are updated.
- Devanagari fixes are 1 line each and can go in one commit; they touch no .sm files.

## Count reconciliation (table vs brief vs measured)

- Table section 7 claims: keywords 3, Devanagari 10, builtins 15, modules 1,
  library 22, total 51. Measured from the table's own lists: keywords 3,
  Devanagari 10, builtins 17 (vartani_cat, pankti_len, sankhya_dot, likha_fmt +
  9 kosh_* + 4 net* = 17, not 15), modules 1, library 21 (not 22), total 52.
  The brief's '31 library renames' is not the table's library list: 21 library +
  10 Devanagari = 31, which is the only combination that gives 31. It is not 31
  library functions. The TSV has 58 rows because it also includes the 2 stem
  questions, the yog shadowing question, and the blend/mixed question, which are
  not renames in the table's counted lists.
- Keyword count in the brief (39) does not match the compiler: the compiler table
  has 32 Latin keyword strings; the table's 42 rows include builtins (likha,
  likh, pad, grahan, shabda, nirmmita, sthagita, dvaram, band) counted as keywords
  and one duplicate (paadh). Use 32 keywords, 45 builtins, 24 modules, 305 lib
  functions as the collision sets; those are the measured numbers on this main.

## Non-code surfaces (must change with the renames, not in the lists above)

- lang/*.lang: pankti_len appears as पङ्क्तिदैर्घ्य in lang/sanskrit.lang and
  पंक्तिलंबाई in lang/gujarati.lang; kosh_* builtins have Devanagari aliases in
  lang/sanskrit.lang (कोशपुष् etc.) and in other packs. A builtin rename that does
  not update the pack aliases leaves the old name working in that pack and the
  new name unknown there.
- tests/r66/test_prepare_review.py lists builtins explicitly (including kosh_*,
  likh, paadh); tests/r66/baseline_packs.json and tests/r68/baseline_packs.json
  embed pack mappings. Update them with the renames, or the pack tests will fail
  on the old names.
- docs/*.md (VOCABULARY-TABLE.md itself, PROJECT-MASTER, scorecard, etc.) name the
  old functions in prose. Those are documentation updates, not compilation sites,
  and are not counted in the TSV; leaving them creates stale claims, which the
  stale-claims gate reports but does not fail on.

No tree changes were made for this round. All measurements are from reading and
from compiling small test programs against the committed compiler on this main.
`git push` has no credentials here, as before; delivery is via the GitHub API.