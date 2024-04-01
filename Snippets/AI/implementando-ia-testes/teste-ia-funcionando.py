import PySimpleGUI as sg
import sqlite3
import datetime
from PIL import Image, ImageTk
from io import BytesIO
import os
import shutil
import uuid
import sys
import serial
import threading
import time
import serial.tools.list_ports
import fitz
import webbrowser
import urllib.parse
import urllib.request
import io
import re
import cv2
import easyocr
import pytesseract
from easyocr import Reader
import pyocr
import pyocr.builders

#######

# Configurando o caminho para o executável do Tesseract-OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Lista de palavras-chave para identificar o nome do medicamento
palavras_chave = [
    'abacavir', 'abiraterona', 'acetaminofeno', 'acetato de tocoferol', 'acetato de zinco', 'aciclovir', 'ácido ascórbico', 'ácido azelaico', 'ácido fólico', 'ácido fusídico', 'ácido glicólico',
    'ácido pantotênico', 'ácido salicílico', 'ácido zoledrônico', 'acitretina', 'adapaleno', 'adrenalina', 'água', 'álcool', 'alendronato', 'alfacalcidol', 'alfentanila', 'alprazolam', 'amiodarona',
    'amitriptilina', 'amlodipina', 'amoxicilina', 'anastrozol', 'andrógeno', 'aripiprazol', 'asenapina', 'aspirina', 'atazanavir', 'atenolol', 'atomoxetina', 'atorvastatina', 'azitromicina', 'bacitracina',
    'baclofeno', 'benazepril', 'benzatropina', 'benzidamina', 'benzocaína', 'betacaroteno', 'betahistina', 'betametasona', 'bezafibrato', 'bicalutamida', 'bicarbonato de potássio', 'bimatoprosta', 'biotina',
    'biperideno', 'bisoprolol', 'boldenona', 'borato de alumínio', 'borato de sódio', 'borato', 'bromazepam', 'brometo de ipratrópio', 'bromidrato de fenoterol', 'bromocriptina', 'bromoprida', 'budesonida',
    'bumetanida', 'bupivacaína', 'bupropiona', 'buspirona', 'butenafina', 'cabergolina', 'calcitonina', 'calcitriol', 'canagliflozina', 'candesartana', 'captopril', 'carbamazepina', 'carbonato de cálcio',
    'carbonato de ferro', 'carbonato de magnésio', 'carbonato', 'carisoprodol', 'carvedilol', 'cefalexina', 'ceftriaxona', 'celecoxibe', 'cetoconazol', 'cetoprofeno', 'cianocobalamina', 'ciclobenzaprina',
    'ciclopirox', 'ciclosporina', 'cinarizina', 'ciprofloxacino', 'ciproterona', 'citalopram', 'citrato de cálcio', 'citrato', 'claritromicina', 'clomifeno', 'clomipramina', 'clonazepam', 'clonidina',
    'clopidogrel', 'cloprostenol', 'clorazepato', 'cloreto de cetilpiridínio', 'cloreto de cromo', 'cloreto de flúor', 'cloreto de potássio', 'cloreto de sódio', 'cloridrato de benzidamina',
    'cloridrato de fenilefrina', 'cloridrato de fexofenadina', 'cloridrato de piridoxina', 'cloridrato de pseudoefedrina', 'clormadinona', 'clorpromazina', 'clortalidona',
    'clotrimazol', 'clozapina', 'codeína', 'colecalciferol', 'colesevelam', 'colutório', 'dapagliflozina', 'darunavir', 'denosumabe', 'desipramina', 'desloratadina', 'desogestrel', 'desvenlafaxina',
    'dexametasona', 'dexmedetomidina', 'dexpantenol', 'dextroanfetamina', 'diazepam', 'dibucaina', 'diclofenaco', 'dicloridrato de cetirizina', 'difenidramina', 'digoxina', 'diltiazem', 'dimenidrinato',
    'dipirona', 'dipirona monoidratada', 'dobutamina', 'domperidona', 'donepezila', 'dopamina', 'doramectina', 'dorflex', 'dostinex', 'doxazosina', 'doxiciclina', 'doxorrubicina', 'dronedarona', 'droperidol', 'drospirenona', 'dulaglutida',
    'duloxetina', 'dutasterida', 'efavirenz', 'empagliflozina', 'enalapril', 'entecavir', 'enzalutamida', 'ergotamina', 'eritromicina', 'escitalopram', 'escopolamina', 'esomeprazol', 'espironolactona',
    'estanozolol', 'estradiol', 'estrogênio', 'estrógeno', 'etilestradiol', 'etinilestradiol', 'etoricoxibe', 'etravirina', 'exemestano', 'exenatida', 'ezetimiba', 'felodipina', 'fenilefrina', 'fenitoína',
    'fenobarbital', 'fenofibrato', 'fentanila', 'fexofenadina', 'fibrato', 'finasterida', 'flecainida', 'fluconazol', 'fludrocortisona', 'flunarizina', 'flunitrazepam', 'fluoreto de estanho', 'fluoreto de sódio',
    'fluoxetina', 'flutamida', 'fluticasona', 'fluvastatina', 'follitropina', 'fosfato de clindamicina', 'fosfato de neomicina', 'fosfato de potássio', 'fosfato', 'fosinopril', 'fulvestranto', 'fumarato ferroso',
    'furosemida', 'gabapentina', 'galantamina', 'gemfibrozil', 'gentamicina', 'gestodeno', 'glibenclamida', 'glicerina', 'glimepirida', 'gluconato de ferro', 'gluconato ferroso', 'gluconato',
    'gonadotrofina coriônica', 'goserrelina', 'granisetrona', 'haloperidol', 'hidralazina', 'hidroclorotiazida', 'hidrocortisona', 'hidrogenocarbonato', 'hidroquinona', 'hidróxido de sódio',
    'hormônio do crescimento', 'ibandronato', 'ibuprofeno', 'imipramina', 'imiquimode', 'indapamida', 'insulina aspart', 'insulina degludeca', 'insulina detemir', 'insulina glargina', 'insulina glulisina',
    'insulina Lente', 'insulina lispro', 'insulina NPH', 'insulina regular', 'insulina Ultra Lente', 'insulina', 'iodeto de ferro', 'iodeto de potássio', 'iodeto de sódio', 'irbesartana', 'isoproterenol',
    'isotretinoína', 'itraconazol', 'ivermectina', 'labetalol', 'lactato', 'lamivudina', 'lamotrigina', 'lansoprazol', 'latanoprosta', 'leflunomida', 'lercanidipina', 'letrozol',
    'leuprorrelina', 'levetiracetam', 'levofloxacino', 'levoitiroxina', 'levomepromazina', 'levonorgestrel', 'levotiroxina', 'lidocaína', 'linagliptina', 'linestrenol', 'liraglutida', 'lisdexanfetamina',
    'lisinopril', 'lopinavir', 'loratadina', 'lorazepam', 'losartana', 'loção', 'lurasidona', 'maleato de dimetindeno', 'maleato', 'mazindol', 'meclizina', 'medroxiprogesterona', 'melanina', 'melatonina',
    'meloxicam', 'memantina', 'menotropina', 'meperidina', 'mesalazina', 'mesilato', 'metformina', 'metilfenidato', 'metilprednisolona', 'metiltestosterona', 'metoclopramida', 'metoprolol', 'metoxamina',
    'metronidazol', 'miconazol', 'midazolam', 'miglitol', 'milnaciprano', 'milrinona', 'minoxidil', 'mirtazapina', 'modafinila', 'montelucaste', 'morfina', 'multivitamínico', 'mupirocina', 'nandrolona',
    'naproxeno', 'naratriptana', 'nateglinida', 'nebivolol', 'neossulfamida', 'nesiritida', 'nicotinamida', 'nifedipina', 'nimesulida', 'nitazoxanida', 'nitrendipina', 'nitroglicerina', 'nitroprussiato',
    'nomegestrol', 'noradrenalina', 'norelgestromina', 'noretisterona', 'nortriptilina', 'olanzapina', 'óleo', 'olmesartana', 'omeprazol', 'ondansetrona', 'orlistat', 'orotato', 'oxandrolona', 'oxazepam',
    'oxcarbazepina', 'oxicodona', 'óxido de cromo', 'óxido de ferro', 'óxido de manganês', 'óxido de zinco', 'oximetazolina', 'paliperidona', 'pantenol', 'pantoprazol', 'paracetamol', 'parlodel', 'paroxetina',
    'perfenazina', 'perindopril', 'peróxido de benzoíla', 'petidina', 'pioglitazona', 'piridoxina', 'piroxicam', 'pitavastatina', 'polidocanol', 'polietilenoglicol', 'polivitamínico', 'pravastatina',
    'prazosina', 'prednisona', 'pregabalina', 'prilocaína', 'primidona', 'primobolan', 'procaína', 'progestágeno', 'progesterona', 'prometazina', 'propafenona', 'propilenoglicol', 'propionato', 'propofol',
    'propranolol', 'quetamina', 'quetiapina', 'raloxifeno', 'raltegravir', 'ramelteon', 'ramipril', 'ranitidina', 'remifentanila', 'repaglinida', 'riboflavina', 'risedronato', 'risperidona', 'ritonavir',
    'rituximabe', 'rivastigmina', 'rizatriptana', 'ropivacaína', 'rosiglitazona', 'rosuvastatina', 'salbutamol', 'salmeterol', 'saxagliptina', 'selegilina', 'semaglutida', 'sertralina', 'sibutramina',
    'sinvastatina', 'sitagliptina', 'solução', 'sorbitol', 'sotalol', 'spironolactona', 'stavudina', 'sufentanila', 'sulfadiazina de prata', 'sulfametoxazol', 'sulfato de cobre', 'sulfato de ferro',
    'sulfato de magnésio', 'sulfato de manganês', 'sulfato de polimixina B', 'sulfato de salbutamol', 'sulfato de zinco', 'sulfato ferroso', 'sulfato', 'sulfeto de selênio', 'sulpirida', 'sumatriptana',
    'tacrolimo', 'tadalafila', 'tamoxifeno', 'tamsulosina', 'telmisartana', 'temazepam', 'tenofovir', 'teofilina', 'terazosina', 'terbinafina', 'terbutalina', 'teriparatida', 'testosterona em gel',
    'testosterona injetável', 'testosterona', 'tetracaína', 'tetraciclina', 'tiamina', 'tibolona', 'tioconazol', 'tiotrópio', 'tizanidina', 'tocoferol', 'tolbutamida', 'tolcapona', 'tolterodina',
    'topiramato', 'tramadol', 'trazodona', 'trembolona', 'tretinoína', 'trieste', 'trifluoperazina', 'trihexifenidilo', 'trimetoprima', 'triptorrelina', 'tris', 'trometamol', 'unguento', 'valaciclovir',
    'valerato', 'valproato', 'valsartana', 'venlafaxina', 'verapami', 'verapamil', 'vitamina B1', 'vitamina B12', 'vitamina B2', 'vitamina B3', 'vitamina B6', 'vitamina C', 'vitamina D', 'vitamina D3',
    'vitamina E', 'voriconazol', 'warfarina', 'zalcitabina', 'zaleplon', 'zidovudina', 'ziprasidona', 'zoledronato', 'zolmitriptana', 'zolpidem', 'zopiclona'
]

