# Round 102 WS2 — Smallest checkable Windows FFI string boundary

**Proposal only, not accepted syntax or implemented code.** The top R101 gap is pointer/string provenance and extent, not the already working Microsoft calling convention. Windows FFI source was checked at `claude/windows-ffi` commit `d29fece4fd38189e59a3fcb37e0c6392495559f6`; `src/r32_ffi.inc` blob `67cfd8562d53934ecd56e8edecbcb0355c134fb8` explicitly supports v2 `windows-x86_64-msabi`, 0..6 arguments, positional GP/XMM registers and stack/shadow space. The proposed feature does not replace that working port.

## 1. Deliverable: `cstr_ro` for direct string literals only

The first implementable profile accepts **only a direct compiler-known string literal** at a `cstr_ro` argument. It checks the decoded literal bytes, creates/stores a final NUL, and passes the address of that exact backing object. It rejects raw integers (including zero), `ptr` variables, kosh, slices, concatenated or dynamically computed strings, and plain variables until their extent/lifetime can be proved separately. Reject embedded NUL rather than silently returning a prefix; reject malformed UTF-8 in this profile. Empty string is allowed.

This narrow restriction matters: a compiler can prove a literal's byte extent and static backing lifetime without pretending that an arbitrary integer address is safe. It **does not** prove arbitrary C code respects `const`, never overreads, never retains addresses, or matches the declared prototype. The foreign body remains trusted/unsafe. Do not advertise general memory safety, ownership or bounds enforcement from this token alone. Existing `ptr` semantics remain explicitly low-level.

## 2. Exact sidecar bytes and version

```
sutram-ffi-v3|windows-x86_64-msabi
s_len|1|cstr_ro|i64|sutram_w_cstrlen
```

The header is **35 bytes**, ASCII, including final LF:

```
73 75 74 72 61 6d 2d 66 66 69 2d 76 33 7c
77 69 6e 64 6f 77 73 2d 78 38 36 5f 36 34 2d 6d 73 61 62 69 0a
```

Byte 12 is ASCII `3`; byte 13 is `|`; bytes 14..33 name the ABI; byte 34 is LF. `cstr_ro` is exactly seven bytes **`63 73 74 72 5f 72 6f`**. The five fields remain `local|arity|argument_kinds|return_kind|external_symbol`, one LF-terminated record per declaration, with the existing 8192-byte and 64-record limits. Arity is exactly one digit 0..6. Local identifiers are ASCII `[A-Za-z_][A-Za-z0-9_]*`, length 1..63; external symbols length 1..127, matching the actual native parser. No BOM, CR, spaces, NUL, comments, duplicate local/foreign names, extra fields or ignored suffixes.

V1 retains strict Linux i64-only semantics. V2 retains its current kinds/targets. V3, **only after approval and implementation**, adds `cstr_ro` as an **argument** kind to the v2 vocabulary; `cstr_ro` as a return kind is refused. The first v3 target is Windows; Linux v3 should remain explicitly unsupported until separately gated. Unknown v3 currently remains a header error; do not mark these examples as accepted by today's compiler. No implicit reinterpretation of v2 or its raw `ptr` kind.

A future `buf_ro@N`/`buf_rw@N` is **not part of this smallest profile**. It needs verified byte length, actual allocation extent, mutability, alias and lifetime tracking. In particular kosh length counts elements, not bytes. The model deliberately refuses these tokens rather than suggesting bounds support already exists.

## 3. Compiler table and bytes emitted

The existing in-memory FFI record is four qwords: local-name pointer at +0, arity at +8, external-name pointer at +16, packed kinds at +24. The packed-kind qword has argument tags at byte offsets 0..5, result tag at 6, reserved byte at 7. Existing tags are i64=0, f64=1, ptr=2, void=3. **Proposed internal tag 4 means cstr_ro**; it is not a new on-disk object field. For the one-argument i64-result sample, the kind bytes are:

```
04 00 00 00 00 00 00 00
```

The current three-character kind parser cannot accept seven-character `cstr_ro` unchanged. Use delimiter-bounded exact token matching, rejecting partial names. Validate literal provenance and bytes before emitting a call or publishing an output object. Existing source-located `E_ARITY` and `E_FFI_KIND` must still point to the actual call/argument; rejected compiles leave no new object and preserve any prior output file. Do not add a fake FUNCDEF or zero-return stub.

Literal backing bytes are exact decoded UTF-8, followed by **one** `00` byte:

