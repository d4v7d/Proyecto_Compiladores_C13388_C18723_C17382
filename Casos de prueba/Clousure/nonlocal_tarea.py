# Resolución de ámbitos LEGB con global y nonlocal

x = "global"

def externa():
    x = "enclosing"

    def interna():
        nonlocal x
        x = "modificado por nonlocal"
        print("Dentro de interna:", x)

    interna()
    print("Dentro de externa:", x)

def cambiar_global():
    global x
    x = "modificado por global"

print("Antes:", x)
externa()
cambiar_global()
print("Después:", x)
