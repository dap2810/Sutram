/* Negative: undefined helper would require an additional object. */
extern long missing_helper(long);
long sutram_ffi_add(long a, long b) { return missing_helper(a + b); }
