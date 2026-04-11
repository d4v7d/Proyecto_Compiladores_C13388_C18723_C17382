class Bateria:
    def __init__(self, nivel_inicial):
        self.nivel = nivel_inicial

    def __str__(self):
        return f"Batería al {self.nivel}%"

    def gastar(self):
        self.nivel -= 25

    def esta_viva(self):
        return self.nivel > 0

# --- Uso con el bucle while ---
mi_celular = Bateria(100)

while mi_celular.esta_viva(): # Se ejecuta mientras la condición sea True
    print(f"Estado: {mi_celular}")
    mi_celular.gastar()

print("Dispositivo apagado. Por favor, cargue su batería.")