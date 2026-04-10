try:
    print("Beggining Process")
    value = int("Hello World")
    print(value)
except Exception as e:
    print(e)
else:
    print("Success")
finally:
    print("Ending Process")