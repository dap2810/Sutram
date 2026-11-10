// Scenarios C and D: fill a buffer of n numbers, then sum all of it r times (arguments: r n)
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <numeric>
#include <vector>

int main(int argc, char **argv) {
    long r = argc > 1 ? std::atol(argv[1]) : 1;
    std::size_t n = argc > 2 ? static_cast<std::size_t>(std::atol(argv[2])) : 10000000;
    std::vector<std::int64_t> p(n);
    for (std::size_t i = 0; i < p.size(); i++) p[i] = static_cast<std::int64_t>(i & 1023);
    std::int64_t t = 0;
    for (long q = 0; q < r; q++) {
        p[q] += 1;
        t += std::accumulate(p.begin(), p.end(), std::int64_t{0});
    }
    std::cout << t << "\n";
}
