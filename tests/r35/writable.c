/* ROUND-35: refused by sutram-coff2smo - writable data. */
#include <stdint.h>
static int64_t counter = 5;
int64_t w_count(void) { return ++counter; }
