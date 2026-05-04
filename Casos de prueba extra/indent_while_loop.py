# While loops con indentación compleja
i = 0
while i < 10:
    if i % 2 == 0:
        j = 0
        while j < i:
            x = i + j
            j = j + 1
    else:
        for k in range(i):
            y = k
    i = i + 1
