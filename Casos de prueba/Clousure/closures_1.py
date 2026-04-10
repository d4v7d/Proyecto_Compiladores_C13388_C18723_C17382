def outer():
    message = "Hello World"
    def inner():
        return message
    return inner

function = outer()

print(function())