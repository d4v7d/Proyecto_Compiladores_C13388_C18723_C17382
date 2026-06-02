# test_class_basic.fpy
# Tests: class definition, __init__, self attribute assignment, method, instantiation
# Expected: parses successfully, no errors

class Dog:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def bark(self):
        return "Woof!"

    def describe(self):
        return self.name

d = Dog("Rex", 3)
sound = d.bark()
info = d.describe()
