import threading
import time

# class TimeoutException(Exception):
#     pass

def contador(timeout=3):
    def run_contador():
        contador = 0
        while not stop_event.is_set():
            print(contador)
            contador += 1
            time.sleep(1)  # Adicionado para simular uma contagem em intervalos de 1 segundo

    stop_event = threading.Event()
    thread = threading.Thread(target=run_contador)

    # Inicia o contador
    thread.start()
    
    # Aguarda o tempo limite
    thread.join(timeout)
    
    # Se o tempo limite foi atingido, define o evento de parada
    if thread.is_alive():
        stop_event.set()
        print("Tempo limite atingido. Encerrando o contador.")

# Exemplo de uso
contador(timeout=3)


Levando em consideração apenas o que eu compartilhei com você com as duas partes dos scripts, sem nenhuma modificação. Quando eu vou na janela de adição de produtos, clico em selecionar imagem, seleciono uma imagem e clico em Ok, recebo a seguinte mensagem no console:

Erro na leitura serial: main thread is not in main loop
Erro ao configurar a porta serial: object of type 'NoneType' has no len()