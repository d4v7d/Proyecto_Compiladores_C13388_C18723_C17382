a, b, c = 1, 2, 3
assert (a, b, c) == (1, 2, 3)

primero, *resto = [1, 2, 3, 4]
assert primero == 1
assert resto == [2, 3, 4]
