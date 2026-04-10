def outer():
    val = 1
    def inner():
        nonlocal val
        val = val * 2
        return val
    return inner

function = outer()

print(function())
print(function())
print(function())