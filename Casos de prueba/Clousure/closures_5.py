def outer(val1):
    def inner(val2):
        def inner2(val3):
            return val1 + val2 + val3
        return inner2
    return inner

function = outer(1)
function2 = function(2)

print(function2(3))