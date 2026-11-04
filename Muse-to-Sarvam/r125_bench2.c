#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
typedef struct { int64_t *buf; int64_t len; int64_t cap; } Desc;
static double now() { struct timespec ts; clock_gettime(CLOCK_MONOTONIC_RAW, &ts); return ts.tv_sec + ts.tv_nsec * 1e-9; }
volatile int64_t sink;
int main() {
    int N = 1 << 20;
    int64_t *buf = malloc(N * sizeof(int64_t));
    for (int i = 0; i < N; i++) buf[i] = i & 255;
    Desc d = { buf, N, N };
    // (a) array loop, throughput: direct vs descriptor (hoistable). Single large loop, no repetition.
    int64_t sum = 0;
    double t0 = now();
    for (int i = 0; i < N; i++) sum += buf[i];
    double t1 = now();
    printf("direct array 1M: %.3f ns/elem\n", (t1 - t0) / N * 1e9);
    sum = 0;
    t0 = now();
    for (int i = 0; i < N; i++) sum += d.buf[i];
    t1 = now();
    printf("descriptor array 1M (hoistable): %.3f ns/elem\n", (t1 - t0) / N * 1e9);
    sink = sum;
    // (b) dependent chain (latency): linked list, direct vs descriptor, HOT (nodes contiguous, L1/L2 hit)
    typedef struct Node { int64_t val; int64_t next; } Node;
    int M = 1 << 20;
    Node *nodes = malloc(M * sizeof(Node));
    for (int i = 0; i < M; i++) { nodes[i].val = i & 255; nodes[i].next = (i + 1) % M; }
    // direct: p = nodes[p].next; sum += nodes[p].val  (dependent chain)
    int64_t p = 0; sum = 0;
    t0 = now();
    for (int i = 0; i < M; i++) { p = nodes[p].next; sum += nodes[p].val; }
    t1 = now();
    printf("direct chain 1M steps (hot, contiguous): %.3f ns/step\n", (t1 - t0) / M * 1e9);
    sink = sum;
    // descriptor chain: each node has a descriptor; step loads desc->buf (the next index) then buf value.
    // Model: descs[i].buf points at a per-node cell holding the next index; value array separate.
    Desc *descs = malloc(M * sizeof(Desc));
    int64_t *cells = malloc(M * sizeof(int64_t));
    for (int i = 0; i < M; i++) { cells[i] = (i + 1) % M; descs[i].buf = &cells[i]; descs[i].len = 0; descs[i].cap = 0; }
    int64_t *vals = malloc(M * sizeof(int64_t));
    for (int i = 0; i < M; i++) vals[i] = i & 255;
    p = 0; sum = 0;
    t0 = now();
    for (int i = 0; i < M; i++) { p = *descs[p].buf; sum += vals[p]; }
    t1 = now();
    printf("descriptor chain 1M steps (hot, contiguous descs): %.3f ns/step\n", (t1 - t0) / M * 1e9);
    sink = sum;
    // (c) dependent chain, COLD: nodes scattered by a permutation stride so each step misses L1/L2
    int64_t *perm = malloc(M * sizeof(int64_t));
    for (int i = 0; i < M; i++) perm[i] = (i * 2654435761LL) % M;
    // direct cold: p = perm[p] (perm is 8MB, exceeds L2, mostly L3/DRAM)
    p = 0; sum = 0;
    t0 = now();
    for (int i = 0; i < M; i++) { p = perm[p]; sum += vals[p]; }
    t1 = now();
    printf("direct chain 1M steps (cold perm, 8MB): %.3f ns/step\n", (t1 - t0) / M * 1e9);
    sink = sum;
    // descriptor cold: descs scattered (24MB), each step loads descs[p].buf (cold) then vals[p]
    Desc *descc = malloc(M * sizeof(Desc));
    for (int i = 0; i < M; i++) { descc[i].buf = &cells[perm[i]]; descc[i].len = 0; descc[i].cap = 0; }
    // chain: p = *descc[p].buf  (descc[p] is cold, cells[perm[p]] is the next index)
    p = 0; sum = 0;
    t0 = now();
    for (int i = 0; i < M; i++) { p = *descc[p].buf; sum += vals[p]; }
    t1 = now();
    printf("descriptor chain 1M steps (cold descs, 24MB): %.3f ns/step\n", (t1 - t0) / M * 1e9);
    sink = sum;
    // (d) memcpy 8MB (deep-copy cost for value semantics, 1M int64)
    int64_t *src = malloc(N * sizeof(int64_t));
    int64_t *dst = malloc(N * sizeof(int64_t));
    memset(src, 7, N * sizeof(int64_t));
    t0 = now();
    memcpy(dst, src, N * sizeof(int64_t));
    t1 = now();
    printf("memcpy 8MB single: %.3f ms (%.1f GB/s)\n", (t1 - t0) * 1e3, (N * 8.0) / (t1 - t0) / 1e9);
    sink = dst[0];
    return 0;
}
