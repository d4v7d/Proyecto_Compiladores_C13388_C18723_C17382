class Contador:
    def __init__(self, limite):
        self.limite = limite
        self.actual = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.actual < self.limite:
            valor = self.actual
            self.actual += 1
            return valor
        else:
            raise StopIteration


if __name__ == "__main__":
    c = Contador(5)

    print("Usando for:")
    for num in c:
        print(num)

    print("\nUso manual:")
    c2 = Contador(3)
    it = iter(c2)
    print(next(it))
    print(next(it))
    print(next(it))

    print("\nFor normal con lista:")
    lista = [10, 11, 12]
    for num in lista:
        print(num)