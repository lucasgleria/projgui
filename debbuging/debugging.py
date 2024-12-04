####### IMPORTAÇÕES #######

import serial.tools.list_ports
from PIL import Image, ImageTk
import PySimpleGUI as sg
from easyocr import Reader
from io import BytesIO
import pyocr.builders
import pytesseract
import webbrowser
import threading
import datetime
import sqlite3
import easyocr
import serial
import pyocr
import time
import fitz
import sys
import cv2
import os
import re

####### LISTAS #######

# Lista de palavras-chave para identificar o nome de medicamentos
medicine_keywords = [
    'abacavir', 'abiraterona', 'acetaminofeno']

# Lista de unidades de medida permitidas
medida_keywords = ["g", "mg", "mmg", "mcg", "L", "ml", "mml", "u"]

####### CONFIGURAÇÕES #######

# COnfigurações do PysimpleGUI
sg.theme('lightblue7')
sg.set_options(font=('Arial', 12))

# Lock para garantir acesso seguro às variáveis globais pelo threading
data_lock = threading.Lock()

####### BIBLIOTECAS #######

informacoes_extraidas = {"nome": None, 'quantidade': None, 'medida': None}

####### VÁRIAVEIS #######

# Variáveis Flags
serial_thread_running = True
has_selected_image = False
serial_thread_stop_event = threading.Event()

# Variáveis setadas como None para evitar bugs
serial_thread_instance = None
nota_fiscal_pdf_path = None
ultima_imagem_id = None
main_window = None
Temperatura = None
quantidade = None
filepath = None
validade = None
registro = None
Umidade = None
eixo_x = None
eixo_z = None
medida = None
path = None
nome = None

####### FUNÇÕES GLOBAIS #######

# Função para conexão com o arduíno através da porta serial


def connect_to_arduino(porta_COM, taxa_band):
    try:
        if not porta_COM:
            raise ValueError('Campo Porta COM obrigatório!')
        elif not taxa_band:
            raise ValueError('Campo Taxa Band obrigatório!')
        elif not taxa_band.isnumeric():
            raise ValueError('A Taxa Band deve ser um valor numérico!')

        ser = serial.Serial(porta_COM, int(taxa_band), timeout=2)
        return ser

    except ValueError as ve:
        sg.popup(ve, title='Erro de Conexão', non_blocking=True, font=(
            'Helvetica', 10), keep_on_top=True, auto_close_duration=3)
        return None

# Função para resetar os valores dos inputs de configurações


def reset_config_values(window):
    window['porta_COM'].update('')
    window['taxa_band'].update('')

# Função para limpar a entrada serial


def clear_serial_input(ser):
    if ser:
        while ser.in_waiting:
            ser.read(ser.in_waiting)

# Função para adicionar produtos


