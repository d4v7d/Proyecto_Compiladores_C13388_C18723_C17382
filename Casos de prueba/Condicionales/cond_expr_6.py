# Expresión con múltiples AND, OR y NOT

a = 10
b = 3
c = ((a * b < 60 and a * b > 40) or (a != b and not a == 10)) and not b == 3
print(c)