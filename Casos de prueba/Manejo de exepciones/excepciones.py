try:
    resultado = 10 / 0
except ZeroDivisionError:
    print("Division por 0: inválida")
finally:
    print("Finalizado")