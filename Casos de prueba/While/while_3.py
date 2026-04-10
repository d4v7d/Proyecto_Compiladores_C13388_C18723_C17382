# While con continue

a = 0
b = 10

while a < b:
    a += 1
    if a % 2 == 0:
        continue
    print(a)