def outer(val1):
    def inner(val2):
        return val1 + val2
    return inner

function = outer(1)

print(function(2))