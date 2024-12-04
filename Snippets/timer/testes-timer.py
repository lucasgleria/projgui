import time

def contador_infinito():
    # Obtém o tempo inicial
    tempo_inicial = time.time()
    
    contador = 0

    while True:
        # Obtém o tempo atual
        tempo_atual = time.time()
        
        # Verifica se passaram 3 segundos
        if tempo_atual - tempo_inicial > 3:
            print("Tempo limite atingido. Encerrando a função.")
            break
        else:
            print(contador)
            contador += 1
            # Pequena pausa para evitar que o loop seja muito rápido
            time.sleep(0.1)

# Chama a função
contador_infinito()
