#define _GNU_SOURCE
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <sys/resource.h>
#include <errno.h>
#include <string.h>

static void test(uint64_t cap, int attempt_map) {
    uint64_t bytes_wrapped = cap * UINT64_C(8);  /* defined unsigned arithmetic */
    int would_unsigned_overflow = cap > UINT64_MAX/8;
    int would_signed_overflow = cap > INT64_MAX/8;
    int64_t as_signed; memcpy(&as_signed, &bytes_wrapped, sizeof(as_signed));
    printf("cap=%" PRIu64 " wrapped_bytes=%" PRIu64 " signed_bytes=%" PRId64
           " unsigned_overflow=%d signed_overflow=%d sz_lt_zero=%d\n",
           cap, bytes_wrapped, as_signed, would_unsigned_overflow,
           would_signed_overflow, as_signed < 0);
    if(!attempt_map) return;
    errno = 0;
    void *ptr = mmap(NULL, (size_t)bytes_wrapped, PROT_READ | PROT_WRITE,
                     MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if(ptr==MAP_FAILED) printf("mmap=%s errno=%d\n", "FAILED", errno);
    else { printf("mmap=SUCCESS nonnull=%d (zero pages touched)\n", ptr != NULL);
           if(munmap(ptr,(size_t)bytes_wrapped) != 0) {perror("munmap");exit(1);} }
}
int main(void) {
    struct rlimit r; if(getrlimit(RLIMIT_AS,&r)!=0) {perror("getrlimit");return 2;}
    printf("RLIMIT_AS=%s\n",r.rlim_cur==RLIM_INFINITY?"unlimited":"finite");
    test(UINT64_C(3037000499),1);
    test(UINT64_C(2305843009213693953),1);  /* 2^61+1, 8B wrap */
    test(INT64_MAX,0);                       /* -8 signed wrap; don't mmap huge */
    return 0;
}
