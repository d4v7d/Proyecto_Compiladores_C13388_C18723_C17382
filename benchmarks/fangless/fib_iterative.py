# Iterative Fibonacci benchmark (Fangless Python).
# Reads N from stdin.
def fib(n):
    a = 0
    b = 1
    i = 0
    while i < n:
        temp = a + b
        a = b
        b = temp
        i += 1
    return a

n = int(input())
repeat = 100000
total = 0
r = 0
while r < repeat:
    total += fib(n)
    r += 1
print(total)
