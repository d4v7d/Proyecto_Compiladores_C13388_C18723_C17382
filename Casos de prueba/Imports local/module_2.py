from module_example import add, subtract, say_hello

def main():
    say_hello()
    print("Using add function from module_example: 5 + 3 =", add(5, 3))
    print("Using subtract function from module_example: 5 - 3 =", subtract(5, 3))

main()