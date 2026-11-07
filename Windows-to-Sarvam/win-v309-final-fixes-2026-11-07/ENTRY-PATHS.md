# Expression entry audit at 664ff188

The concurrent [R208 review](../../ChatGPT-to-Sarvam/ROUND-208-V309-ENTRY-PATH-AND-LOCK-REVIEW.md) identified a real bypass. The original compiler failed 21 of the expanded 42 global/local cases. The repaired compiler passes all 42 on Windows and Linux. Negative cases require a nonzero compiler exit, the specific diagnostic, and no output executable; valid controls execute natively.

The fix validates each global initializer before lowering and applies `r134_holds_kosh` at the global store. Global expressions run with empty local-name analysis, then mukhya's local analysis is established. The validator has its own traversal stack because return-kind analysis uses `rfx2_stack`. Exhausting the node or stack budget now refuses compilation with `E_VISHLESHANA_SEEMA`; the former node-budget branch silently returned success. A disposable Windows host with only the node budget lowered to zero verifies refusal for local and global inputs. This is forced-path coverage, not proof that ordinary inputs reach the original 200000-node bound.

The direct `call gen_expr` sites in `src/sutram_compiler.asm` were enumerated and inspected:

| Caller | Calls | Input / validation |
| --- | ---: | --- |
| `gen_stmt` | 23 | User statement expressions; validator runs before dispatch |
| `r56_gen_global_initializers` | 1 | User global initializer; now explicitly validated before emission and global ownership check |
| `gen_expr` | 98 | Recursive expression lowering below those validated roots |
| `gen_typed_call_arg` | 2 | Arguments below a validated call; retains parameter ownership checks |
| `r103_emit_budget_checks` | 1 | Compiler-created internal mark-variable AST |
| `r82_emit_check` | 1 | Compiler-created diagnostic line-number call |
| `r80_emit_div_fatal` | 1 | Compiler-created diagnostic line-number call |
| `r80_emit_likha_tail` | 1 | Compiler-created diagnostic string call |
| `emit_array_bounds_check` | 1 | Compiler-created bounds-error string call |
| `emit_kosh_empty_check_r9` | 1 | Compiler-created empty-kosh diagnostic call |
| `r127_emit_grow_check` | 1 | Compiler-created growth diagnostic call |
| `r65_emit_number` | 1 | Compiler-created numeric diagnostic call |
| `r121_emit_image_check` | 1 | Compiler-created image-error string |

This is a source audit of these entry points plus executable regressions, not a general memory-safety or complete language proof. No frozen expectation or release source-integrity pin was changed. Rebuild/re-pin the canonical release only after independent acceptance of the review branch.