informacoes_extraidas = {'nome': None, 'quantidade': None, 'medida': None}

# Lista de unidades de medida permitidas
palavras_medida = ["g", "mg", "mmg", "mcg", "L", "ml", "mml", "u"]

#######

sg.theme('lightblue7')
# sg.set_options(font=('Courier New', 20))


# Lock para garantir acesso seguro às variáveis globais
data_lock = threading.Lock()


# ...
path = None
nome = None
registro = None
eixo_x = None
nota_fiscal_pdf_path = None
eixo_z = None
quantidade = None
validade = None
medida = None
selected_image_path = None
has_selected_image = False
Temperatura = None
Umidade = None
main_window = None
ultima_imagem_id = None
# ...

# Funções globais
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
    cursor.execute('SELECT nome, nota_fiscal_pdf_path, registro, quantidade, medida, eixo_x, eixo_z, path, validade FROM produtos WHERE nome = ?', (product_name,))
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
        [sg.Table(values=data, headings=header, auto_size_columns=False, justification='left',
                  display_row_numbers=False, hide_vertical_scroll=True, num_rows=min(25, len(data)),
                  col_widths=[20, 20, 20], key="table", enable_events=True)]
    ]

# Função para loop de informações do produto
def products_info_loop():
    nome, nota_fiscal_pdf_path, registro, quantidade, medida, eixo_x, eixo_z, path_imagem, validade = product_info
    main_window.hide()

    info_product_window = sg.Window("Informações do Produto", info_product_layout(
        has_selected_image=(path_imagem is not None), path_imagem=path_imagem), finalize=True)

    # Atualiza os elementos de texto na janela de informações do produto
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

        elif info_event == 'Voltar':
            info_product_window.close()
            products_table_window.un_hide()

        elif info_event == 'Guardar Produto':
            guardar = f'X{eixo_x}Z{eixo_z}GUARDAR' + '\n'
            ser.write(guardar.encode())
            sg.popup(f"O produto foi guardado.", title='Produto guardado',
                     non_blocking=True, font=('Helvetica', 10), keep_on_top=True)
            info_product_window.close()
            products_table_window.close()
            main_window.un_hide()

        elif info_event == 'Retirar Produto':
            info_product_window.hide()

            takeOff_product_window = sg.Window(
                "Retirada do Produto", takeOff_product_layout(), finalize=True)

            while True:
                takeOff_event, takeOff_values = takeOff_product_window.read()

                if takeOff_event == sg.WINDOW_CLOSED:
                    break

                elif takeOff_event == 'Sim':
                    teste_sim = f'X{eixo_x}Z{eixo_z}RETIRAR' + '\n'
                    ser.write(teste_sim.encode())
                    sg.popup(f"O produto foi retirado.", title='Produto retirado',non_blocking=True, font=('Helvetica', 10), keep_on_top=True)
                    takeOff_product_window.close()
                    info_product_window.close()
                    products_table_window.close()
                    main_window.un_hide()

                elif takeOff_event == 'Não':
                    teste_nao = f'X{eixo_x}Z{eixo_z}RETIRARN' + '\n'
                    ser.write(teste_nao.encode())
                    sg.popup(f"O produto foi retirado.", title='Produto retirado',non_blocking=True, font=('Helvetica', 10), keep_on_top=True)
                    takeOff_product_window.close()
                    info_product_window.close()
                    products_table_window.close()
                    main_window.un_hide()

                elif info_event == "Limpar":
                    limpar = f'X{eixo_x}Z{eixo_Z}LIMPAR' + '\n'
                    ser.write(limpar.encode())

