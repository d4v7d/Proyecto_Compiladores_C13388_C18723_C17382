def outer(message):
    def inner():
        return message
    return inner

function = outer("Hello World")

print(function())