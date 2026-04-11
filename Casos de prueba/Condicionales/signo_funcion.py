def signo(n):
    if n > 0:
        return "positivo"
    elif n < 0:
        return "negativo"
    else:
        return "cero"

assert signo(1) == "positivo"
assert signo(-1) == "negativo"
assert signo(0) == "cero"
