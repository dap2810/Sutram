/* ROUND-32: refused by sutram-elf2smo: it calls out, so it has a relocation. */
extern long missing_helper(long);
long sutram_ffi_add(long a, long b) { return missing_helper(a + b); }
