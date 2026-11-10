// Scenario B: build a collection of 1,000,000 numbers, then sum it - std::vector
#include <cstdint>
#include <iostream>
#include <numeric>
#include <vector>

int main() {
    std::vector<std::int64_t> v;
    for (std::int64_t i = 0; i < 1000000; i++) v.push_back(i);
    std::cout << std::accumulate(v.begin(), v.end(), std::int64_t{0}) << "\n";
}
