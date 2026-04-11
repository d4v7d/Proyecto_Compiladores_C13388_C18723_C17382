assert [x**2 for x in range(4)] == [0, 1, 4, 9]
assert {x: x*2 for x in range(3)} == {0: 0, 1: 2, 2: 4}
assert {x % 2 for x in range(4)} == {0, 1}
