def gen(n):
    for i in range(n):
        yield i

assert list(gen(3)) == [0, 1, 2]
