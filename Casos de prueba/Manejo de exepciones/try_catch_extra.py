class Calculadora:
    def __init__(self, nombre):
        self.nombre = nombre
 
    def dividir(self, a, b):
        try:
            resultado = a / b
        except ZeroDivisionError:
            return "Error: no se puede dividir entre cero."
        except TypeError:
            return "Error: los operandos deben ser numéricos."
        else:
            return f"Resultado: {resultado}"
        finally:
            print(f"[{self.nombre}] Operación finalizada.")
 
    def convertir(self, valor):
        try:
            return int(valor)
        except ValueError:
            raise ValueError(f"'{valor}' no es un entero.")
 
 
calc = Calculadora("Calc-1")
print(calc.dividir(10, 2))
print(calc.dividir(10, 0))
print(calc.dividir(10, "x"))
 
try:
    print(calc.convertir("abc"))
except ValueError as e:
    print(e)