// Hand-written recursive Fibonacci reference implementation.
// Mirrors benchmarks/fangless/fib_recursive.py exactly.
#include <iostream>
#include <cstdint>

int64_t fib(int64_t n) {
    if (n < 2) {
        return n;
    }
    return fib(n - 1) + fib(n - 2);
}

int main() {
    int64_t n;
    std::cin >> n;
    std::cout << fib(n) << std::endl;
    return 0;
}
