import module_example

def main():
    module_example.say_hello()
    print("Using add function from module_example: 5 + 3 =", module_example.add(5, 3))
    print("Using subtract function from module_example: 5 - 3 =", module_example.subtract(5, 3))

main()