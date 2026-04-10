import module_example as utils

def main():
    utils.say_hello()
    print("Using add function from module_example: 5 + 3 =", utils.add(5, 3))
    print("Using subtract function from module_example: 5 - 3 =", utils.subtract(5, 3))

main()