| Source value | Machine bytes |
|---|---|
| `"abc"` | `61 62 63 00` |
| `""` | `00` |
| `"नमस्ते"` | `e0 a4 a8 e0 a4 ae e0 a4 b8 e0 a5 8d e0 a4 a4 e0 a5 87 00` |

No UTF-16 conversion, byte-to-qword repacking or unbounded NUL scan. The compiler knows `payload_length+1` before codegen. Verify that length addition and final object offsets fit the emitter's bounds. Store the literal in the normal program string backing region; keep it live for the whole call. The C contract is `int64_t sutram_w_cstrlen(const char *p)`, returning a **byte count**, not code-point count. On Windows do not use `long` as an i64 surrogate: use an explicitly 64-bit C type.

## 4. Windows register, stack and relocation details

A cstr address is in the integer/pointer class, **by argument position**: argument 1 RCX, 2 RDX, 3 R8, 4 R9; arguments 5 and 6 at caller `[rsp+32]`, `[rsp+40]` immediately before CALL. A float in another position uses that position's XMM register. For `(i64,f64,cstr_ro,f64)` the registers are **RCX, XMM1, R8, XMM3**, not SysV independent streams.

Reuse the existing verified Windows 0..6-argument alignment scheme, not the Linux shim. At a general call site:

```
mov r11,rsp       ; 49 89 E3
and rsp,-16       ; 48 83 E4 F0
push r11          ; 41 53
sub rsp,56        ; 48 83 EC 38
; store optional arguments 5/6 at +32/+40, leaving +0..31 for shadow
call foreign      ; E8 <signed disp32>
add rsp,56        ; 48 83 C4 38
pop rsp           ; 5C
```

Before CALL, RSP is 0 modulo 16. The saved original RSP lives at `[rsp+56]`, above shadow space, both stack-argument slots and padding; it is not stored inside the callee-owned 32-byte home area. Return i64 is RAX. A future mixed signature must evaluate/stage arguments without later expressions clobbering earlier values; use the existing staging path and native nested-call tests.

The caller's **SUTRAMO2** object defines no `s_len`/foreign stub. It records a named four-byte call displacement for **`sutram_w_cstrlen`**, the external name. Patch using the existing target-minus-next-instruction formula, with signed reach and field bounds validated. The seven-byte sidecar token is never copied into machine-code ABI metadata. No object-format version change is required for this argument restriction.

## 5. What the COFF converter can and cannot establish

Keep the existing NASM `sutram-coff2smo` reader: x64 COFF, bounded code/read-only data, supported internal REL32 family relocations, code symbol offset/range and exact external symbol. A simple self-contained C length loop needs neither a DLL nor a CRT call. Reject undefined callees, unsupported writable data/TLS/unwind/directives and bad metadata as today. Keep PE object alignment rules and SUTRAMO2 unchanged.

COFF symbol names and function flags **do not reveal `const char*`, return width, ownership, arity, encoding or read length**. Pair the sidecar with a reviewed producer header/manifest (and exact object hash) or clearly describe the declaration as an unchecked promise about the C body. Do not call this whole-program memory safety merely because literal arguments are statically verified.

## 6. Native acceptance list for the owner / Claude

- Direct literals `"abc"`, empty, and known UTF-8 produce exact byte counts through the real Windows compiler, converter and linker, under both object and separate modes. No new external runtime or default-path changes.
- Embedded NUL and malformed UTF-8 are rejected before output. Integer, raw ptr, variable, kosh, slice, dasham and result-kind `cstr_ro` are rejected with the correct source/sidecar location.
- Wrong arity 0/2 for the one-argument declaration yields `E_ARITY`; no stub, no wrong local-name relocation. Unknown v3 on an old compiler fails closed. Existing v1/v2 accepted and rejected fixtures are unchanged.
- Test cstr in **all six positions**, interleaved with f64, with a trusted C fixture that reports values; verify stack/shadow alignment and nested calls. Do not dereference deliberately invalid pointers.
- Match sidecar/object/producer metadata hashes, preserve existing output on compile/converter/link failures, and rerun normal-path byte identity, FFI fuzz/corpus and non-elevated Windows acceptance at the exact candidate commit.

**Executed this round:** Python byte/grammar/provenance/stack models inside `ROUND-102-CONTROLS.py`, with exact raw stdout. They are part of the **69 PASS / 0 FAIL** control groups. **Native Windows/Sutram v3 tests: NOT_RUN; feature: NOT_IMPLEMENTED.** Only the proposed first literal-only profile has model coverage; arbitrary buffer ownership remains out of scope.