def adicionar_produto(nome, registro, eixo_x, nota_fiscal_pdf_path, eixo_z, quantidade, medida, validade, path_imagem):
    global has_selected_image
    data_criada = datetime.datetime.now()
    cursor.execute('INSERT INTO produtos (nome, registro, eixo_x, nota_fiscal_pdf_path, eixo_z, quantidade, medida, path, validade, data_criada) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   (nome, registro, eixo_x, nota_fiscal_pdf_path, eixo_z, quantidade, medida, path_imagem, validade, data_criada))
    cursor.execute('INSERT INTO imagens (path) VALUES (?)', (path_imagem,))
    conn.commit()
    global ultima_imagem_id
    ultima_imagem_id = cursor.lastrowid
    sg.popup(f"O produto {nome} foi adicionado.", title='Produto adicionado',
             non_blocking=True, font=('Helvetica', 10), keep_on_top=True)
    has_selected_image = path_imagem is not None

# Função para exibir produtos


def exibir_produtos_existentes():
    cursor.execute('SELECT nome, registro, validade FROM produtos')
    produtos = cursor.fetchall()
    return produtos

# Função para localizar produtos


def localizar_produto(filtro_nome):
    cursor.execute(
        'SELECT nome, registro FROM produtos WHERE nome LIKE ?', ('%' + filtro_nome + '%',))
    produtos = cursor.fetchall()
    return produtos

# Função para pegar as informações do produto


def get_product_info(product_name):
    cursor.execute(
        'SELECT nome, nota_fiscal_pdf_path, registro, quantidade, medida, eixo_x, eixo_z, path, validade FROM produtos WHERE nome = ?', (product_name,))
    product_info = cursor.fetchone()

    if product_info:
        nome, nota_fiscal_pdf_path, registro, quantidade, medida, eixo_x, eixo_z, path_imagem, validade = product_info

        # Verifica se há uma imagem associada
        if path_imagem and os.path.exists(path_imagem):
            return nome, nota_fiscal_pdf_path, registro, quantidade, medida, eixo_x, eixo_z, path_imagem, validade
        else:
            return nome, nota_fiscal_pdf_path, registro, quantidade, medida, eixo_x, eixo_z, None, validade
    else:
        return None

# Função para exibir em tabela


def products_table_layout(products):
    header = ["Nome", "Registro", "Validade"]
    data = [[product[0], product[1], get_product_info(
        product[0])[-1]] for product in products]

    return [
        [sg.Table(values=data, headings=header, auto_size_columns=False, justification='center',
                  display_row_numbers=False, hide_vertical_scroll=True, num_rows=min(25, len(data)),
                  col_widths=[20, 20, 20], key="table", enable_events=True)]
    ]

# Função para loop de informações do produto


def products_info_loop():
    nome, nota_fiscal_pdf_path, registro, quantidade, medida, eixo_x, eixo_z, path_imagem, validade = product_info
    main_window.hide()

    info_product_window = sg.Window("Informações do Produto", info_layout(
        has_selected_image=(path_imagem is not None), path_imagem=path_imagem), finalize=True)

    # Atualiza os elementos de text na janela de informações do produto
    info_product_window["nome"].update(nome)
    info_product_window["registro"].update(registro)
    info_product_window["quantidade"].update(quantidade)
    info_product_window["medida"].update(medida)
    info_product_window["eixo_x"].update(eixo_x)
    info_product_window["eixo_z"].update(eixo_z)
    info_product_window["validade"].update(validade)

    if path_imagem:
        pil_image = Image.open(path_imagem)
        pil_image = pil_image.resize((300, 300), Image.ANTIALIAS if hasattr(
            Image, 'ANTIALIAS') else Image.LANCZOS)
        tk_image = ImageTk.PhotoImage(pil_image)
        info_product_window['-PRODUCT_IMAGE-'].update(
            data=tk_image, visible=True)
    else:
        info_product_window['-PRODUCT_IMAGE-'].update(data=None, visible=False)

    while True:
        info_event, info_values = info_product_window.read()

        if info_event == sg.WINDOW_CLOSED:
            break

        elif info_event == 'Visualizar a Nota Fiscal':
            if nota_fiscal_pdf_path:
                view_pdf_window(nota_fiscal_pdf_path)
            else:
                sg.popup("Nenhum PDF associado a este produto.",
                         title="Informação", keep_on_top=True)

        elif info_event == 'Guardar Produto':
            try:
                guardar = f'X{eixo_x}Z{eixo_z}GUARDAR' + '\n'
                ser.write(guardar.encode())
                sg.popup(f"O produto foi guardado.", title='Produto guardado',
                         non_blocking=True, font=('Helvetica', 10), keep_on_top=True)
                info_product_window.close()
                products_table_window.close()
                main_window.un_hide()
            except Exception as e:
                sg.popup_error('Nenhuma porta serial conectada.\n\n Impossível fazer a comunicação.', title='Produtos Não Encontrados',
                               non_blocking=True, font=('Helvetica', 10), keep_on_top=True)
                print("Erro em Guardar: " + str(e))

        elif info_event == 'Limpar Produto':
            try:
                limpar = f'X{eixo_x}Z{eixo_z}LIMPAR' + '\n'
                ser.write(limpar.encode())
                sg.popup(f"O produto foi limpo.", title='Produto limpo',
                         non_blocking=True, font=('Helvetica', 10), keep_on_top=True)
                info_product_window.close()
                products_table_window.close()
                main_window.un_hide()
            except Exception as e:
                sg.popup_error('Nenhuma porta serial conectada.\n\n Impossível fazer a comunicação.', title='Produtos Não Encontrados',
                               non_blocking=True, font=('Helvetica', 10), keep_on_top=True)
                print("Erro em Limpar: " + str(e))

        elif info_event == 'Retirar Produto':
            info_product_window.hide()

            takeOff_product_window = sg.Window(
                "Retirada do Produto", take_off_layout(), finalize=True)

            while True:
                takeOff_event, takeOff_values = takeOff_product_window.read()

                if takeOff_event == sg.WINDOW_CLOSED:
                    takeOff_product_window.close()
                    break

                elif takeOff_event == 'Sim':
                    try:
                        teste_sim = f'X{eixo_x}Z{eixo_z}RETIRAR' + '\n'
                        ser.write(teste_sim.encode())
                        sg.popup(f"O produto foi retirado.", title='Produto retirado',
                                 non_blocking=True, font=('Helvetica', 10), keep_on_top=True)
                        takeOff_product_window.close()
                        info_product_window.close()
                        products_table_window.close()
                        main_window.un_hide()
                    except Exception as e:
                        sg.popup_error('Nenhuma porta serial conectada.\n\n Impossível fazer a comunicação.', title='Produtos Não Encontrados',
                                       non_blocking=True, font=('Helvetica', 10), keep_on_top=True)
                        print("Erro em Retirar -> Sim: " + str(e))

                elif takeOff_event == 'Não':
                    try:
                        teste_nao = f'X{eixo_x}Z{eixo_z}RETIRARN' + '\n'
                        ser.write(teste_nao.encode())
                        sg.popup(f"O produto foi retirado.", title='Produto retirado',
                                 non_blocking=True, font=('Helvetica', 10), keep_on_top=True)
                        takeOff_product_window.close()
                        info_product_window.close()
                        products_table_window.close()
                        main_window.un_hide()
                    except Exception as e:
                        sg.popup_error('Nenhuma porta serial conectada.\n\n Impossível fazer a comunicação.', title='Produtos Não Encontrados',
                                       non_blocking=True, font=('Helvetica', 10), keep_on_top=True)
                        print("Erro em Retirar-> Não: " + str(e))

# Função para leitura e comunicação serial


def read_serial(ser):
    global Temperatura, Umidade

    buffer = ''  # Buffer para armazenar dados parciais
    start_time = time.time()  # Tempo inicial

    while True:
        if serial_thread_stop_event.is_set():
            break  # Sai do loop se o evento de parada for sinalizado

        try:
            data = ser.readline().decode('utf-8')
            if '\n' in data:
                buffer += data
                values = buffer.split('\n')
                if len(values) >= 2 and values[0] and values[1]:
                    # Filtra valores vazios
                    values = [str(value) for value in values if value]

                    with data_lock:
                        Temperatura = values[0]
                        Umidade = float(values[1])

                    # Atualiza a interface gráfica com os novos valores
                    update_gui_window(Temperatura, Umidade)
                    buffer = ''  # Limpa o buffer após processar os dados

            # Verifica se passou 5 segundos
            elapsed_time = time.time() - start_time
            if elapsed_time >= 5:
                break

        except Exception as e:
            print(f"Erro na leitura serial: {e}")
            break

# Função para atualizar a interface gráfica


def update_gui_window(temperatura, umidade):
    global main_window  # Adicionando global window
    main_window['-TEMPERATURA-'].update(f'Temperatura: {temperatura}°C')
    main_window['-UMIDADE-'].update(f'Umidade: {umidade * 100:.0f}%')
    main_window.Refresh()  # Atualiza a janela

# Thread para leitura serial

def serial_thread(ser):
    global serial_thread_running
    while serial_thread_running:
        try:
            if serial_thread_stop_event.is_set():
                break  # Sai do loop se o evento de parada for sinalizado
            if ser and ser.is_open:
                enter = f'\n'
                ser.write(enter.encode())
                read_serial(ser)
        except Exception as e:
            print("Erro na leitura serial:", str(e))
            break


def stop_serial_thread():
    global serial_thread_running
    serial_thread_running = False
    serial_thread_stop_event.set()  # Sinaliza o evento de parada
    if serial_thread_instance:
        serial_thread_instance.join()  # Aguarda a thread terminar


def start_serial_thread(ser):
    global serial_thread_instance, serial_thread_running, serial_thread_stop_event
    serial_thread_stop_event.clear()  # Redefine o evento de parada
    serial_thread_running = True
    serial_thread_instance = threading.Thread(
        target=serial_thread, args=(ser,), daemon=True)
    serial_thread_instance.start()


# Função para avançar páginas do pdf


def display_page(image_elem, pdf_document, page_num, window_size):
    page = pdf_document[page_num]

    # Obtém a largura e altura da página
    image_width = int(page.rect.width)
    image_height = int(page.rect.height)

    # Obtém o tamanho da janela
    window_width, window_height = window_size

    # Calcula o zoom necessário para caber a página na janela
    zoom_x = window_width / image_width
    zoom_y = window_height / image_height
    zoom = min(zoom_x, zoom_y)

    # Renderiza a página com o zoom calculado
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))

    # Atualiza a imagem na janela
    image_elem.update(data=pix.tobytes())

    return page_num + 1  # Retorna o número da página atualizado

