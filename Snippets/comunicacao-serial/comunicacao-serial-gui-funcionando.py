import serial
import time
import PySimpleGUI as sg
import threading

# Variáveis globais para armazenar os dados
Temperatura = None
Umidade = None
window = None

# Lock para garantir acesso seguro às variáveis globais
data_lock = threading.Lock()

# Função para ler dados da porta serial
def read_serial(ser):
    global Temperatura, Umidade

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

                    with data_lock:
                        Temperatura = values[0]
                        Umidade = float(values[1])

                    update_gui_window(Temperatura, Umidade)  # Atualiza a interface gráfica com os novos valores
                    buffer = ''  # Limpa o buffer após processar os dados

            # Verifica se passou 5 segundos
            elapsed_time = time.time() - start_time
            if elapsed_time >= 1:
                break

        except Exception as e:
            print(f"Erro na leitura serial: {e}")

# Função para atualizar a interface gráfica
def update_gui_window(temperatura, umidade):
    global window  # Adicionando global window
    window['-TEMPERATURA-'].update(f'Temperatura: {temperatura}°C')
    window['-UMIDADE-'].update(f'Umidade: {umidade * 100:.0f}%')
    window.Refresh()  # Atualiza a janela

# Thread para leitura serial
def serial_thread(ser):
    while True:
        time.sleep(1)
        enter = f'\n'
        ser.write(enter.encode())
        read_serial(ser)

# Função principal
def main():
    global window  # Adicionando global window

    # Defina a porta serial do Arduino
    arduino_port = 'COM12'  # Altere para a porta correta

    # Tenta abrir a porta serial
    ser = None
    try:
        ser = serial.Serial(arduino_port, 9600, timeout=1)
        print(f"Porta serial {arduino_port} aberta com sucesso!")

        # Layout da interface gráfica
        layout = [
            [sg.Text('', size=(20, 1), key='-TEMPERATURA-')],
            [sg.Text('', size=(20, 1), key='-UMIDADE-')],
        ]

        # Cria a janela com finalize=True
        window = sg.Window('Dados Arduino', layout, size=(300, 100), finalize=True)

        

        # Aguarda o fechamento da janela
        while True:
            event, values = window.read()

            if event == sg.WINDOW_CLOSED:
                break

    except Exception as e:
        print(f"Erro ao abrir a porta serial: {e}")

    finally:
        # Fecha a porta serial se estiver aberta
        if ser and ser.is_open:
            ser.close()
            print("Porta serial fechada.")

if __name__ == '__main__':
    main()
