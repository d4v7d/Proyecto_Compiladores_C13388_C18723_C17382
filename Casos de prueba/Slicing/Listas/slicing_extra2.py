class Salon:
    def __init__(self, alumnos):
        self.alumnos = alumnos 

    def obtener_resumen(self):
        # 1. Slicing en Listas: [inicio:fin]
        primeros_dos = self.alumnos[:2]
        
        # 2. Slicing con Paso: [::paso] 
        uno_si_uno_no = self.alumnos[::2]
        
        # 3. Slicing para Invertir: [::-1]
        lista_invertida = self.alumnos[::-1]
        
        return primeros_dos, uno_si_uno_no, lista_invertida



# Datos de prueba
nombres = ["Ana", "Beto", "Carla", "David", "Elena"]
mi_clase = Salon(nombres)

p2, saltos, inv = mi_clase.obtener_resumen()

print(f"Lista completa: {mi_clase.alumnos}")
print(f"1. Primeros dos: {p2}")          
print(f"2. Saltando de 2 en 2: {saltos}")
print(f"3. Orden inverso: {inv}")       

# Manipulación de Strings
palabra = "Python"
print(f"4. String invertido: {palabra[::-1]}") 