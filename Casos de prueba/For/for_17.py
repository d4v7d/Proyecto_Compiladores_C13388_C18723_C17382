# Iteración sobre un objeto que cuenta con el método dunder __iter__

class MyList:
    def __init__(self, items = [1, 2, 3]):
        self.items = items

    def __iter__(self):
        return iter(self.items)

for x in MyList([1, 2, 10, 20, 0, -10]):
    print(x)