#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <x86intrin.h>
typedef struct { int64_t *buf; int64_t len; int64_t cap; } Desc;
static uint64_t tsc() { return __rdtsc(); }
int main() {
    // (a) hoisted: small array, descriptor pointer is a local (-O2 hoists d->buf)
    int N = 1 << 20;
    int64_t *buf = malloc(N * sizeof(int64_t));
    for (int i = 0; i < N; i++) buf[i] = i & 255;
    Desc d = { buf, N, N };
    int64_t sum = 0;
    // warmup
    for (int i = 0; i < N; i++) sum += buf[i];
    uint64_t t0 = tsc();
    for (int r = 0; r < 20; r++) for (int i = 0; i < N; i++) sum += buf[i];
    uint64_t t1 = tsc();
    printf("direct small: %.2f cycles/elem (sum %lld)\n", (double)(t1 - t0) / (20.0 * N), (long long)sum);
    sum = 0;
    for (int i = 0; i < N; i++) sum += d.buf[i];
    t0 = tsc();
    for (int r = 0; r < 20; r++) for (int i = 0; i < N; i++) sum += d.buf[i];
    t1 = tsc();
    printf("descriptor small (hoistable): %.2f cycles/elem (sum %lld)\n", (double)(t1 - t0) / (20.0 * N), (long long)sum);
    // (b) per-iteration descriptor load, hot: array of descriptors, contiguous (L1 hit), dependent via perm
    int M = 1 << 16;
    Desc *descs = malloc(M * sizeof(Desc));
    for (int i = 0; i < M; i++) { descs[i].buf = buf; descs[i].len = N; descs[i].cap = N; }
    int *perm = malloc(M * sizeof(int));
    for (int i = 0; i < M; i++) perm[i] = (i * 2654435761u) % N;
    sum = 0;
    for (int i = 0; i < M; i++) sum += buf[perm[i]];
    t0 = tsc();
    for (int r = 0; r < 20; r++) for (int i = 0; i < M; i++) sum += buf[perm[i]];
    t1 = tsc();
    printf("direct dependent (perm): %.2f cycles/elem\n", (double)(t1 - t0) / (20.0 * M));
    sum = 0;
    for (int i = 0; i < M; i++) sum += descs[i].buf[perm[i]];
    t0 = tsc();
    for (int r = 0; r < 20; r++) for (int i = 0; i < M; i++) sum += descs[i].buf[perm[i]];
    t1 = tsc();
    printf("descriptor dependent hot (descs in L1/L2, 1.5MB): %.2f cycles/elem\n", (double)(t1 - t0) / (20.0 * M));
    // (c) per-iteration descriptor load, cold: 1M descriptors scattered over 24MB (L1 miss, L2/L3)
    int MC = 1 << 20;
    Desc *descc = malloc(MC * sizeof(Desc));
    for (int i = 0; i < MC; i++) { descc[i].buf = buf; descc[i].len = N; descc[i].cap = N; }
    int *permc = malloc(MC * sizeof(int));
    for (int i = 0; i < MC; i++) permc[i] = (i * 2654435761u) % N;
    sum = 0;
    for (int i = 0; i < MC; i++) sum += descc[i].buf[permc[i]];
    t0 = tsc();
    for (int r = 0; r < 5; r++) for (int i = 0; i < MC; i++) sum += descc[i].buf[permc[i]];
    t1 = tsc();
    printf("descriptor dependent cold (24MB descs, L1 miss): %.2f cycles/elem\n", (double)(t1 - t0) / (5.0 * MC));
    // (d) memcpy 8MB (1M int64) - the deep-copy cost for value semantics
    int64_t *src = malloc(N * sizeof(int64_t));
    int64_t *dst = malloc(N * sizeof(int64_t));
    memset(src, 7, N * sizeof(int64_t));
    memcpy(dst, src, N * sizeof(int64_t));
    t0 = tsc();
    for (int r = 0; r < 20; r++) memcpy(dst, src, N * sizeof(int64_t));
    t1 = tsc();
    double cyc = (double)(t1 - t0) / 20.0;
    printf("memcpy 8MB: %.0f cycles/copy (%.2f cycles/elem)\n", cyc, cyc / N);
    printf("final sum %lld (anti-dead-code)\n", (long long)sum);
    return 0;
}
