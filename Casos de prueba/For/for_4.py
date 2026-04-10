# For iterando sobre un objeto Range inválido. Debería tirar error.
for i in range(-10, 10, 0):
    print(i)