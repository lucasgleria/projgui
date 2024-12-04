import sqlite3
import sys
import os
import PySimpleGUI as sg
from PIL import Image, ImageTk
from io import BytesIO
import serial
from threading import Thread, Event
import time

####### FUNÇÕES DE COMUNICAÇÃO COM ARDUINO #######

def connect_to_arduino(porta, baudrate):
    try:
        ser = serial.Serial(porta, baudrate)
        return ser
    except Exception as e:
        sg.popup_error("Erro ao conectar à porta serial: " + str(e))
        return None

def start_serial_thread(ser):
    def read_serial():
        while True:
            try:
                data = ser.readline().decode().strip()
                if data:
                    print(data)
                    sg.Window.read(timeout=10)
            except Exception as e:
                print("Erro na leitura serial: " + str(e))
                break

    thread = Thread(target=read_serial)
    thread.start()
    return thread

def stop_serial_thread():
    global serial_thread_running
    serial_thread_running = False

####### FUNÇÕES PARA INTERAÇÃO COM O BANCO DE DADOS #######

def insert_image(conn, path):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO imagens (path) VALUES (?)", (path,))
    conn.commit()
    return cursor.lastrowid

def adicionar_produto(nome, registro, eixo_x, nota_fiscal_pdf_path, eixo_z, quantidade, medida, validade, imagem_path):
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO produtos (nome, registro, eixo_x, nota_fiscal_pdf_path, eixo_z, quantidade, medida, validade, path, data_criada)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (nome, registro, eixo_x, nota_fiscal_pdf_path, eixo_z, quantidade, medida, validade, imagem_path, time.strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()

def exibir_produtos_existentes():
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM produtos")
    return cursor.fetchall()

def get_product_info(nome):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos WHERE nome=?", (nome,))
    return cursor.fetchone()

def localizar_produto(filtro_nome):
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM produtos WHERE nome LIKE ?", ('%' + filtro_nome + '%',))
    return cursor.fetchall()

####### FUNÇÕES DE LAYOUT PARA INTERFACES GRÁFICAS (GUI) #######

# Janela de configurações
def config_layout():
    return [
        [sg.Text("Porta COM:"), sg.Combo(["COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9"], key="porta_COM", size=(10, 1)),
         sg.Text("Taxa Band:"), sg.Combo(['300', '1200', '2400', '4800', '9600', '19200', '38400', '57600', '74880', '115200', '230400', '250000', '500000'], key="taxa_band", size=(10, 1))],
        [sg.Button("OK")]
    ]

# Janela principal
def main_layout():
    return [
        [sg.Button("Adicionar Produto"), sg.Button("Exibir Produtos Existentes")],
        [sg.Button('Calibrar')],
        [sg.HSeparator()],
        [sg.Text("Localizar por Nome:"), sg.InputText(key="filtro_nome"), sg.Button("Localizar Produto")],
        [sg.HSeparator()],
        [sg.Text('', size=(20, 1), key='-TEMPERATURA-')],
        [sg.Text('', size=(20, 1), key='-UMIDADE-')],
        [sg.Button('Voltar')]
    ]

# Janela de adição de produtos
def add_layout():
    return [
        [sg.Text("Nome:"), sg.InputText(key="nome", size=(40, 1), pad=(54, None))],
        [sg.Text("Registro:"), sg.InputText(key="registro", size=(40, 1), pad=(40, None))],
        [sg.Text("Eixo X:"), sg.InputText(key="eixo_x", size=(40, 1), pad=(53, None))],
        [sg.Text("Eixo Z:"), sg.InputText(key="eixo_z", size=(40, 1), pad=(53, None))],
        [sg.Text("Validade:"), sg.InputText(key="validade", size=(40, 1), pad=(53, None))],
        [sg.Text("Quantidade:"), sg.InputText(key="quantidade", size=(20, 1), pad=(25, None)),
         sg.Combo(['unid', 'mmg', 'mg', 'g', 'ml'], tooltip="choose something", key="medida", size=(7, 1))],
        [sg.Button("Selecionar Imagem", key="selecionar_imagem"), sg.Button("Limpar Imagem", key="limpar_imagem")],
        [sg.Image(key='-IMAGE-', size=(300, 300), pad=(0, 0))],
        [sg.Text("Nota Fiscal:"), sg.Input(key="-NOTA_FISCAL_PDF-"), sg.FileBrowse(key="-BROWSE_PDF-", file_types=(("PDF Files", "*.pdf"),))],
        [sg.Button("Adicionar")],
        [sg.Text("", visible=False, key="path")]
    ]

# Janela de informações do produto
def info_layout(has_selected_image=False, path_imagem=None):
    layout = [
        [sg.Text("Nome:"), sg.Text("", key="nome", size=(40, 1), pad=(54, None))],
        [sg.Text("Registro:"), sg.Text("", key="registro", size=(40, 1), pad=(40, None))],
        [sg.Text("Validade:"), sg.Text("", key="validade", size=(40, 1))],
        [sg.Text("Quantidade:"), sg.Text("", key="quantidade", size=(20, 1), pad=(25, None))],
        [sg.Text("Medida da Quantidade: "), sg.Text("", key="medida")],
        [sg.Text("Eixo X:"), sg.Text("", key="eixo_x", size=(40, 1), pad=(53, None))],
        [sg.Text("Eixo Z:"), sg.Text("", key="eixo_z", size=(40, 1), pad=(53, None))],
        [sg.Image(key='-PRODUCT_IMAGE-', size=(300, 300), pad=(0, 0), expand_y=False, expand_x=False, visible=False)],
        [sg.Button("Guardar Produto"), sg.Button("Retirar Produto"), sg.Button("Limpar Produto")],
        [sg.Button("Visualizar a Nota Fiscal")]
    ]

    if has_selected_image:
        layout[-2].insert(0, sg.Image(key='-PRODUCT_IMAGE-', visible=True))

    return layout

# Janela de limpeza do produto na hora da retirada
def take_off_layout():
    return [
        [sg.Text("Deseja realizar limpeza?")],
        [sg.Button("Sim"), sg.Button("Não")]
    ]

# Janela de Carregamento
def loading_layout():
    posicao_x = 800
    posicao_y = 300

    layout = [
        [sg.Text("Estou analisando a imagem fornecida\n\nIsso pode demorar um pouco...", justification='center')]
    ]
    loading_window = sg.Window("Loading", layout, finalize=True, size=(300, 100), location=(posicao_x, posicao_y), keep_on_top=True)
    return loading_window

# Janela de escolha
def choose_layout(nome):
    layout = [
        [sg.Text("Escolha o nome correto:")],
        [sg.Listbox(values=nome, size=(30, len(nome)), key="-NOME-")],
        [sg.Button("OK")]
    ]
    choose_window = sg.Window("Escolha o nome correto", layout, finalize=True)
    return choose_window

####### CRIAÇÃO E CONEXÃO DO BANCO DE DADOS #######

try:
    # Conexão com o Banco de Dados
    with sqlite3.connect("banco-para-apresentacao.db") as conn:
        cursor = conn.cursor()

        # Criando tabelas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS imagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL
        )
    ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos 
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            registro TEXT NOT NULL,
            eixo_x TEXT NOT NULL,
            nota_fiscal_pdf_path TEXT NOT NULL,  
            eixo_z TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            medida TEXT NOT NULL,
            validade DATE NOT NULL,
            path TEXT,
            data_criada TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    ''')

        conn.commit()

except sqlite3.Error as e:
    sg.popup_error("Erro ao conectar ao banco de dados: " + str(e))
    sys.exit()

####### FUNÇÕES PARA CARREGAR E EXIBIR IMAGEM #######

def load_and_display_image(image_path, window, image_element_key):
    try:
        image = Image.open(image_path)
        image.thumbnail((300, 300))
        bio = BytesIO()
        image.save(bio, format="PNG")
        window[image_element_key].update(data=bio.getvalue())
    except Exception as e:
        sg.popup_error("Erro ao carregar a imagem: " + str(e))

####### FUNÇÕES PARA EXTRAÇÃO DE INFORMAÇÕES COM TIMEOUT #######

def extract_info_with_timeout(image_path, timeout=10):
    def extract_info(event, result):
        try:
            # Simulando extração de informações com delay
            time.sleep(15)  # Remova esta linha na implementação real
            result.append({
                'nome': 'Nome extraído',
                'registro': 'Registro extraído',
                'eixo_x': 'Eixo X extraído',
                'eixo_z': 'Eixo Z extraído',
                'validade': 'Validade extraída',
                'quantidade': 'Quantidade extraída',
                'medida': 'Medida extraída',
            })
        except Exception as e:
            result.append(None)
        finally:
            event.set()

    event = Event()
    result = []

    thread = Thread(target=extract_info, args=(event, result))
    thread.start()
    thread.join(timeout)

    if not event.is_set():
        return {
            'nome': 'Informação não encontrada',
            'registro': 'Informação não encontrada',
            'eixo_x': 'Informação não encontrada',
            'eixo_z': 'Informação não encontrada',
            'validade': 'Informação não encontrada',
            'quantidade': 'Informação não encontrada',
            'medida': 'Informação não encontrada',
        }
    return result[0] if result else {
        'nome': 'Informação não encontrada',
        'registro': 'Informação não encontrada',
        'eixo_x': 'Informação não encontrada',
        'eixo_z': 'Informação não encontrada',
        'validade': 'Informação não encontrada',
        'quantidade': 'Informação não encontrada',
        'medida': 'Informação não encontrada',
    }

####### INTERFACE PRINCIPAL DO PROGRAMA #######

def main():
    global serial_thread_running
    global ser

    serial_thread_running = True
    ser = None
    image_path = None

    # Criação da janela de configuração inicialmente
    config_window = sg.Window("Configurações", config_layout())
    main_window = None

    while True:
        window, event, values = sg.read_all_windows(timeout=100)

        if window is None:
            continue

        # Depuração para verificar o evento e a janela ativa
        print(f"Evento: {event}, Janela: {window.Title if window else 'None'}")

        if event == sg.WINDOW_CLOSED or event == 'Voltar':
            if window == config_window:
                break
            else:
                window.hide()
                main_window.un_hide()

        if event == 'OK' and window == config_window:
            porta_COM = values['porta_COM']
            taxa_band = values['taxa_band']
            ser = connect_to_arduino(porta_COM, taxa_band)
            if ser:
                start_serial_thread(ser)
                config_window.hide()
                if not main_window:
                    main_window = sg.Window("Sistema de Produtos", main_layout())
                else:
                    main_window.un_hide()

        if event == 'Adicionar Produto' and window == main_window:
            add_window = sg.Window("Adicionar Produto", add_layout())
            main_window.hide()

        if event == 'Exibir Produtos Existentes' and window == main_window:
            produtos = exibir_produtos_existentes()
            produtos_nome = [produto[0] for produto in produtos]
            if produtos_nome:
                choose_window = choose_layout(produtos_nome)
                window.hide()

        if event == "Adicionar" and window == add_window:
            nome = values['nome']
            registro = values['registro']
            eixo_x = values['eixo_x']
            eixo_z = values['eixo_z']
            validade = values['validade']
            quantidade = values['quantidade']
            medida = values['medida']
            nota_fiscal_pdf_path = values['-NOTA_FISCAL_PDF-']
            path = values['path']

            if all([nome, registro, eixo_x, eixo_z, validade, quantidade, medida, path, nota_fiscal_pdf_path]):
                adicionar_produto(nome, registro, eixo_x, nota_fiscal_pdf_path, eixo_z, quantidade, medida, validade, path)
                sg.popup("Produto adicionado com sucesso!")
                add_window.close()
                main_window.un_hide()
            else:
                sg.popup_error("Por favor, preencha todos os campos.")

        if event == "Selecionar Imagem" and window == add_window:
            file_path = sg.popup_get_file('Escolha uma imagem', file_types=(("Image Files", "*.png;*.jpg;*.jpeg;*.bmp"),))
            if file_path:
                load_and_display_image(file_path, window, '-IMAGE-')
                window['path'].update(value=file_path)

                loading_window = loading_layout()
                loading_window.read(timeout=100)

                def run_extraction():
                    info = extract_info_with_timeout(file_path)
                    window.write_event_value("ExtractionComplete", info)

                Thread(target=run_extraction).start()

        if event == "ExtractionComplete" and window == add_window:
            loading_window.close()
            info = values[event]

            window['nome'].update(info['nome'])
            window['registro'].update(info['registro'])
            window['eixo_x'].update(info['eixo_x'])
            window['eixo_z'].update(info['eixo_z'])
            window['validade'].update(info['validade'])
            window['quantidade'].update(info['quantidade'])
            window['medida'].update(info['medida'])

        if event == "Limpar Imagem" and window == add_window:
            window['-IMAGE-'].update(data=None)
            window['path'].update(value="")

        if event == "Localizar Produto" and window == main_window:
            filtro_nome = values['filtro_nome']
            produtos_localizados = localizar_produto(filtro_nome)
            produtos_nome = [produto[0] for produto_localizado in produtos_localizados]
            if produtos_nome:
                choose_window = choose_layout(produtos_nome)
                window.hide()
            else:
                sg.popup("Nenhum produto encontrado com esse nome.")

        if event == "OK" and window == choose_window:
            nome_selecionado = values['-NOME-'][0]
            produto_info = get_product_info(nome_selecionado)
            if produto_info:
                nome, registro, eixo_x, nota_fiscal_pdf_path, eixo_z, quantidade, medida, validade, path = produto_info[1:10]
                has_selected_image = path is not None
                path_imagem = path if has_selected_image else None
                info_window = sg.Window("Informações do Produto", info_layout(has_selected_image, path_imagem))
                choose_window.close()
                if has_selected_image:
                    load_and_display_image(path_imagem, info_window, '-PRODUCT_IMAGE-')

        if event == "Guardar Produto" and window == info_window:
            sg.popup("Produto guardado com sucesso!")
            info_window.close()
            main_window.un_hide()

        if event == "Retirar Produto" and window == info_window:
            take_off_window = sg.Window("Limpeza", take_off_layout())
            info_window.hide()

        if event == "Sim" and window == take_off_window:
            sg.popup("Produto retirado com sucesso! Realizando limpeza...")
            take_off_window.close()
            main_window.un_hide()

        if event == "Não" and window == take_off_window:
            sg.popup("Produto retirado com sucesso! Sem realizar limpeza...")
            take_off_window.close()
            main_window.un_hide()

    stop_serial_thread()
    if ser:
        ser.close()

if __name__ == "__main__":
    main()