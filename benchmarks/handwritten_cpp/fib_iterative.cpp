// Hand-written iterative Fibonacci reference implementation.
// Mirrors benchmarks/fangless/fib_iterative.py exactly (same REPEAT count).
#include <iostream>
#include <cstdint>

int64_t fib(int64_t n) {
    int64_t a = 0;
    int64_t b = 1;
    for (int64_t i = 0; i < n; ++i) {
        int64_t temp = a + b;
        a = b;
        b = temp;
    }
    return a;
}

int main() {
    int64_t n;
    std::cin >> n;
    int64_t repeat = 100000;
    int64_t total = 0;
    for (int64_t r = 0; r < repeat; ++r) {
        total += fib(n);
    }
    std::cout << total << std::endl;
    return 0;
}
