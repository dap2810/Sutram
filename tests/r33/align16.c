/* ROUND-33: refused by sutram-elf2smo: fabs needs a 16-byte constant (.rodata.cst16),
 * which the linker, laying objects end to end, could not keep 16-byte aligned. */
double sutram_k_abs(double x) { return __builtin_fabs(x); }
