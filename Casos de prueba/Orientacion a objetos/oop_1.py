class Animal:
    def __init__(self, nombre):
        self.nombre = nombre
    def __str__(self):
        return f"Animal: {self.nombre}"

class Volador:
    def volar(self):
        return "volando"

class Pajaro(Animal, Volador):
    pass

p = Pajaro("Pío")
assert str(p) == "Animal: Pío"
assert p.volar() == "volando"
assert Pajaro.__mro__ == (Pajaro, Animal, Volador, object)
