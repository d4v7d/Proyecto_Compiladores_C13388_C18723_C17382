# Argumentos de función: *args, **kwargs, argumentos por defecto

def mostrar_datos(nombre, saludo="Hola", *args, **kwargs):
    print(f"{saludo}, {nombre}")
    print("args =", args)
    print("kwargs =", kwargs)

mostrar_datos("Sebastian")
print("---")
mostrar_datos("David", "Buenas", 1, 2, 3, edad=25, ciudad="Madrid")
