class Conteo:
    def __init__(self, limite):
        self.limite = limite
 
    def generar(self):
        for i in range(1, self.limite + 1):
            yield i
 
conteo = Conteo(5)
print("Conteo con yield:")
for numero in conteo.generar():
    print(numero)
 
def pares_infinitos():
    n = 0
    while True:
        yield n
        n += 2
 
gen = pares_infinitos()
print("\nPrimeros 4 pares:")
for _ in range(4):
    print(next(gen))