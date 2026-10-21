/* ROUND-32: the foreign side of the FFI test, built freestanding, no libc:
 *   gcc -c -O2 -ffreestanding -fno-asynchronous-unwind-tables -fno-pic \
 *       -fno-stack-protector foreign.c -o foreign.o
 * foreign.o is committed, so the test does not need a C compiler. */
long sutram_ffi_add(long a, long b) { return a + b; }
long sutram_ffi_neg(long a) { return -a; }
long sutram_ffi_mix(long a, long b, long c, long d, long e, long f) {
    return a + 2 * b + 3 * c + 4 * d + 5 * e + 6 * f;
}
/* rsp mod 16 on entry: 8 when the caller kept the C ABI's 16-byte alignment */
long sutram_ffi_rsp(void) {
    long r;
    __asm__ volatile("mov %%rsp, %0" : "=r"(r));
    return r & 15;
}