# Função para leitura e comunicação serial
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

# Função para atualizar a interface gráfica
def update_gui_window(temperatura, umidade):
    global main_window  # Adicionando global window
    main_window['-TEMPERATURA-'].update(f'Temperatura: {temperatura}°C')
    main_window['-UMIDADE-'].update(f'Umidade: {umidade * 100:.0f}%')
    main_window.Refresh()  # Atualiza a janela

# Thread para leitura serial
def serial_thread(ser):
    while True:
        time.sleep(1)
        if ser:
            enter = f'\n'
            ser.write(enter.encode())
            read_serial(ser)

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

    window_size = (1000, 850)
    layout = [
        [sg.Text(f'Página 1 de {num_pages}', key='-PAGE_COUNTER-')],
        [sg.Button('Anterior'), sg.Button('Próxima'), sg.Button(
            'Abrir no Navegador'), sg.Button('Fechar')],
        [sg.Image(key='-IMAGE-')]
    ]

    window = sg.Window('Visualizar PDF', layout,finalize=True, size=window_size)
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


#######


def mostrar_loading():
    posicao_x = 800  
    posicao_y = 300  
    
    loading_layout = [
        [sg.Text("Estou analisando a imagem fornecida\n\nEsse processo pode demorar um pouco...", justification='center')]
    ]
    loading_window = sg.Window("Loading", loading_layout, finalize=True, size=(300, 100), location=(posicao_x, posicao_y), keep_on_top=True)
    return loading_window

