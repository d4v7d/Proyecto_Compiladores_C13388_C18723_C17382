// Hand-written bubble sort reference implementation.
// Mirrors benchmarks/fangless/bubble_sort.py exactly.
#include <iostream>
#include <cstdint>
#include <vector>

int main() {
    int64_t n;
    std::cin >> n;

    std::vector<int64_t> arr(n);
    for (int64_t i = 0; i < n; ++i) {
        arr[i] = n - i;
    }

    for (int64_t a = 0; a < n; ++a) {
        for (int64_t b = 0; b < n - 1; ++b) {
            if (arr[b] > arr[b + 1]) {
                int64_t temp = arr[b];
                arr[b] = arr[b + 1];
                arr[b + 1] = temp;
            }
        }
    }

    std::cout << arr[0] + arr[n - 1] << std::endl;
    return 0;
}
