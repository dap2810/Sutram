#define _GNU_SOURCE
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

/* Developer-only probe: original compiler is not replaced by this harness.
 * The three routines below are the exact NASM payload instruction bodies,
 * assembled through the narrow GNU-as bridge. mmap/mincore are real OS calls.
 */
extern uint64_t growth_guard_bridge(uint64_t capacity, uint64_t length);
extern uint64_t allocation_guard_bridge(uint64_t address);
extern void reclaim_bridge(uint64_t *old_user, uint64_t *new_user, uint64_t *saved);

static uint64_t pattern(uint64_t i, int floating_bits) {
    static const uint64_t bits[] = {
        UINT64_C(0x8000000000000000), UINT64_C(0x7ff8000000001234),
        UINT64_C(0x3ff8000000000000), UINT64_C(0xfff0000000000000),
        UINT64_C(0x0000000000000001), UINT64_C(0x4004000000000000)
    };
    return floating_bits ? bits[i % 6] : (i * UINT64_C(0x9e3779b97f4a7c15));
}
static uint64_t *allocate(uint64_t capacity) {
    size_t n = (size_t)(capacity * 8 + 16);
    void *p = mmap(NULL, n, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (p == MAP_FAILED) { perror("probe mmap"); exit(70); }
    allocation_guard_bridge((uint64_t)(uintptr_t)p);
    uint64_t *h = p;
    h[0] = 0; h[1] = capacity;
    return h + 2;
}
static int unmapped(uint64_t *old_user, uint64_t cap, long pagesize, size_t *checked) {
    uintptr_t base = (uintptr_t)(old_user - 2);
    size_t n = (size_t)(cap * 8 + 16);
    for (size_t off = 0; off < n; off += (size_t)pagesize) {
        unsigned char vec = 0;
        errno = 0;
        if (mincore((void *)(base + off), (size_t)pagesize, &vec) != -1 || errno != ENOMEM)
            return 0;
        ++*checked;
    }
    return 1;
}
int main(int argc, char **argv) {
    if (argc < 2) return 64;
    if (!strcmp(argv[1], "guard") && argc == 4) {
        uint64_t c = strtoull(argv[2], NULL, 0), n = strtoull(argv[3], NULL, 0);
        uint64_t r = growth_guard_bridge(c, n);
        if (r != UINT64_C(0x123456789abcdef0)) return 65;
        puts("guard-returned"); return 0;
    }
    if (!strcmp(argv[1], "allocation") && argc == 3) {
        uint64_t value = strtoull(argv[2], NULL, 0);
        if (allocation_guard_bridge(value) != value) return 65;
        puts("allocation-returned"); return 0;
    }
    if (!strcmp(argv[1], "release-fail")) {
        uint64_t *p = allocate(8), out[8] = {0};
        /* Inject an unaligned OLD allocation base, without an invalid read. */
        p[0] = 1; /* capacity read by reclaim: [old_user-8] */
        reclaim_bridge(p + 1, p, out);
        return 66; /* failure must terminate, not silently return */
    }
    if (strcmp(argv[1], "cycle") || argc != 5) return 64;
    uint64_t initial = strtoull(argv[2], NULL, 0);
    unsigned steps = (unsigned)strtoul(argv[3], NULL, 0);
    int float_bits = atoi(argv[4]);
    if (initial > 4097 || steps > 16) return 64;
    long ps = sysconf(_SC_PAGESIZE);
    if (ps <= 0) return 70;
    uint64_t *live = allocate(initial), cap = initial, length = cap;
    live[-2] = length;
    for (uint64_t i = 0; i < length; ++i) live[i] = pattern(i, float_bits);
    size_t checked = 0, released = 0;
    for (unsigned step = 0; step < steps; ++step) {
        if (growth_guard_bridge(cap, length) != UINT64_C(0x123456789abcdef0)) return 65;
        uint64_t newcap = cap ? cap * 2 : 4;
        uint64_t *newptr = allocate(newcap);
        memcpy(newptr, live, (size_t)length * 8);
        newptr[-2] = length;
        uint64_t *old = live;
        live = newptr; /* match compiler ordering: publish BEFORE reclaim */
        uint64_t out[8] = {0};
        reclaim_bridge(old, newptr, out);
        if (out[0] != (uint64_t)(uintptr_t)newptr || out[1] != UINT64_C(0x1122334455667788)
            || out[2] != UINT64_C(0x1020304050607080) || out[3] != UINT64_C(0x8877665544332211)
            || out[4] != UINT64_C(0x0123456789abcdef) || out[5] != (uint64_t)(uintptr_t)old
            || out[6] != length || out[7] != (uint64_t)(uintptr_t)newptr) return 67;
        if (!unmapped(old, cap, ps, &checked)) return 68;
        ++released;
        if (live[-2] != length || live[-1] != newcap) return 69;
        for (uint64_t i = 0; i < length; ++i) if (live[i] != pattern(i, float_bits)) return 69;
        /* Fill new capacity for the next growth. This is test setup, not an emitter. */
        for (uint64_t i = length; i < newcap; ++i) live[i] = pattern(i, float_bits);
        cap = newcap; length = cap; live[-2] = length;
    }
    size_t final_bytes = (size_t)(cap * 8 + 16);
    if (munmap(live - 2, final_bytes)) return 70; /* test-owned final cleanup only */
    printf("{\"growths\":%u,\"released\":%zu,\"old_pages_confirmed_unmapped\":%zu,"
           "\"final_live_bytes_before_test_cleanup\":%zu,\"raw_float_bits\":%d,\"uid\":%ld}\n",
           steps, released, checked, final_bytes, float_bits, (long)getuid());
    return 0;
}