# Função apra criar a janela de escolha
def criar_janela_escolha(nomes_medicamentos):
    escolha_layout = [
        [sg.Text("Escolha o medicamento:")],
        [sg.Listbox(values=nomes_medicamentos, size=(30, len(nomes_medicamentos)), key="-MEDICAMENTO-")],
        [sg.Button("OK")]
    ]
    escolha_window = sg.Window("Escolha o Medicamento", escolha_layout, finalize=False)
    return escolha_window

# Função para criar a janela principal
def criar_janela_principal():
    layout_principal = [
        [sg.Button("Image Upload", key='-UPLOAD-'), sg.Button("Visualizar Imagem", key='-VISUALIZAR-', disabled=True), sg.Button("Extrair Texto", key='-EXTRAIR-', disabled=True)]
    ]
    window_principal = sg.Window("Principal", layout_principal, finalize=True)
    return window_principal

def inserir_imagem(conn, path_imagem):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO imagens (path) VALUES (?)', (path_imagem,))
    conn.commit()
    global ultima_imagem_id
    ultima_imagem_id = cursor.lastrowid  # Obtém o ID da última imagem inserida

# Função para inserir o produto no banco de dados
def inserir_produto(conn, nome_produto, quantidade, medida, imagem_id):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO produtos (nome_produto, quantidade, medida, imagem_id) VALUES (?, ?, ?, ?)',
                   (nome_produto, quantidade, medida, imagem_id))
    conn.commit()

# Função para obter o path da imagem do banco de dados
def obter_imagem(conn, imagem_id):
    cursor = conn.cursor()
    cursor.execute('SELECT path FROM imagens WHERE id = ?', (imagem_id,))
    path = cursor.fetchone()
    return path[0] if path else None

# Função para carregar a imagem e exibi-la na janela
def exibir_imagem(window_imagem, conn, imagem_id):
    path = obter_imagem(conn, imagem_id)
    if path:
        image = Image.open(path)
        image.thumbnail((400, 400))
        bio = io.BytesIO()
        image.save(bio, format="PNG")
        img_bytes = bio.getvalue()
        window_imagem['-IMAGE-'].update(data=img_bytes)

# Função para realizar OCR com easyocr
def ocr_with_easyocr(image):
    reader = easyocr.Reader(['pt'])
    results = reader.readtext(image)
    extracted_text = [result[1] for result in results]
    return " ".join(extracted_text)

