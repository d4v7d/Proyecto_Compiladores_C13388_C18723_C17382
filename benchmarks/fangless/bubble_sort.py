# Bubble sort benchmark (Fangless Python).
# Reads N from stdin, builds a reverse-sorted array of size N (n being the worst case),
# sorts it, and prints a checksum (first + last element after sorting).
n = int(input())

arr = []
i = 0
while i < n:
    arr.append(n - i)
    i += 1

a = 0
while a < n:
    b = 0
    while b < n - 1:
        if arr[b] > arr[b + 1]:
            temp = arr[b]
            arr[b] = arr[b + 1]
            arr[b + 1] = temp
        b += 1
    a += 1

print(arr[0] + arr[n - 1])
