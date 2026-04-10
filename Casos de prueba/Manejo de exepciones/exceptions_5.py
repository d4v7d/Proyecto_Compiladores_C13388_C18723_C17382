try:
    print("Beggining Process")
    try:
        value = int("Hello World")
        print(value)
    except Exception as e:
        print("Catched: " , e)
        raise
except:
    print("Launched")
finally:
    print("Ending Process")