# Função para extrair o nome da imagem
def extrair_nome_imagem(add_product_window, conn, escolha_window, tentativa=1):
    global ultima_imagem_id
    path = obter_imagem(conn, ultima_imagem_id)
    if path:
        if tentativa == 1:
            image = cv2.imread(path)
            texto = ocr_with_easyocr(image)
        elif tentativa == 2:
            image = Image.open(path)
            texto = pytesseract.image_to_string(image)
        else:
            tools = pyocr.get_available_tools()
            if len(tools) == 0:
                sg.popup_error(
                    "Nenhum motor OCR disponível. Certifique-se de ter o Tesseract-OCR instalado.")
                return None

            tool = tools[0]
            with Image.open(path) as img:
                texto = tool.image_to_string(
                    img, builder=pyocr.builders.TextBuilder())

        nomes_medicamentos = encontrar_nome_medicamento(texto)

        if len(nomes_medicamentos) > 1:
            escolha_window = criar_janela_escolha(nomes_medicamentos)

            while True:
                event_escolha, values_escolha = escolha_window.read()

                if event_escolha == sg.WIN_CLOSED or event_escolha == "OK":
                    break

            escolha_window.close()

            if values_escolha["-MEDICAMENTO-"]:
                nome_medicamento = values_escolha["-MEDICAMENTO-"][0]
            else:
                sg.popup_error("Selecione um medicamento.")
                return

        elif len(nomes_medicamentos) == 1:
            nome_medicamento = nomes_medicamentos[0]

        else:
            sg.popup_error("Nenhum medicamento encontrado.")
            return

        add_product_window['-NOME-'].update(
            nome_medicamento if nome_medicamento else "")

    else:
        sg.popup("Nome do medicamento não encontrado.",
                 "Informação não encontrada.")
        return None

# Função para extrair a unidade e medida da imagem
def extrair_unidade_e_medida_imagem(add_product_window, conn, escolha_window, tentativa=1):
    global ultima_imagem_id
    path = obter_imagem(conn, ultima_imagem_id)
    if path:
        if tentativa == 1:
            image = cv2.imread(path)
            texto = ocr_with_easyocr(image)
        elif tentativa == 2:
            image = Image.open(path)
            texto = pytesseract.image_to_string(image)
        else:
            tools = pyocr.get_available_tools()
            if len(tools) == 0:
                sg.popup_error(
                    "Nenhum motor OCR disponível. Certifique-se de ter o Tesseract-OCR instalado.")
                return None

            tool = tools[0]
            with Image.open(path) as img:
                texto = tool.image_to_string(
                    img, builder=pyocr.builders.TextBuilder())

        # Calling the function to extract quantidade and medida
        quantidade, medida = encontrar_quantidade_e_medida(texto)

        if quantidade == "Quantidade não encontrada." or medida == "Medida não encontrada.":
            # Faça a mesma função rodar novamente para pegar os dados corretos, mas agora com a segunda tentativa
            return extrair_unidade_e_medida_imagem(add_product_window, conn, escolha_window, tentativa=2)
        else:
            add_product_window['-QUANTIDADE-'].update(
                quantidade if quantidade else "")
            add_product_window['-MEDIDA-'].update(medida if medida else "")
    else:
        sg.popup("Nome do medicamento não encontrado.",
                 "Informação não encontrada.")
        return None

# Função para reconhecer o nome do medicamento
def encontrar_nome_medicamento(texto):
    resultados = []

    for palavra_chave in palavras_chave:
        palavras = re.split(r'[\s\n]+', palavra_chave.lower())
        encontradas = all(p.lower() in texto.lower() for p in palavras)
        if encontradas:
            resultados.append(palavra_chave.capitalize())

    return resultados if resultados else ["Medicamento não encontrado."]

# Função para reconhecer a quantidade e medida e após isso separá-las
def encontrar_quantidade_e_medida(texto):
    # Expressão regular para encontrar a quantidade e medida
    padrao = r"(\d+\s*(" + "|".join(palavras_medida) + r")\b)"
    resultado = re.findall(padrao, texto, flags=re.IGNORECASE)
    if resultado:
        # Extrair a primeira ocorrência de quantidade e medida
        quantidade_medida = resultado[0][0]
        # Dividir a quantidade da medida
        partes = re.split(r"\s*(" + "|".join(palavras_medida) +
                          r")\b", quantidade_medida, flags=re.IGNORECASE)
        quantidade = partes[0].strip() if len(
            partes) > 0 else "Quantidade não encontrada"
        medida = partes[1].strip().lower() if len(
            partes) > 1 else "Medida não encontrada"
        return quantidade, medida
    else:
        return "Quantidade não encontrada.", "Medida não encontrada."


########

# Interface gráfica com PySimpleGUI

# Janela de configurações
def config_layout():
    return [
        [sg.Text("Porta COM:"), sg.InputText(key="porta_COM")],
        [sg.Text("Taxa Band:"), sg.Combo(['300', '1200', '2400', '4800', '9600', '19200', '38400', '57600', '74880',
                                          '115200', '230400', '250000', '500000'], tooltip="choose something", key="taxa_band", size=(10, 1))],
        [sg.Button("OK")]
    ]