# Função para visualização da janela do pdf


def view_pdf_window(nota_fiscal_pdf_path):
    pdf_document = fitz.open(nota_fiscal_pdf_path)
    num_pages = pdf_document.page_count

    window_size = (500, 425)
    layout = [
        [sg.Text(f'Página 1 de {num_pages}', key='-PAGE_COUNTER-')],
        [sg.Button('Anterior'), sg.Button('Próxima'), sg.Button(
            'Abrir no Navegador'), sg.Button('Fechar')],
        [sg.Image(key='-IMAGE-')]
    ]

    window = sg.Window('Visualizar PDF', layout,
                       finalize=True, size=window_size)
    image_elem = window['-IMAGE-']
    page_num = 0

    while True:
        display_page_num = display_page(
            image_elem, pdf_document, page_num, window_size)
        window['-PAGE_COUNTER-'].update(
            f'Página {display_page_num} de {num_pages}')

        event, _ = window.read()

        if event == sg.WINDOW_CLOSED or event == 'Fechar':
            break
        elif event == 'Próxima' and page_num < num_pages - 1:
            page_num += 1
        elif event == 'Anterior' and page_num > 0:
            page_num -= 1
        elif event == 'Abrir no Navegador':
            webbrowser.open_new_tab(nota_fiscal_pdf_path)

    pdf_document.close()
    window.close()

