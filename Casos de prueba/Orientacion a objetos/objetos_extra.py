class A:
    def __init__(self, nombre): 
        self.nombre = nombre

    def __str__(self):          
        return f"Clase C llamada: {self.nombre}"

    def saludar(self):
        return "Hola desde A"

class B:
    def saludar(self):
        return "Hola desde B"

class C(A, B): # Herencia múltiple
    pass

# Pruebas
objeto = C("MiObjeto")

print(objeto)             
print(objeto.saludar())   