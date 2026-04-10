def procesar_dato(dato: int | str):
    if isinstance(dato, int):
        print(f"El número al cuadrado es: {dato ** 2}")
    elif isinstance(dato, str):
        print(f"El texto en mayúsculas es: {dato.upper()}")

# Probando la función con diferentes tipos
procesar_dato(10)      # Salida: El número al cuadrado es: 100
procesar_dato("hola")  # Salida: El texto en mayúsculas es: HOLA