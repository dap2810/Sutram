/* ROUND-35: refused by sutram-coff2smo - a relocation in read-only data (a table of pointers). */
#include <stdint.h>
static const char *const names[] = { "eka", "dvi", "tri" };
const char *w_name(int64_t i) { return names[i]; }
