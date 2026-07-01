# Exercises every control-flow construct owned by Part 3.
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

if total > 5:
    print("big")
elif total == 5:
    print("exactly five")
else:
    print("small")

print(total)
