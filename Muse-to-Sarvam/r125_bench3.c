#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <x86intrin.h>
typedef struct { int64_t *buf; int64_t len; int64_t cap; } Desc;
static double now() { struct timespec ts; clock_gettime(CLOCK_MONOTONIC_RAW, &ts); return ts.tv_sec + ts.tv_nsec * 1e-9; }
int main(int argc, char **argv) {
    // TSC calibration (sleep is opaque, so rdtsc cannot be reordered past it)
    uint64_t c0 = __rdtsc(); struct timespec sl = {0, 100000000L}; nanosleep(&sl, NULL); uint64_t c1 = __rdtsc();
    double freq = (double)(c1 - c0) / 0.1; // cycles per second
    printf("TSC frequency: %.2f GHz\n", freq / 1e9);
    int seed = argc > 1 ? atoi(argv[1]) : 12345; // runtime seed: compiler cannot prove array contents
    int N = 1 << 20;
    volatile int64_t *buf = malloc(N * sizeof(int64_t));
    for (int i = 0; i < N; i++) buf[i] = (i * seed + 7) & 255;
    Desc d = { (int64_t*)buf, N, N };
    volatile Desc *vd = &d;
    int64_t sum = 0;
    double t0 = now();
    for (int i = 0; i < N; i++) sum += buf[i];
    double t1 = now();
    printf("direct array 1M (volatile, load-bound): %.3f ns/elem = %.2f cycles/elem\n", (t1-t0)/N*1e9, (t1-t0)/N*1e9*freq/1e9);
    sum = 0;
    t0 = now();
    for (int i = 0; i < N; i++) sum += vd->buf[i];
    t1 = now();
    printf("descriptor array 1M (volatile, per-access desc load): %.3f ns/elem = %.2f cycles/elem\n", (t1-t0)/N*1e9, (t1-t0)/N*1e9*freq/1e9);
    // dependent chain, HOT: contiguous nodes, volatile to force loads
    typedef struct Node { int64_t val; int64_t next; } Node;
    int M = 1 << 20;
    volatile Node *nodes = malloc(M * sizeof(Node));
    for (int i = 0; i < M; i++) { nodes[i].val = (i * seed) & 255; nodes[i].next = (i + 1) % M; }
    int64_t p = 0; sum = 0;
    t0 = now();
    for (int i = 0; i < M; i++) { p = nodes[p].next; sum += nodes[p].val; }
    t1 = now();
    printf("direct chain hot (volatile, contiguous): %.3f ns/step = %.2f cycles/step\n", (t1-t0)/M*1e9, (t1-t0)/M*1e9*freq/1e9);
    // descriptor chain, HOT: descs contiguous, each desc->buf points at its node's next cell
    volatile Desc *descs = malloc(M * sizeof(Desc));
    volatile int64_t *cells = malloc(M * sizeof(int64_t));
    volatile int64_t *vals = malloc(M * sizeof(int64_t));
    for (int i = 0; i < M; i++) { cells[i] = (i + 1) % M; vals[i] = (i * seed) & 255; descs[i].buf = (int64_t*)&cells[i]; descs[i].len = 0; descs[i].cap = 0; }
    p = 0; sum = 0;
    t0 = now();
    for (int i = 0; i < M; i++) { p = *descs[p].buf; sum += vals[p]; }
    t1 = now();
    printf("descriptor chain hot (volatile, contiguous descs): %.3f ns/step = %.2f cycles/step\n", (t1-t0)/M*1e9, (t1-t0)/M*1e9*freq/1e9);
    // dependent chain, COLD: descs scattered over 24MB, volatile (compiler cannot replace loads with arithmetic)
    volatile Desc *descc = malloc(M * sizeof(Desc));
    volatile int64_t *permc = malloc(M * sizeof(int64_t));
    for (int i = 0; i < M; i++) permc[i] = ((int64_t)i * seed * 2654435761LL) % M;
    for (int i = 0; i < M; i++) { descc[i].buf = (int64_t*)&cells[permc[i]]; descc[i].len = 0; descc[i].cap = 0; }
    p = 0; sum = 0;
    t0 = now();
    for (int i = 0; i < M; i++) { p = *descc[p].buf; sum += vals[p]; }
    t1 = now();
    printf("descriptor chain cold (volatile, 24MB descs): %.3f ns/step = %.2f cycles/step\n", (t1-t0)/M*1e9, (t1-t0)/M*1e9*freq/1e9);
    // direct cold chain, volatile perm (for comparison)
    p = 0; sum = 0;
    t0 = now();
    for (int i = 0; i < M; i++) { p = permc[p]; sum += vals[p]; }
    t1 = now();
    printf("direct chain cold (volatile perm, 8MB): %.3f ns/step = %.2f cycles/step\n", (t1-t0)/M*1e9, (t1-t0)/M*1e9*freq/1e9);
    printf("sink %lld\n", (long long)sum);
    return 0;
}
