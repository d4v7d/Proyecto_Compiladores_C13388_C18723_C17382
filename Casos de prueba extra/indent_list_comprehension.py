# Comprensiones de lista con condicionales
numbers = [1, 2, 3, 4, 5]

# Comprensión simple
squares = [x ** 2 for x in numbers]

# Comprensión con condicional
evens = [x for x in numbers if x % 2 == 0]

# Comprensión anidada
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flat = [x for row in matrix for x in row]