# Função para coletar o path do pdf


def get_pdf_path():
    cursor.execute(
        'SELECT nota_fiscal_pdf_path FROM pdfs ORDER BY id DESC LIMIT 1')
    nota_fiscal_pdf_path = cursor.fetchone()
    conn.close()
    if nota_fiscal_pdf_path:
        return nota_fiscal_pdf_path[0]
    else:
        return None

# Função para inserir o path da imagem selecionada ao banco de dados de imagens


def insert_image(conn, path_imagem):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO imagens (path) VALUES (?)', (path_imagem,))
    conn.commit()
    global ultima_imagem_id
    ultima_imagem_id = cursor.lastrowid  # Obtém o ID da última imagem inserida

# Função para obter o path da imagem da tabela imagens do banco de dados


def get_image(conn, imagem_id):
    cursor = conn.cursor()
    cursor.execute('SELECT path FROM imagens WHERE id = ?', (imagem_id,))
    path = cursor.fetchone()
    return path[0] if path else None

# Função para realizar OCR com easyocr


def ocr_with_easyocr(image):
    reader = easyocr.Reader(['pt'])
    results = reader.readtext(image)
    extracted_text = [result[1] for result in results]
    return " ".join(extracted_text)

# Função para extrair o nome da imagem


def extract_nome(add_product_window, conn, choose_window, attempt=1):
    global ultima_imagem_id
    path = get_image(conn, ultima_imagem_id)
    if path:
        if attempt == 1:
            image = cv2.imread(path)
            text = ocr_with_easyocr(image)
        elif attempt == 2:
            image = Image.open(path)
            text = pytesseract.image_to_string(image)
        else:
            tools = pyocr.get_available_tools()
            if len(tools) == 0:
                sg.popup_error(
                    "Nenhum motor OCR disponível. Certifique-se de ter o Tesseract-OCR instalado.")
                return None

            tool = tools[0]
            with Image.open(path) as img:
                text = tool.image_to_string(
                    img, builder=pyocr.builders.TextBuilder())

        nome = find_nome(text)

        if len(nome) > 1:
            choose_window = choose_layout(nome)

            while True:
                choose_event, choose_values = choose_window.read()

                if choose_event == sg.WIN_CLOSED or choose_event == "OK":
                    break

            choose_window.close()

            if choose_values["-NOME-"]:
                nome_medicamento = choose_values["-NOME-"][0]
            else:
                sg.popup_error("Selecione um medicamento.")
                return

        elif len(nome) == 1:
            nome_medicamento = nome[0]

        else:
            sg.popup_error("Nenhum medicamento encontrado.")
            return

        add_product_window["nome"].update(
            nome_medicamento if nome_medicamento else "")

    else:
        sg.popup("Nome do medicamento não encontrado.",
                 "Informação não encontrada.")
        return None

# Função para extrair a unidade e medida da imagem


def extract_unidade_and_medida(add_product_window, conn, choose_window, attempt=1):
    global ultima_imagem_id
    path = get_image(conn, ultima_imagem_id)
    if path:
        if attempt == 1:
            image = cv2.imread(path)
            text = ocr_with_easyocr(image)
        elif attempt == 2:
            image = Image.open(path)
            text = pytesseract.image_to_string(image)
        else:
            tools = pyocr.get_available_tools()
            if len(tools) == 0:
                sg.popup_error(
                    "Nenhum motor OCR disponível. Certifique-se de ter o Tesseract-OCR instalado.")
                return None

            tool = tools[0]
            with Image.open(path) as img:
                text = tool.image_to_string(
                    img, builder=pyocr.builders.TextBuilder())

        # Calling the function to extract quantidade and medida
        quantidade, medida = find_quantidade_and_medida(text)

        if quantidade == "Quantidade não encontrada." or medida == "Medida não encontrada.":
            # Faça a mesma função rodar novamente para pegar os dados corretos, mas agora com a segunda attempt
            return extract_unidade_and_medida(add_product_window, conn, choose_window, attempt=2)
        else:
            add_product_window["quantidade"].update(
                quantidade if quantidade else "")
            add_product_window["medida"].update(medida if medida else "")
    else:
        sg.popup("Nome do medicamento não encontrado.",
                 "Informação não encontrada.")
        return None

