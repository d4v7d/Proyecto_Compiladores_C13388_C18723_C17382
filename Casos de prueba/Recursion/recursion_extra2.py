class Matematica:
    def factorial(self, n):
        if n == 0:
            return 1
        return n * self.factorial(n - 1)

mate = Matematica()

print("Factorial de 5:", mate.factorial(5))
print("Factorial de 0:", mate.factorial(0))