/* Scenario B: build a collection of 1,000,000 numbers, then sum it. C has no growing collection:
   this is the usual hand-written one - malloc, and realloc to twice the size when it is full. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    size_t len = 0, cap = 4;
    int64_t *a = malloc(cap * sizeof *a);
    if (!a) return 1;
    for (int64_t i = 0; i < 1000000; i++) {
        if (len == cap) {
            cap *= 2;
            int64_t *b = realloc(a, cap * sizeof *a);
            if (!b) return 1;
            a = b;
        }
        a[len++] = i;
    }
    int64_t s = 0;
    for (size_t j = 0; j < len; j++) s += a[j];
    printf("%lld\n", (long long)s);
    free(a);
    return 0;
}
