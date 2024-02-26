import serial
import time

# Função para ler dados da porta serial
def read_serial(ser):
    buffer = ''  # Buffer para armazenar dados parciais
    start_time = time.time()  # Tempo inicial

    while True:
        try:
            data = ser.readline().decode('utf-8')
            if '\n' in data:
                buffer += data
                values = buffer.split('\n')
                if len(values) >= 2 and values[0] and values[1]:
                    values = [str(value) for value in values if value]  # Filtra valores vazios
                    print(f'Dado 1: {values[0]}, Dado 2: {values[1]}')
                    buffer = ''  # Limpa o buffer após processar os dados

            # Verifica se passou 5 segundos
            elapsed_time = time.time() - start_time
            if elapsed_time >= 5:
                break

        except Exception as e:
            print(f"Erro na leitura serial: {e}")

# Função principal
def main():
    # Defina a porta serial do Arduino
    arduino_port = 'COM7'  # Altere para a porta correta

    # Tenta abrir a porta serial
    ser = None
    try:
        ser = serial.Serial(arduino_port, 9600, timeout=1)
        print(f"Porta serial {arduino_port} aberta com sucesso!")

        for _ in range(5):  # Loop principal com limite de 5 execuções
            # Envie o caractere de nova linha para iniciar a comunicação
            time.sleep(3)
            enter = f'\n'
            ser.write(enter.encode())

            # Executa a função de leitura serial
            read_serial(ser)

            # Aguarde 5 segundos antes de recomeçar
            time.sleep(2)

    except Exception as e:
        print(f"Erro ao abrir a porta serial: {e}")

    finally:
        # Fecha a porta serial se estiver aberta
        if ser and ser.is_open:
            ser.close()
            print("Porta serial fechada.")

if __name__ == '__main__':
    main()
