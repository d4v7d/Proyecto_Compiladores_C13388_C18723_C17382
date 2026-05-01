# Funciones anidadas con múltiples niveles de indentación
def outer():
    a = 1
    def middle():
        b = 2
        def inner():
            c = 3
            return c
        return inner()
    return middle()
