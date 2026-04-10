#Adaptado de https://www.w3schools.com/python/python_args_kwargs.asp
def say_hello_to(fname, lname):
  print("Hello, ", fname, lname)

person = {"fname": "Andrea", "lname": "Gomez"}
say_hello_to(**person) 