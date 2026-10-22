/* ROUND-35: refused by sutram-coff2smo - it calls out (an undefined symbol). */
#include <stdint.h>
int64_t elsewhere(int64_t);
int64_t w_callout(int64_t a) { return elsewhere(a) + 1; }
