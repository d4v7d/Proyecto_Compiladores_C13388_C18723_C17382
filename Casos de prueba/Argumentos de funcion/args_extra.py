def saludo(nombre, msg="Hola"):
    return f"{msg} {nombre}"

def suma(*args):
    return sum(args)

assert saludo("Ana") == "Hola Ana"
assert saludo("Ana", "Hey") == "Hey Ana"
assert suma(1, 2, 3) == 6
