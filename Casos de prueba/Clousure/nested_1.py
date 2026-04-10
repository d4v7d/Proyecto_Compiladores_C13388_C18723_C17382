def outer():
    def inner():
        print("Hello World")
    inner()

outer()
