def outer():
    def inner():
        return "Hello World"
    return inner()

print(outer())