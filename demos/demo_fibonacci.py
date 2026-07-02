# Demo 5: recursive function (benchmark-style, fixed input for live demo).
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

print(fib(10))
