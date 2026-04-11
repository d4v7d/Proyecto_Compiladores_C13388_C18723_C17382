def multiplicador(n):
    def mul(x):
        return x * n
    return mul

doble = multiplicador(2)
assert doble(5) == 10