# Função para reconhecer o nome do medicamento


def find_nome(text):
    resultados = []

    for palavra_chave in medicine_keywords:
        palavras = re.split(r'[\s\n]+', palavra_chave.lower())
        encontradas = all(p.lower() in text.lower() for p in palavras)
        if encontradas:
            resultados.append(palavra_chave.capitalize())

    return resultados if resultados else ["Medicamento não encontrado."]

# Função para reconhecer a quantidade e medida e após isso separá-las


def find_quantidade_and_medida(text):
    # Expressão regular para encontrar a quantidade e medida
    padrao = r"(\d+\s*(" + "|".join(medida_keywords) + r")\b)"
    resultado = re.findall(padrao, text, flags=re.IGNORECASE)
    if resultado:
        # Extrair a primeira ocorrência de quantidade e medida
        quantidade_medida = resultado[0][0]
        # Dividir a quantidade da medida
        partes = re.split(r"\s*(" + "|".join(medida_keywords) +
                          r")\b", quantidade_medida, flags=re.IGNORECASE)
        quantidade = partes[0].strip() if len(
            partes) > 0 else "Quantidade não encontrada"
        medida = partes[1].strip().lower() if len(
            partes) > 1 else "Medida não encontrada"
        return quantidade, medida
    else:
        return "Quantidade não encontrada.", "Medida não encontrada."


####### FUNÇÕES DE LAYOUT PARA INTERFCES GRÁFICAS (GUI) #######

# Janela de configurações
def config_layout():
    return [
        [sg.Text("Porta COM:"), sg.Combo(["COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9"], key="porta_COM", size=(10, 1)),
         sg.Text("Taxa Band:"), sg.Combo(['300', '1200', '2400', '4800', '9600', '19200', '38400', '57600', '74880',
                                          '115200', '230400', '250000', '500000'], key="taxa_band", size=(10, 1))],
        [sg.Button("OK")]
    ]

# Janela principal


def main_layout():
    return [
        [sg.Button("Adicionar Produto"), sg.Button(
            "Exibir Produtos Existentes")], [sg.Button('Calibrar')],
        [sg.HSeparator("Separador")],
        [sg.Text("Localizar por Nome:"), sg.InputText(
            key="filtro_nome"), sg.Button("Localizar Produto")],
        [sg.HSeparator("Separador")],
        [sg.Text('', size=(20, 1), key='-TEMPERATURA-')],
        [sg.Text('', size=(20, 1), key='-UMIDADE-')],
        [sg.Button('Voltar')]
    ]

# Janlea de adição de produtos


def add_layout():
    return [
        [sg.Text("Nome:"), sg.InputText(
            key="nome", size=(40, 1), pad=(54, None))],
        [sg.Text("Registro:"), sg.InputText(
            key="registro", size=(40, 1), pad=(40, None))],
        [sg.Text("Eixo X:"), sg.InputText(
            key="eixo_x", size=(40, 1), pad=(53, None))],
        [sg.Text("Eixo Z:"), sg.InputText(
            key="eixo_z", size=(40, 1), pad=(53, None))],
        [sg.Text("Validade:"), sg.InputText(
            key="validade", size=(40, 1), pad=(53, None))],
        [sg.Text("Quantidade:"), sg.InputText(key="quantidade", size=(20, 1), pad=(25, None)),
         sg.Combo(['unid', 'mmg', 'mg', 'g', 'ml'], tooltip="choose something", key="medida", size=(7, 1))],
        [sg.Button("Selecionar Imagem", key="selecionar_imagem"),
         sg.Button("Limpar Imagem", key="limpar_imagem")],
        [sg.Image(key='-IMAGE-', size=(300, 300), pad=(0, 0),)],
        [sg.Text("Nota Fiscal:"), sg.Input(key="-NOTA_FISCAL_PDF-"),
         sg.FileBrowse(key="-BROWSE_PDF-", file_types=(("PDF Files", "*.pdf"),))],
        [sg.Button("Adicionar")],
        [sg.Text("", visible=False, key="path")]
    ]

