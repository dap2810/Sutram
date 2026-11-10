/* Scenarios C and D: fill a buffer of n numbers, then sum all of it r times (arguments: r n) */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    long r = argc > 1 ? atol(argv[1]) : 1;
    size_t n = argc > 2 ? (size_t)atol(argv[2]) : 10000000;
    int64_t *p = malloc(n * sizeof *p);
    if (!p) return 1;
    for (size_t i = 0; i < n; i++) p[i] = (int64_t)(i & 1023);
    int64_t t = 0;
    for (long q = 0; q < r; q++) {
        p[q] += 1;
        int64_t s = 0;
        for (size_t j = 0; j < n; j++) s += p[j];
        t += s;
    }
    printf("%lld\n", (long long)t);
    free(p);
    return 0;
}
