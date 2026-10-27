/* ROUND-35: the foreign side of the Windows FFI test - the Microsoft x64 ABI,
 * freestanding, no libc. int64_t, never long: Windows is LLP64 (long is 32 bits).
 *   gcc -c -O2 -ffreestanding -fno-asynchronous-unwind-tables -fno-stack-protector winffi.c -o winffi.obj
 * winffi.obj is committed (tests/r35/OBJECTS.md), so the test needs no C compiler. */
#include <stdint.h>

int64_t w_zero(void) { return 42; }
int64_t w_one(int64_t a) { return a * 3; }
/* each argument weighted by its position, so a swap shows */
int64_t w_four(int64_t a, int64_t b, int64_t c, int64_t d) { return a * 1000 + b * 100 + c * 10 + d; }
int64_t w_five(int64_t a, int64_t b, int64_t c, int64_t d, int64_t e) {
    return a * 10000 + b * 1000 + c * 100 + d * 10 + e;          /* e: the stack, [rsp+40] at entry */
}
int64_t w_six(int64_t a, int64_t b, int64_t c, int64_t d, int64_t e, int64_t f) {
    return a * 100000 + b * 10000 + c * 1000 + d * 100 + e * 10 + f;
}
/* THE case: rcx, XMM1, r8, XMM3 - by position. System V's rule would put b in xmm0
 * and c in the second integer register, and return a different number. */
double w_mixed(int64_t a, double b, int64_t c, double d) { return a * 1000.0 + b * 100.0 + c * 10.0 + d; }
/* doubles first: xmm0, rdx, xmm2, r9 */
double w_fmix(double a, int64_t b, double c, int64_t d) { return a * 1000.0 + b * 100.0 + c * 10.0 + d; }
/* three integers then a double: the double is xmm3 (System V: xmm0) */
double w_i3f(int64_t a, int64_t b, int64_t c, double d) { return a * 1000.0 + b * 100.0 + c * 10.0 + d; }
/* six, mixed, two on the stack: rcx xmm1 r8 xmm3 [rsp+40] [rsp+48] */
double w_mix6(int64_t a, double b, int64_t c, double d, int64_t e, double f) {
    return a + b * 10.0 + c * 100.0 + d * 1000.0 + e * 10000.0 + f * 100000.0;
}
double w_f4(double a, double b, double c, double d) { return a * 1000.0 + b * 100.0 + c * 10.0 + d; }
double w_f6(double a, double b, double c, double d, double e, double f) {
    return a + b * 10.0 + c * 100.0 + d * 1000.0 + e * 10000.0 + f * 100000.0;
}
/* 16-byte constants (xorpd / andpd read them aligned) */
double w_neg(double x) { return -x; }
double w_abs(double x) { return x < 0 ? -x : x; }
int64_t w_trunc(double x) { return (int64_t)x; }
int64_t w_strlen(const char *s) { int64_t n = 0; while (s[n]) n++; return n; }
int64_t w_sum(const int64_t *p, int64_t n) { int64_t t = 0; for (int64_t i = 0; i < n; i++) t += p[i]; return t; }
double w_fsum(const double *p, int64_t n) { double t = 0; for (int64_t i = 0; i < n; i++) t += p[i]; return t; }
void w_set(int64_t *p, int64_t i, int64_t v) { p[i] = v; }
void w_nothing(void) { }

/* rsp mod 16 at entry: 8 when the caller aligned to 16 before CALL */
__attribute__((naked)) int64_t w_align(void) {
    __asm__("movq %rsp, %rax\n\tandq $15, %rax\n\tret");
}
/* writes over all 32 bytes of its shadow space, as a callee may; a caller that
 * did not reserve them loses whatever it kept there */
__attribute__((naked)) int64_t w_shadow(int64_t a, int64_t b, int64_t c, int64_t d) {
    __asm__("movq $-1, 8(%rsp)\n\tmovq $-1, 16(%rsp)\n\tmovq $-1, 24(%rsp)\n\tmovq $-1, 32(%rsp)\n\t"
            "leaq (%rcx,%rdx), %rax\n\taddq %r8, %rax\n\taddq %r9, %rax\n\tret");
}
/* destroys every volatile register (rax rcx rdx r8-r11, xmm0-5) and returns 7 */
__attribute__((naked)) int64_t w_clobber(void) {
    __asm__("movq $-1, %rcx\n\tmovq $-1, %rdx\n\tmovq $-1, %r8\n\tmovq $-1, %r9\n\t"
            "movq $-1, %r10\n\tmovq $-1, %r11\n\t"
            "pcmpeqd %xmm0, %xmm0\n\tpcmpeqd %xmm1, %xmm1\n\tpcmpeqd %xmm2, %xmm2\n\t"
            "pcmpeqd %xmm3, %xmm3\n\tpcmpeqd %xmm4, %xmm4\n\tpcmpeqd %xmm5, %xmm5\n\t"
            "movq $7, %rax\n\tret");
}
