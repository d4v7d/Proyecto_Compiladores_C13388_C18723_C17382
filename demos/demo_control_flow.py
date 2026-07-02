# Demo 3: if/elif/else, while, for, break, and continue.
total = 0
for i in range(10):
    if i % 2 == 0:
        continue
    elif i > 7:
        break
    else:
        total += i

n = 3
while n > 0:
    total += n
    n -= 1

if total > 20:
    print("large")
elif total == 16:
    print("exact")
else:
    print("small")

print(total)
