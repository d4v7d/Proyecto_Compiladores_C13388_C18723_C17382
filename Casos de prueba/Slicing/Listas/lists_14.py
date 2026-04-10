values = [
            [0, 1, 2], 
            [3, 4, 5]
         ]

results = [0, 0]

for i in range(2):
    for n in range(3):
        results[i] = values[i][n] + results[i]
    
print(results)