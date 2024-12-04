import threading

def contador_infinito(tempo_limite):
    contador = 0
    stop_flag = [False]

    def interrupcao_temporizada(tempo):
        # Função interna que define o tempo de execução e altera o stop_flag após o tempo limite
        for _ in range(tempo * 10):
            if stop_flag[0]:
                return
            for _ in range(1000000):
                pass
        stop_flag[0] = True

    # Cria uma thread que executará a função interrupcao_temporizada
    thread = threading.Thread(target=interrupcao_temporizada, args=(tempo_limite,))
    thread.start()

    while not stop_flag[0]:
        print(contador)
        contador += 1
        for _ in range(1000000):
            pass

    thread.join()
    print("Tempo limite atingido. Encerrando a função.")

# Chama a função com um tempo limite de 3 segundos
contador_infinito(3)
