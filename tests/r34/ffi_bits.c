/* ROUND-34: the bits of a double, through the FFI in both directions, for -0.0,
 * infinities, NaNs and subnormals. Freestanding, no libc:
 *   gcc -c -O2 -ffreestanding -fno-asynchronous-unwind-tables -fno-pic \
 *       -fno-stack-protector ffi_bits.c -o ffi_bits.o
 * ffi_bits.o is committed (force-added: .gitignore has *.o), so the test needs no C compiler. */
typedef union { double d; long l; } bits;
long sutram_b_of(double x) { bits u; u.d = x; return u.l; }
double sutram_b_from(long l) { bits u; u.l = l; return u.d; }
/* a double that goes Sutram -> C -> Sutram -> C unchanged */
long sutram_b_twice(double x, long n) { bits u; u.d = x; return u.l ^ n; }
