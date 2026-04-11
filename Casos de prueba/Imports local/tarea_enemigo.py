class Enemigo:
    def atacar(self, objetivo):
        # El import sucede solo cuando se ejecuta la función, no al cargar el archivo
        from core.jugador import Jugador 
        
        if isinstance(objetivo, Jugador):
            print("Atacando al jugador...")
            objetivo.recibir_danio(10)