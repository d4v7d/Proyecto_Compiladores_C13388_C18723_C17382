def crear_multiplicador(n):
    def multiplicar(x):
        return x * n
    return multiplicar

por_tres = crear_multiplicador(3)

print(por_tres(10))