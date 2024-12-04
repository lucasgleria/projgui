def contador_infinito(tempo_limite):
    contador = 0
    ciclos = 0
    ciclos_por_segundo = 12  # Assumindo que cada ciclo leva aproximadamente 0.1 segundos
    limite_de_ciclos = tempo_limite * ciclos_por_segundo

    while True:
        if ciclos > limite_de_ciclos:
            print("Tempo limite atingido. Encerrando a função.")
            break
        else:
            print(contador)
            contador += 1
            ciclos += 1
            # Simulando um pequeno atraso para evitar que o loop seja muito rápido
            for _ in range(1000000):
                pass

# Chama a função com um tempo limite de 3 segundos
contador_infinito(3)
