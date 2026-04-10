#Adaptado de https://www.w3schools.com/python/python_args_kwargs.asp
def add(*numbers):
  total = 0
  for num in numbers:
    total += num
  return total

print(add(1, 2, 3))
print(add(10, 20, 30, 40))