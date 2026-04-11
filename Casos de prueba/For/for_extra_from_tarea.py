class CuentaRegresiva:
    def __init__(self, inicio):
        self.valor = inicio

    def __iter__(self):
        return self

    def __next__(self):
        if self.valor < 1:
            raise StopIteration  
        
        actual = self.valor
        self.valor -= 1
        return actual

# Uso con el bucle for
cuenta = CuentaRegresiva(3)

print("Iniciando cuenta:")
for numero in cuenta:
    print(numero)