class EjemploVariables:
    def __init__(self):
        self.valor = 5

    def cambiar_valor(self):
        print("Valor inicial:", self.valor)
        self.valor = 10
        print("Valor cambiado:", self.valor)

    def reasignar_local(self):
        valor = 20
        print("Variable local:", valor)

ej = EjemploVariables()

ej.cambiar_valor()
ej.reasignar_local()
print("Valor final del objeto:", ej.valor)