#Janela principal
def main_layout():
    return [
        [sg.Button("Adicionar Produto"), sg.Button("Exibir Produtos Existentes")], [sg.Button('Calibrar')],
        [sg.HSeparator("Separador")],
        [sg.Text("Localizar por Nome:"), sg.InputText(key="filtro_nome"), sg.Button("Localizar Produto")],
        [sg.HSeparator("Separador")],
        [sg.Text('', size=(20, 1), key='-TEMPERATURA-')],
        [sg.Text('', size=(20, 1), key='-UMIDADE-')],
        [sg.Button('Voltar')]
    ]

# Janlea de adição de produtos
def add_product_layout():
    return [
        [sg.Button("Teste")],
        [sg.Text("Nome:"), sg.InputText(key='-NOME-', size=(40, 1), pad=(54, None))],
        [sg.Text("Registro:"), sg.InputText(key="registro", size=(40, 1), pad=(40, None))],
        [sg.Text("Eixo X:"), sg.InputText(key="eixo_x", size=(40, 1), pad=(53, None))],
        [sg.Text("Eixo Z:"), sg.InputText(key="eixo_z", size=(40, 1), pad=(53, None))],
        [sg.Text("Validade:"), sg.InputText(key="validade", size=(40, 1), pad=(53, None))],
        [sg.Text("Quantidade:"), sg.InputText(key='-QUANTIDADE-', size=(20, 1), pad=(25, None)),
        sg.Combo(['unid', 'mmg', 'mg', 'g', 'ml'], tooltip="choose something", key='-MEDIDA-', size=(7, 1))],
        [sg.Button("Selecionar Imagem", key="selecionar_imagem"),
         sg.Button("Limpar Imagem", key="limpar_imagem")],
        [sg.Image(key='-IMAGE-', size=(300, 300), pad=(0, 0),)],
        [sg.Text("Nota Fiscal:"), sg.Input(key="-NOTA_FISCAL_PDF-"),
         sg.FileBrowse(key="-BROWSE_PDF-", file_types=(("PDF Files", "*.pdf"),))],
        [sg.Button("Adicionar")],
        [sg.Button('Voltar')],
        [sg.Text("", visible=False, key="path")],
    ]

# Janela de informações do produto
def info_product_layout(has_selected_image=False, path_imagem=None):
    layout = [
        [sg.Text("Nome:"), sg.Text(nome, key="nome",size=(40, 1), pad=(54, None))],
        [sg.Text("Registro:"), sg.Text(registro, key="registro", size=(40, 1), pad=(40, None))],
        [sg.Text("Validade:"), sg.Text(validade, key="validade", size=(40, 1))],
        [sg.Text("Quantidade:"), sg.Text(quantidade, key="quantidade", size=(20, 1), pad=(25, None))],
        [sg.Text("Medida da Quantidade: "), sg.Text(medida, key="medida")],
        [sg.Text("Eixo X:"), sg.Text(eixo_x, key="eixo_x", size=(40, 1), pad=(53, None))],
        [sg.Text("Eixo Z:"), sg.Text(eixo_z, key="eixo_z", size=(40, 1), pad=(53, None))],
        [sg.Image(key='-PRODUCT_IMAGE-', size=(300, 300), pad=(0, 0), expand_y=False, expand_x=False, visible=False)],
        [sg.Button("Guardar Produto"), sg.Button("Retirar Produto")], [sg.Button("Limpar")],
        [sg.Button("Visualizar a Nota Fiscal")],
        [sg.Button('Voltar')]
    ]

    if has_selected_image:
        layout[-2].insert(0, sg.Image(key='-PRODUCT_IMAGE-', visible=True))

    return layout

# Janela de limpeza do produto na hora da retirada
def takeOff_product_layout():
    return [
        [sg.Text("Deseja realizar limpeza?")],
        [sg.Button("Sim"), sg.Button("Não")]
    ]

####

# JANELA DE CONFIGURAÇÕES
config_window = sg.Window("Configurações", config_layout(), finalize=True)

# Loop para a janela de configurações
while True:
    event, values = config_window.read()

    if event == sg.WINDOW_CLOSED:
        break
    elif event == 'OK':
        ser = connect_to_arduino(values["porta_COM"], values["taxa_band"])
        if ser:
            break

config_window.close()

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

# JANELA PRINCIPAL
main_window = sg.Window("Janela Principal", main_layout())

# Inicia a thread para leitura serial
serial_thread_instance = threading.Thread(target=serial_thread, args=(ser,), daemon=True)
serial_thread_instance.start()

