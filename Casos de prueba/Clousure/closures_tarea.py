# Closures y funciones anidadas

def crear_sumador(n):
    def sumar(x):
        return x + n
    return sumar

sumar_5 = crear_sumador(5)
sumar_10 = crear_sumador(10)

print("5 + 3 =", sumar_5(3))
print("10 + 3 =", sumar_10(3))
