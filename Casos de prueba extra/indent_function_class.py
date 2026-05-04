# Clases con métodos indentados
class MyClass:
    def __init__(self):
        self.value = 10
    
    def method1(self):
        if self.value > 0:
            return self.value
        else:
            return 0
    
    def method2(self):
        for i in range(self.value):
            x = i
        return x
