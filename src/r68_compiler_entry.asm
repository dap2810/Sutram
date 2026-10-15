; R68 review entry. Build this file, not the bare inherited compiler, for
; the NEW host-side diagnostics. Existing generated-code paths stay intact.
; First run tools/r68_prepare_review.py to verify the accepted input blobs.
; This instruction macro changes only two compiler-host CALL sites/families.
; It is not a runtime wrapper, interpreter, or a new backend.
%macro call 1
    %ifidni %1,lex
        call r68_prelex_validate
        call lex
    %elifidni %1,parse_primary
        call r68_guard_value_start
        call parse_primary
    %else
        call %1
    %endif
%endmacro
%include "src/sutram_compiler.asm"
%unmacro call 1
%include "src/r68_unicode_helpers.inc"
%include "src/r68_diagnostics.inc"
