total = 0
for i in range(5):
    total += i
assert total == 10

resultado = list(enumerate(["a", "b"]))
assert resultado == [(0, "a"), (1, "b")]