# Janela de informações do produto


def info_layout(has_selected_image=False, path_imagem=None):
    layout = [
        [sg.Text("Nome:"), sg.Text(nome, key="nome",
                                   size=(40, 1), pad=(54, None))],
        [sg.Text("Registro:"), sg.Text(
            registro, key="registro", size=(40, 1), pad=(40, None))],
        [sg.Text("Validade:"), sg.Text(
            validade, key="validade", size=(40, 1))],
        [sg.Text("Quantidade:"), sg.Text(
            quantidade, key="quantidade", size=(20, 1), pad=(25, None))],
        [sg.Text("Medida da Quantidade: "), sg.Text(medida, key="medida")],
        [sg.Text("Eixo X:"), sg.Text(
            eixo_x, key="eixo_x", size=(40, 1), pad=(53, None))],
        [sg.Text("Eixo Z:"), sg.Text(
            eixo_z, key="eixo_z", size=(40, 1), pad=(53, None))],
        [sg.Image(key='-PRODUCT_IMAGE-', size=(300, 300), pad=(0, 0),
                  expand_y=False, expand_x=False, visible=False)],
        [sg.Button("Guardar Produto"), sg.Button(
            "Retirar Produto"), sg.Button("Limpar Produto")],
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
        [sg.Text("Estou analisando a imagem fornecida\n\Isso pode demorar um pouco...",
                 justification='center')]
    ]
    loading_window = sg.Window("Loading", layout, finalize=True, size=(
        300, 100), location=(posicao_x, posicao_y), keep_on_top=True)
    return loading_window

# Janela de escolha


