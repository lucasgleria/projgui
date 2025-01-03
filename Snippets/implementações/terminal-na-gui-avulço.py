import serial
import time
import PySimpleGUI as sg
import threading
import sys
import io

data_lock = threading.Lock()

velx = None
vely = None
velz = None

aclx = None
acly = None
aclz = None

posx = None
posy = None
posz = None

# Redireciona prints para atualizar a área de log da interface
class DualOutput(io.StringIO):
    def __init__(self, element):
        super().__init__()
        self.element = element
        self.console = sys.__stdout__  # Salva o stdout original do terminal

    def write(self, message):
        # Envia para o console original
        self.console.write(message)
        self.console.flush()
        # Envia para a GUI
        self.element.update(value=message, append=True)
        self.element.Widget.yview_moveto(1.0)  # Scroll até o final

    def flush(self):
        self.console.flush()


# Função para ler dados da porta serial
def read_serial_m114(ser):
    global posx, posy, posz  # Tornar variáveis globais acessíveis dentro da função
    start_time = time.time()  # Tempo inicial

    while True:
        try:
            data = ser.readline().decode('utf-8').strip()
            print(f"Dados recebidos: {data}")  # Imprimir a string recebida no console

            if data.startswith("X:"):
                # Filtra os valores de X, Y e Z
                values = data.split()
                if len(values) >= 3:
                    posx = values[0].split(':')[1]
                    posy = values[1].split(':')[1]
                    posz = values[2].split(':')[1]

            # Verifica se passou 1 segundo
            elapsed_time = time.time() - start_time
            if elapsed_time >= 1:
                break

        except Exception as e:
            print(f"Erro na leitura serial: {e}")

def update_gui_window_m114(posx, posy, posz):
    global window  # Adicionando global window
    window['posicao'].update(f'X: {posx}\tY: {posy}\tZ: {posz}')
    window.Refresh()

# Thread para leitura serial
def serial_thread_m114(ser):
    while True:
        time.sleep(5)
        enter = 'M114\n'
        print("Enviado")
        ser.write(enter.encode())
        read_serial_m114(ser)


# Função para ler dados da porta serial
def read_serial_m203(ser):
    global velx, vely, velz  # Tornar variáveis globais acessíveis dentro da função
    start_time = time.time()  # Tempo inicial

    while True:
        try:
            data = ser.readline().decode('utf-8').strip()
            print(f"Dados recebidos m203: {data}")  # Imprimir a string recebida no console

            if data.startswith("M203 "):
                # Filtra os valores de X, Y e Z
                values = data.split()
                for value in values:
                    if value.startswith("X"):
                        velx = value[1:]
                    elif value.startswith("Y"):
                        vely = value[1:]
                    elif value.startswith("Z"):
                        velz = value[1:]

            # Verifica se passou 1 segundo
            elapsed_time = time.time() - start_time
            if elapsed_time >= 1:
                break

        except Exception as e:
            print(f"Erro na leitura serial: {e}")

def update_gui_window_m203(velx, vely, velz):
    global window  # Adicionando global window
    window['velx'].update(f'{velx}')
    window['vely'].update(f'{vely}')
    window['velz'].update(f'{velz}')
    window.Refresh()

# Thread para leitura serial
def serial_thread_m203(ser):
    while True:
        time.sleep(7)
        enter = 'M203\n'
        print("Enviado m203")
        ser.write(enter.encode())
        read_serial_m203(ser)


# Função para ler dados da porta serial
def read_serial_m201(ser):
    global aclx, acly, aclz  # Tornar variáveis globais acessíveis dentro da função
    start_time = time.time()  # Tempo inicial

    while True:
        try:
            data = ser.readline().decode('utf-8').strip()
            print(f"Dados recebidos m201: {data}")  # Imprimir a string recebida no console

            if data.startswith("M201 "):
                # Filtra os valores de X, Y e Z
                values = data.split()
                for value in values:
                    if value.startswith("X"):
                        aclx = value[1:]
                    elif value.startswith("Y"):
                        acly = value[1:]
                    elif value.startswith("Z"):
                        aclz = value[1:]

            # Verifica se passou 1 segundo
            elapsed_time = time.time() - start_time
            if elapsed_time >= 1:
                break

        except Exception as e:
            print(f"Erro na leitura serial: {e}")

def update_gui_window_m201(aclx, acly, aclz):
    global window  # Adicionando global window
    window['aclx'].update(f'{aclx}')
    window['acly'].update(f'{acly}')
    window['aclz'].update(f'{aclz}')
    window.Refresh()

# Thread para leitura serial
def serial_thread_m201(ser):
    while True:
        time.sleep(9)
        enter = 'M201\n'
        print("Enviado m201")
        ser.write(enter.encode())
        read_serial_m201(ser)

# Função para enviar novos valores de velocidade para o Arduino
def send_new_velocity_values(ser, new_velx, new_vely, new_velz):
    try:
        enter = f'M203 X{new_velx} Y{new_vely} Z{new_velz}\n'
        print(f"Enviando novos valores de velocidade: {enter.strip()}")
        ser.write(enter.encode())
    except Exception as e:
        print(f"Erro ao enviar novos valores de velocidade via serial: {e}")