# Loop principal do programa
while True:
    event, values = main_window.read()

    if event == sg.WINDOW_CLOSED:
        break

    elif event == 'Voltar':
        main_window.close()
        clear_serial_input(ser)
        ser.close()  # Fecha a conexão serial
        # Reabre a janela de configurações
        config_window = sg.Window("Configurações", config_layout(), finalize=True)

        # Chama a função para redefinir os valores
        reset_config_values(config_window)

        while True:
            event, values = config_window.read()

            if event == sg.WINDOW_CLOSED:
                break

            elif event == 'OK':
                ser = connect_to_arduino(
                    values["porta_COM"], values["taxa_band"])
                if ser:
                    break

        config_window.close()

        # Reabre a janela principal
        main_window = sg.Window("Controle de Estoque Farmacêutico Automático", main_layout())
        serial_communication(ser)

    elif event == 'Adicionar Produto':
        main_window.hide()

        add_product_window = sg.Window("Adicione Produtos", add_product_layout())

        while True:
            add_event, add_values = add_product_window.read()

            if add_event == sg.WINDOW_CLOSED:
                break

            elif add_event == "Teste":
                window_principal = criar_janela_principal()

                while True:

                    event, values = window_principal.read()

                    if event == sg.WIN_CLOSED:
                        break

                    # Evento de fazer upload da imagem
                    elif event == '-UPLOAD-':
                        filepath = sg.popup_get_file("Selecione uma imagem")
                        if filepath:
                            inserir_imagem(conn, filepath)
                            window_principal['-VISUALIZAR-'].update(disabled=False)
                            window_principal['-EXTRAIR-'].update(disabled=False)

                    # Evento de visualizar a imagem posteiormente selecionada
                    elif event == '-VISUALIZAR-':
                        imagem_id = ultima_imagem_id
                        if imagem_id:
                            window_imagem = sg.Window("Visualizar Imagem", [
                                                    [sg.Image(key='-IMAGE-')]], finalize=True)
                            exibir_imagem(window_imagem, conn, imagem_id)
                            event_imagem, values_imagem = window_imagem.read()
                            window_imagem.close()

                    # Evento principal para extrair informações da imagem
                    elif event == '-EXTRAIR-':
                        window_principal.hide()
                        loading_window = mostrar_loading()

                        if ultima_imagem_id:

                            escolha_window = criar_janela_escolha([])
                            
                            # Abrir a segunda janela de adicionar produto com as informações extraídas
                            # window_adicionar = criar_janela_adicionar()

                            extrair_nome_imagem(add_product_window, conn, escolha_window)
                            extrair_unidade_e_medida_imagem(add_product_window, conn, escolha_window)

                            loading_window.close()

                            # Loop da segunda janela de adicionar produto
                            while True:

                                event_adicionar, add_values = add_product_window.read()

                                if event_adicionar == sg.WIN_CLOSED:
                                    break

                                # Evento para adicionar produto ao banco de dados
                                elif event_adicionar == 'Adicionar':
                                    if add_values['-NOME-'] and add_values['-QUANTIDADE-'] and add_values['-MEDIDA-']:
                                        inserir_produto(conn, add_values['-NOME-'], add_values['-QUANTIDADE-'], add_values['-MEDIDA-'], ultima_imagem_id)
                                        sg.popup("Produto adicionado com sucesso!")

                                        # Exibir as informações extraídas na janela de adição
                                        add_product_window['-NOME-'].update(informacoes_extraidas['nome'])
                                        add_product_window['-QUANTIDADE-'].update(informacoes_extraidas['quantidade'])
                                        add_product_window['-MEDIDA-'].update(informacoes_extraidas['medida'])

                                        window_principal.un_hide()
                                        add_product_window.close()

                                        break
                                    else:
                                        sg.popup_error("Por favor, preencha todas as informações do medicamento.")

                # Fechando as janelas ao sair dos loops
                window_principal.close()

            elif add_event == 'Adicionar':
                nome = add_values.get("nome")
                registro = add_values.get("registro")
                eixo_x = add_values.get("eixo_x")
                nota_fiscal_pdf_path = add_values.get("-NOTA_FISCAL_PDF-")
                eixo_z = add_values.get("eixo_z")
                quantidade = add_values.get("quantidade")
                medida = add_values.get("medida")
                validade = add_values.get("validade")

                if not nome:
                    sg.popup('Campo Nome obrigatório!', title='Campo Obrigatório', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                elif not registro:
                    sg.popup('Campo Registro obrigatório!', title='Campo Obrigatório', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                elif not nota_fiscal_pdf_path:
                    sg.popup('Campo Nota Fiscal obrigatório!', title='Campo Obrigatório', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                elif not eixo_x.isdigit():
                    sg.popup('Campo Eixo X é obrigatório!\n\nPreencha com números inteiros.', title='Campo Obrigatório',non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                elif not eixo_z.isdigit():
                    sg.popup('Campo Eixo Z é obrigatório!\n\nPreencha com números inteiros.', title='Campo Obrigatório',non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                elif not quantidade.isdigit():
                    sg.popup('Campo Quantidade é obrigatório!\n\nPreencha com números inteiros', title='Campo Obrigatório',non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                elif not medida:
                    sg.popup('Campo Medida da Quantidade obrigatório!', title='Campo Obrigatório', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                elif not validade:
                    sg.popup('Campo Validade obrigatório!', title='Campo Obrigatório', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                else:
                    if selected_image_path and os.path.exists(selected_image_path):
                        # Check if the file is a valid image file
                        valid_image_extensions = {".png", ".jpg", ".jpeg"}
                        _, file_extension = os.path.splitext(
                            selected_image_path)
                        if file_extension.lower() in valid_image_extensions:
                            # Converting the image to bytes
                            with open(selected_image_path, 'rb') as image_file:
                                image_data = image_file.read()

                            # Resizing the image to 300x300 pixels
                            pil_image = Image.open(BytesIO(image_data))
                            pil_image = pil_image.resize((300, 300), Image.ANTIALIAS if hasattr(
                                Image, 'ANTIALIAS') else Image.LANCZOS)

                            # Converting the image to the format supported by PySimpleGUI
                            tk_image = ImageTk.PhotoImage(pil_image)

                            # Updating the image in the layout
                            add_product_window['-IMAGE-'].update(data=tk_image)

                            # If everything is fine, add the product
                            adicionar_produto(nome, registro, eixo_x, nota_fiscal_pdf_path, eixo_z,
                                              quantidade, medida, validade, selected_image_path)

                    else:
                        # If no image is selected, add the product without an image
                        adicionar_produto(nome, registro, eixo_x, nota_fiscal_pdf_path,
                                          eixo_z, quantidade, medida, validade, None)

            elif add_event == 'selecionar_imagem':
                selected_image_path = sg.popup_get_file(
                    "Selecionar Imagem", file_types=(("Imagens", "*.png;*.jpg;*.jpeg"),))
                add_product_window["path"].update(selected_image_path)
                if selected_image_path and os.path.exists(selected_image_path):
                    if os.path.exists(selected_image_path) and os.path.isfile(selected_image_path):

                        # Check if the file is a valid image file
                        valid_image_extensions = {".png", ".jpg", ".jpeg"}
                        _, file_extension = os.path.splitext(
                            selected_image_path)
                        if file_extension.lower() in valid_image_extensions:
                            # Converte a imagem para bytes
                            with open(selected_image_path, 'rb') as image_file:
                                image_data = image_file .read()

                            # Redimensiona a imagem para 300x300 pixels
                            pil_image = Image.open(BytesIO(image_data))
                            pil_image = pil_image.resize((300, 300), Image.ANTIALIAS if hasattr(Image, 'ANTIALIAS') else Image.LANCZOS)

                            # Converte a imagem para o formato suportado pelo PySimpleGUI
                            tk_image = ImageTk.PhotoImage(pil_image)

                            # Atualiza a imagem no layout
                            add_product_window['-IMAGE-'].update(data=tk_image)
                else:
                    sg.popup('Imagem não selecionada ou caminho inválido!', title='Erro', non_blocking=True, font=(
                        'Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                    continue  # Continue para o próximo loop, não adicionando o produto

            elif add_event == 'limpar_imagem':
                selected_image_path = None
                add_product_window["path"].update(selected_image_path)
                add_product_window['-IMAGE-'].update(data=None)

            elif add_event == 'selecionar_pdf':
                selected_nota_fiscal_pdf_path = sg.popup_get_file(
                    "Selecionar PDF", file_types=(("Arquivos PDF", "*.pdf"),))
                add_product_window["nota_fiscal_pdf_path"].update(
                    selected_nota_fiscal_pdf_path)

            elif add_event == 'Voltar':
                add_product_window.close()
                main_window.un_hide()

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
                        product_info = get_product_info(selected_product_name)

                        # Ensure that product_info is not None before using it
                        if product_info:
                            products_info_loop()

        else:
            sg.popup('Nenhum produto cadastrado.', title='Produtos Não Encontrados',
                     non_blocking=True, font=('Helvetica', 10), keep_on_top=True)

    elif event == 'Calibrar':
        calibrar = f"CALIBRAR" + '\n'
        ser.write(calibrar.encode())

    elif event == 'Localizar Produto':
        filtro_nome = values["filtro_nome"]
        if filtro_nome:
            produtos = localizar_produto(filtro_nome)
            if produtos:
                if len(produtos) == 1:
                    selected_product_name = produtos[0][0]
                    product_info = get_product_info(selected_product_name)

                    # Ensure that product_info is not None before using it
                    if product_info:
                        products_info_loop()

                else:
                    products_table_window = sg.Window(
                        "Listagem de Produtos", products_table_layout(produtos), finalize=True)

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
                sg.popup('Nenhum produto encontrado para o filtro fornecido.', title='Produtos não encontrados',
                         non_blocking=True, font=('Helvetica', 10), keep_on_top=True)

if main_window:
    main_window.close()

if conn:
    conn.close()

ser.close()