def outer():
    def inner():
        def inner2():
            return "Hello World"
        return inner2()
    return inner()

print(outer())