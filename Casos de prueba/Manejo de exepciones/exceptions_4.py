try:
    print("Beggining Process")
    try:
        value = int("Hello World")
        print(value)
    except Exception as e:
        print(e)
except:
    print("In Process")
finally:
    print("Ending Process")