def choose_layout(nome):
    layout = [
        [sg.Text("Escolha o nome correto:")],
        [sg.Listbox(values=nome, size=(30, len(nome)), key="-NOME-")],
        [sg.Button("OK")]
    ]
    choose_window = sg.Window("Escolha o nome correto", layout, finalize=False)
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
            quantidade INT NOT NULL,
            medida TEXT NOT NULL,
            path TEXT NOT NULL,
            validade TEXT NOT NULL,
            data_criada DATETIME,
            data_guardada DATETIME,
            data_retirada DATETIME,
            imagem_id INTEGER,
            FOREIGN KEY (imagem_id) REFERENCES imagens(id)
        )
    ''')

except sqlite3.Error as e:
    sg.popup('Erro ao conectar ao banco de dados: ' + str(e), title='Erro',
             non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
    sys.exit(1)

####### INÍCIO DO PROGRAMA #######

# Primeira Janela chamada (de configurações)
config_window = sg.Window("Configurações", config_layout(), finalize=True)

####### LOOP PRINCIPAL DO PROFRAMA #######
while True:
    event, values = config_window.read()

    if event == sg.WINDOW_CLOSED:
        break

    elif event == 'OK':
        try:
            ser = connect_to_arduino(values["porta_COM"], values["taxa_band"])
            if ser:

                # Inicia a thread para leitura serial
                start_serial_thread(ser)

                config_window.close()
                # Janela principal é chamada após a verificação das configurações
                main_window = sg.Window(
                    "Janela Principal", main_layout(), finalize=True)

                while True:
                    event, values = main_window.read()

                    if event == sg.WINDOW_CLOSED:
                        stop_serial_thread()
                        break

                    elif event == 'Voltar':
                        stop_serial_thread()  # Encerra a thread antes de fechar a porta serial
                        
                        if ser and ser.is_open:
                            clear_serial_input(ser)
                            ser.close()
                        main_window.close()  # Fecha a janela principal
                        config_window = sg.Window(
                            "Configurações", config_layout(), finalize=True)
                        
                        reset_config_values(config_window)

                        while True:
                            event, values = config_window.read()

                            if event == sg.WINDOW_CLOSED:
                                stop_serial_thread()
                                # Encerra o programa se a janela de configuração for fechada
                                sys.exit(0)
                            
                            elif event == 'OK':
                                ser = connect_to_arduino(
                                    values["porta_COM"], values["taxa_band"])
                                
                                if ser:
                                    # Reinicia a thread serial
                                    start_serial_thread(ser)
                                    break

                        config_window.close()
                        main_window = sg.Window(
                            "Janela Principal", main_layout(), finalize=True)

                    elif event == 'Adicionar Produto':
                        main_window.hide()

                        add_product_window = sg.Window(
                            "Adicione Produtos", add_layout())

                        while True:
                            add_event, add_values = add_product_window.read()

                            if add_event == sg.WINDOW_CLOSED:
                                main_window.un_hide()
                                break

                            elif add_event == 'Adicionar':
                                nome = add_values.get("nome")
                                registro = add_values.get("registro")
                                eixo_x = add_values.get("eixo_x")
                                nota_fiscal_pdf_path = add_values.get(
                                    "-NOTA_FISCAL_PDF-")
                                eixo_z = add_values.get("eixo_z")
                                quantidade = add_values.get("quantidade")
                                medida = add_values.get("medida")
                                validade = add_values.get("validade")

                                if not nome:
                                    sg.popup('Campo Nome obrigatório!', title='Campo Obrigatório', non_blocking=True, font=(
                                        'Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                                elif not registro:
                                    sg.popup('Campo Registro obrigatório!', title='Campo Obrigatório', non_blocking=True, font=(
                                        'Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                                elif not nota_fiscal_pdf_path:
                                    sg.popup('Campo Nota Fiscal obrigatório!', title='Campo Obrigatório', non_blocking=True, font=(
                                        'Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                                elif not eixo_x.isdigit():
                                    sg.popup('Campo Eixo X é obrigatório!\n\nPreencha com números inteiros.', title='Campo Obrigatório',
                                             non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                                elif not eixo_z.isdigit():
                                    sg.popup('Campo Eixo Z é obrigatório!\n\nPreencha com números inteiros.', title='Campo Obrigatório',
                                             non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                                elif not quantidade.isdigit():
                                    sg.popup('Campo Quantidade é obrigatório!\n\nPreencha com números inteiros', title='Campo Obrigatório',
                                             non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                                elif not medida:
                                    sg.popup('Campo Medida da Quantidade obrigatório!', title='Campo Obrigatório', non_blocking=True, font=(
                                        'Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                                elif not validade:
                                    sg.popup('Campo Validade obrigatório!', title='Campo Obrigatório', non_blocking=True, font=(
                                        'Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                                else:
                                    if filepath and os.path.exists(filepath):
                                        # Check if the file is a valid image file
                                        valid_image_extensions = {
                                            ".png", ".jpg", ".jpeg"}
                                        _, file_extension = os.path.splitext(
                                            filepath)
                                        if file_extension.lower() in valid_image_extensions:
                                            # Converting the image to bytes
                                            with open(filepath, 'rb') as image_file:
                                                image_data = image_file.read()

                                            # Resizing the image to 300x300 pixels
                                            pil_image = Image.open(
                                                BytesIO(image_data))
                                            pil_image = pil_image.resize((300, 300), Image.ANTIALIAS if hasattr(
                                                Image, 'ANTIALIAS') else Image.LANCZOS)

                                            # Converting the image to the format supported by PySimpleGUI
                                            tk_image = ImageTk.PhotoImage(
                                                pil_image)

                                            # Updating the image in the layout
                                            add_product_window['-IMAGE-'].update(
                                                data=tk_image)

                                            # If everything is fine, add the product
                                            adicionar_produto(nome, registro, eixo_x, nota_fiscal_pdf_path, eixo_z,
                                                              quantidade, medida, validade, filepath)

                                    else:
                                        # If no image is selected, add the product without an image
                                        adicionar_produto(nome, registro, eixo_x, nota_fiscal_pdf_path,
                                                          eixo_z, quantidade, medida, validade, None)

                            elif add_event == 'selecionar_imagem':
                                filepath = sg.popup_get_file("Selecionar Imagem", file_types=(
                                    ("Imagens", "*.png;*.jpg;*.jpeg"),))
                                add_product_window["path"].update(filepath)
                                if filepath and os.path.exists(filepath):
                                    insert_image(conn, filepath)
                                    if os.path.exists(filepath) and os.path.isfile(filepath):

                                        loading_window = loading_layout()
                                        if ultima_imagem_id:

                                            choose_window = choose_layout([])

                                            extract_nome(add_product_window,
                                                         conn, choose_window)
                                            extract_unidade_and_medida(
                                                add_product_window, conn, choose_window)

                                            loading_window.close()

                                            add_product_window["nome"].update(
                                                informacoes_extraidas["nome"])
                                            add_product_window["quantidade"].update(
                                                informacoes_extraidas['quantidade'])
                                            add_product_window["medida"].update(
                                                informacoes_extraidas['medida'])

                                        # Check if the file is a valid image file
                                        valid_image_extensions = {
                                            ".png", ".jpg", ".jpeg"}
                                        _, file_extension = os.path.splitext(
                                            filepath)
                                        if file_extension.lower() in valid_image_extensions:
                                            # Converte a imagem para bytes
                                            with open(filepath, 'rb') as image_file:
                                                image_data = image_file .read()

                                            # Redimensiona a imagem para 300x300 pixels
                                            pil_image = Image.open(
                                                BytesIO(image_data))
                                            pil_image = pil_image.resize((300, 300), Image.ANTIALIAS if hasattr(
                                                Image, 'ANTIALIAS') else Image.LANCZOS)

                                            # Converte a imagem para o formato suportado pelo PySimpleGUI
                                            tk_image = ImageTk.PhotoImage(
                                                pil_image)

                                            # Atualiza a imagem no layout
                                            add_product_window['-IMAGE-'].update(
                                                data=tk_image)
                                else:
                                    sg.popup('Imagem não selecionada ou caminho inválido!', title='Erro', non_blocking=True, font=(
                                        'Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                                    continue  # Continue para o próximo loop, não adicionando o produto

                            elif add_event == 'limpar_imagem':
                                filepath = None
                                add_product_window["path"].update(filepath)
                                add_product_window['-IMAGE-'].update(data=None)

                            elif add_event == 'selecionar_pdf':
                                selected_nota_fiscal_pdf_path = sg.popup_get_file(
                                    "Selecionar PDF", file_types=(("Arquivos PDF", "*.pdf"),))
                                add_product_window["nota_fiscal_pdf_path"].update(
                                    selected_nota_fiscal_pdf_path)

                    elif event == 'Exibir Produtos Existentes':
                        produtos = exibir_produtos_existentes()
                        if produtos:
                            main_window.hide()

                            products_table_window = sg.Window(
                                "Produtos Existentes", products_table_layout(produtos), finalize=True)

                            while True:
                                table_event, table_values = products_table_window.read()

                                if table_event == sg.WINDOW_CLOSED:
                                    main_window.un_hide()
                                    break

                                elif table_event == 'table':
                                    selected_row = table_values["table"]
                                    if selected_row:
                                        selected_product_name = produtos[selected_row[0]][0]
                                        product_info = get_product_info(
                                            selected_product_name)

                                        # Ensure that product_info is not None before using it
                                        if product_info:
                                            products_info_loop()

                        else:
                            sg.popup('Nenhum produto cadastrado.', title='Produtos Não Encontrados',
                                     non_blocking=True, font=('Helvetica', 10), keep_on_top=True)

                    elif event == 'Calibrar':
                        try:
                            calibrar = f"CALIBRAR" + '\n'
                            ser.write(calibrar.encode())
                        except Exception as e:
                            sg.popup_error('Nenhuma porta serial conectada.\n\n Impossível fazer a comunicação.', title='Produtos Não Encontrados',
                                           non_blocking=True, font=('Helvetica', 10), keep_on_top=True)
                            print("Erro em Calibrar: " + str(e))

                    elif event == 'Localizar Produto':
                        filtro_nome = values["filtro_nome"]
                        if filtro_nome:
                            produtos = localizar_produto(filtro_nome)
                            if produtos:
                                if len(produtos) == 1:
                                    selected_product_name = produtos[0][0]
                                    product_info = get_product_info(
                                        selected_product_name)

                                    # Ensure that product_info is not None before using it
                                    if product_info:
                                        products_info_loop()

                                    products_table_window = sg.Window("Produtos Existentes", products_table_layout(produtos), finalize=True)
                                    
                                    while True:
                                        table_event, table_values = products_table_window.read()

                                        if table_event == sg.WINDOW_CLOSED:
                                            main_window.un_hide()
                                            break

                                        elif table_event == 'table':
                                            selected_row = table_values["table"]
                                            if selected_row:
                                                selected_product_name = produtos[selected_row[0]][0]
                                                product_info = get_product_info(
                                                    selected_product_name)

                                                # Ensure that product_info is not None before using it
                                                if product_info:
                                                    products_info_loop()

                                else:
                                    products_table_window = sg.Window(
                                        "Listagem de Produtos", products_table_layout(produtos), finalize=True)

                            else:
                                sg.popup('Nenhum produto encontrado para o filtro fornecido.', title='Produtos não encontrados',
                                         non_blocking=True, font=('Helvetica', 10), keep_on_top=True)
                        else:
                            sg.popup('Escreva algo para buscar.', title='Produtos Não Encontrados',
                                     non_blocking=True, font=('Helvetica', 10), keep_on_top=True)

                if main_window:
                    main_window.close()

                if conn:
                    conn.close()

                try:
                    ser.close()
                except Exception as e:
                    print("Erro ao fechar a porta serial: " + str(e))

        except Exception as e:
            print("Erro ao configurar a porta serial: " + str(e))
            sg.popup_error("Valores inválidos, tente novamente")
    else:
        sg.popup("Valores inválidos, tente novamente")