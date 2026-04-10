#Adaptado de https://www.w3schools.com/python/python_args_kwargs.asp
def my_function(username, **details):
  print("Username :", username)
  for key, value in details.items():
    print(key, ":", value)

my_function("user123", age = 23, city = "San Jose", hobby = "coding") 