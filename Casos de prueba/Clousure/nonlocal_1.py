x = "global"

def test_nonlocal():
    x = "externa"
    def interna():
        nonlocal x
        x = "interna"
    interna()
    return x

assert test_nonlocal() == "interna"
assert x == "global"
