class Termostato:
    def __init__(self, temperatura):
        self.temperatura = temperatura

    def analizar_clima(self):
        # Estructura condicional anidada en un método
        if self.temperatura > 30:
            return "Hace mucho calor. Encendiendo aire acondicionado."
        elif 18 <= self.temperatura <= 30:
            return "Temperatura agradable. No hacer nada."
        elif 0 < self.temperatura < 18:
            return "Hace frío. Encendiendo calefacción."
        else:
            return "¡Alerta de congelación! Revisando tuberías."

# Pruebas
entorno_1 = Termostato(35)
entorno_2 = Termostato(22)
entorno_3 = Termostato(-5)

print(f"35°C: {entorno_1.analizar_clima()}")
print(f"22°C: {entorno_2.analizar_clima()}")
print(f"-5°C: {entorno_3.analizar_clima()}")