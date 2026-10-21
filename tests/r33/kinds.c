/* ROUND-33: the foreign side of the FFI kinds test, freestanding, no libc:
 *   gcc -c -O2 -ffreestanding -fno-asynchronous-unwind-tables -fno-pic \
 *       -fno-stack-protector kinds.c -o kinds.o
 * kinds.o is committed, so the test does not need a C compiler. */
double sutram_k_half(double x) { return x / 2.0; }
double sutram_k_scale(double x, long n) { return x * n; }
/* integers and doubles interleaved: rdi, xmm0, rsi, xmm1, rdx, xmm2 */
double sutram_k_mix(long a, double b, long c, double d, long e, double f) {
    return a + b * 10.0 + c * 100.0 + d * 1000.0 + e * 10000.0 + f * 100000.0;
}
long sutram_k_strlen(const char *s) {
    long n = 0;
    while (s[n]) n++;
    return n;
}
long sutram_k_sum(const long *p, long n) {
    long t = 0;
    for (long i = 0; i < n; i++) t += p[i];
    return t;
}
double sutram_k_fsum(const double *p, long n) {
    double t = 0;
    for (long i = 0; i < n; i++) t += p[i];
    return t;
}
void sutram_k_set(long *p, long i, long v) { p[i] = v; }
void sutram_k_nothing(void) { }
long sutram_k_trunc(double x) { return (long)x; }
