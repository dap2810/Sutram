/* R97 negative host control: must reject unresolved helper/relocations. */
extern long missing_helper(long);
long sutram_ffi_add(long a, long b) { return missing_helper(a+b); }
