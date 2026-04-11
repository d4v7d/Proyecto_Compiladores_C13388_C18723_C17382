class Archivo:
    def __init__(self, nombre):
        self.nombre = nombre

    def __enter__(self):
        print(f"Abriendo {self.nombre}")
        return self

    def escribir(self, texto):
        print(f"  Escribiendo: {texto}")

    def __exit__(self, tipo_exc, valor_exc, tb):
        print(f"Cerrando {self.nombre}")
        return False


with Archivo("notas.txt") as f:
    f.escribir("Hola mundo")
    f.escribir("Segunda línea")