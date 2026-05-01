# Closures con múltiples niveles de indentación
def outer(x):
    def middle(y):
        def inner(z):
            return x + y + z
        
        if y > 0:
            return inner
        else:
            return None
    
    for i in range(x):
        middle(i)
    
    return middle
