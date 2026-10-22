/* Sutram R100: compile-only Microsoft x64 ABI witness, not Windows execution. */
typedef struct { long long a; long long b; } R100Pair;
__attribute__((ms_abi, noinline)) long long r100_int4(long long a,long long b,long long c,long long d){ return a + 2*b + 3*c + 4*d; }
__attribute__((ms_abi, noinline)) long long r100_int5(long long a,long long b,long long c,long long d,long long e){ return a + b + c + d + e; }
__attribute__((ms_abi, noinline)) double r100_fp4(double a,double b,double c,double d){ return a+b+c+d; }
__attribute__((ms_abi, noinline)) long long r100_mixed(long long a,double b,long long c,double d){ return a+c+(long long)(b+d); }
__attribute__((ms_abi, noinline)) void r100_store(long long *p,long long v){ *p = v; }
__attribute__((ms_abi, noinline)) R100Pair r100_pair_return(long long a,long long b){ R100Pair p={a,b};return p; }
