if __name__ == "__main__":
    lista = [10, 20, 30, 40, 50]
    tupla = (1, 2, 3, 4, 5)
    texto = "python"

    # Slicing
    print("Slicing:")
    print(lista[1:4])      # [20, 30, 40]
    print(tupla[:3])       # (1, 2, 3)
    print(texto[2:])       # "thon"

    # Manipulación de listas
    print("\nManipulación de listas:")
    lista.append(60)
    lista.remove(20)
    print(lista)

    # Acceso a elementos
    print("\nAcceso a elementos:")
    print(lista[0])
    print(tupla[-1])
    print(texto[0])
