def dividir(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None
    finally:
        pass

assert dividir(10, 2) == 5.0
assert dividir(10, 0) is None
