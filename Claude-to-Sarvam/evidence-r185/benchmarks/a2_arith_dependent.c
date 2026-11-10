/* Scenario A2: 10,000,000 passes of s = (s + i * 2) ^ (s >> 3) - each pass needs the one before */
#include <stdint.h>
#include <stdio.h>

int main(void) {
    int64_t s = 0;
    for (int64_t i = 0; i < 10000000; i++) {
        s = (s + i * 2) ^ (s >> 3);
    }
    printf("%lld\n", (long long)s);
    return 0;
}
