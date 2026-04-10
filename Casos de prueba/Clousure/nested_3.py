def outer():
    def inner(val1, val2):
        return val1 + val2
    return inner(1, 2)

print(outer())