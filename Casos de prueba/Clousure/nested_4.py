def outer():
    def inner(val1, val2):
        return val1 + val2
    def inner2(val1, val2):
        return val1 - val2
    return inner(1, 2), inner2(2, 1)

print(outer())