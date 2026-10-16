; R71 explicit experimental compiler entry, retaining the R68 diagnostics.
; First verify reviewed inputs using tools/r71_prepare_review.py.
; SUTRAM_R71_UNSAFE_BOUNDARY adds the tested token-boundary pass after lex.
; The ordinary R69 release build continues to select r68_compiler_entry.asm.
; No new parser, backend, interpreter or generated runtime dependency.
%macro call 1
    %ifidni %1,lex
        call r68_prelex_validate
        call lex
%ifdef SUTRAM_R71_UNSAFE_BOUNDARY
        call r71_after_lex
%endif
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

%ifdef SUTRAM_R71_UNSAFE_BOUNDARY
%include "src/r71_unsafe_tokens.inc"
%include "src/r71_unsafe_integration.inc"
%endif
