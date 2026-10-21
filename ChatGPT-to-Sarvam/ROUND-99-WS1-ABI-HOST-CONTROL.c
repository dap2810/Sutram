/* Round 99: ABI host witness, no Sutram compiler involved. */
typedef struct { long a; long b; } R99Pair;
typedef struct { long a; long b; long c; } R99Big;

double r99_f64_add(double a, double b) { return a + b; }
double r99_mixed(long a, double b, long c, double d) { return (double)(a + c) + b + d; }
long r99_pointer_sum(const unsigned char *p, long n) {
    long s = 0;
    for (long i = 0; i < n; ++i) s += p[i];
    return s;
}
void r99_void_store(long *p, long value) { *p = value; }
long r99_pair_sum(R99Pair p) { return p.a + p.b; }
long r99_big_sum(R99Big p) { return p.a + p.b + p.c; }
__attribute__((ms_abi)) long r99_ms_abi_add(long a, long b) { return a + b; }