# Função para enviar novos valores de aceleração para o Arduino
def send_new_acceleration_values(ser, new_aclx, new_acly, new_aclz):
    try:
        enter = f'M201 X{new_aclx} Y{new_acly} Z{new_aclz}\n'
        print(f"Enviando novos valores de aceleração: {enter.strip()}")
        ser.write(enter.encode())
    except Exception as e:
        print(f"Erro ao enviar novos valores de aceleração via serial: {e}")
        

# Função para criar a janela de log separada
def create_log_window():
    log_layout = [
        [sg.Text('Saída do Console:')],
        [sg.Multiline('', size=(60, 20), key='log_output', autoscroll=True, disabled=True)]
    ]
    return sg.Window('Log de Console', log_layout, finalize=True)

# Função principal
def main():
    global window, log_window  # Tornar as janelas globais para uso em outras funções

    # Defina a porta serial do Arduino
    arduino_port = 'COM6'  # Altere para a porta correta

    # Tenta abrir a porta serial
    ser = None
    try:
        ser = serial.Serial(arduino_port, 115200, timeout=1)
        print(f"Porta serial {arduino_port} aberta com sucesso!")
        try:
            # Layout da interface gráfica principal
            layout = [
                [sg.TabGroup([[  # Grupo de abas
                    sg.Tab('Velocidade', [
                        [sg.Text("Velocidades: ")],
                        [sg.Text('X: '), sg.InputText(key="velx")],
                        [sg.Text('Y: '), sg.InputText(key="vely")],
                        [sg.Text('Z: '), sg.InputText(key="velz")],
                        [sg.Button('Atualizar', key='-UPDATE_M203-')],  # Botão para atualizar velocidade
                        [sg.Button('Ajustar', key='ajust-vel')]
                    ]),
                    sg.Tab('Aceleração', [
                        [sg.Text("Acelerações: ")],
                        [sg.Text('X: '), sg.InputText(key="aclx")],
                        [sg.Text('Y: '), sg.InputText(key="acly")],
                        [sg.Text('Z: '), sg.InputText(key="aclz")],
                        [sg.Button('Atualizar', key='-UPDATE_M201-')],  # Botão para atualizar aceleração
                        [sg.Button('Ajustar', key='ajust-acl')]
                    ]),
                    sg.Tab('Posição', [
                        [sg.Text('Posição: ')], [sg.Text('', key="posicao")],
                        [sg.Button('Atualizar', key='-UPDATE_M114-')]  # Botão para atualizar posição
                    ])
                ]], key='tabgroup')]
            ]

            # Cria a janela principal e a janela de log com finalize=True
            window = sg.Window('Dados Arduino', layout, size=(400, 300), finalize=True)
            log_window = create_log_window()

            # Redireciona o print para o Multiline log_output da janela de log
            sys.stdout = DualOutput(log_window['log_output'])

            # Cria e inicia as threads para leitura serial
            thread_m114 = threading.Thread(target=serial_thread_m114, args=(ser,), daemon=True)
            thread_m114.start()

            thread_m203 = threading.Thread(target=serial_thread_m203, args=(ser,), daemon=True)
            thread_m203.start()

            thread_m201 = threading.Thread(target=serial_thread_m201, args=(ser,), daemon=True)
            thread_m201.start()

            # Loop para ambas as janelas
            while True:
                # Leitura da janela principal e da janela de log
                window_event, window_values = window.read(timeout=100)
                log_event, _ = log_window.read(timeout=100)

                # Eventos da janela principal
                if window_event == sg.WINDOW_CLOSED or log_event == sg.WINDOW_CLOSED:
                    break
                elif window_event == '-UPDATE_M114-':
                    update_gui_window_m114(posx, posy, posz)
                elif window_event == '-UPDATE_M203-':
                    update_gui_window_m203(velx, vely, velz)
                elif window_event == '-UPDATE_M201-':
                    update_gui_window_m201(aclx, acly, aclz)
                elif window_event == 'ajust-vel':
                    new_velx = window_values['velx']
                    new_vely = window_values['vely']
                    new_velz = window_values['velz']
                    send_new_velocity_values(ser, new_velx, new_vely, new_velz)
                    # Atualiza os campos na GUI com os novos valores
                    window['velx'].update(new_velx)
                    window['vely'].update(new_vely)
                    window['velz'].update(new_velz)
                elif window_event == 'ajust-acl':
                    new_aclx = window_values['aclx']
                    new_acly = window_values['acly']
                    new_aclz = window_values['aclz']
                    send_new_acceleration_values(ser, new_aclx, new_acly, new_aclz)
                    # Atualiza os campos na GUI com os novos valores
                    window['aclx'].update(new_aclx)
                    window['acly'].update(new_acly)
                    window['aclz'].update(new_aclz)

        except Exception as e:
            print(f"Erro em gerar a GUI: {e}")

    except Exception as e:
        print(f"Erro ao abrir a porta serial: {e}")

    finally:
        # Fecha a porta serial e ambas as janelas
        if ser and ser.is_open:
            ser.close()
            print("Porta serial fechada.")
        window.close()
        log_window.close()

if __name__ == '__main__':
    main()