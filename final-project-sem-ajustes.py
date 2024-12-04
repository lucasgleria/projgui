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
import io

####### LISTAS #######

# Lista de palavras-chave para identificar o nome de medicamentos


medicine_keywords = [
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

# Lista de unidades de medida permitidas
medida_keywords = ["g", "mg", "mmg", "mcg", "L", "ml", "mml", "u"]

# Lista de taxas de banda
baud_gates = ['300', '1200', '2400', '4800', '9600', '19200',
              '38400', '57600', '74880', '115200', '230400', '250000', '500000']

####### CONFIGURAÇÕES #######

# COnfigurações do PysimpleGUI
sg.theme('lightblue7')
default_font = 'Arial'
default_font_size = 12
current_font_size = default_font_size
sg.set_options(font=(default_font, current_font_size))

# Lock para garantir acesso seguro às variáveis globais pelo threading
lock_temp_umi = threading.Lock()

####### BIBLIOTECAS #######

informacoes_extraidas = {"nome": None, 'quantidade': None, 'medida': None}

####### VÁRIAVEIS #######

# Variáveis Flags
find_quantidade_and_medida_called = False
serial_thread_running = True
has_selected_image = False
serial_thread_stop_event = threading.Event()

# Variáveis setadas como None para evitar bugs
serial_thread_instance = None
nota_fiscal_pdf_path = None
ultima_imagem_id = None
nome_medicamento = None
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
velx = 0
vely = 0
velz = 0
aclx = 0
acly = 0
aclz = 0
posx = 0
posy = 0
posz = 0

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

        ser = serial.Serial(porta_COM, int(taxa_band), timeout=5)
        print("Porta serial aberta co sucesso")
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


# Função para obter portas COM disponíveis


def get_available_com_ports():
    ports = list(serial.tools.list_ports.comports())
    return [port.device for port in ports]


# Função para obter as medidas pré-selecionadas

def get_available_medida_keywords(medida_keywords):
    return medida_keywords


# Função para obter taxas de banda adequadas

def get_baud_rates():
    return baud_gates


# Função para adicionar produtos


def adicionar_produto(nome, registro, eixo_x, nota_fiscal_pdf_path, eixo_z, quantidade, medida, validade, path_imagem):
    global has_selected_image
    data_criada = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    cursor.execute('INSERT INTO produtos (nome, registro, eixo_x, nota_fiscal_pdf_path, eixo_z, quantidade, medida, path, validade, data_criada) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   (nome, registro, eixo_x, nota_fiscal_pdf_path, eixo_z, quantidade, medida, path_imagem, validade, data_criada))
    cursor.execute('INSERT INTO imagens (path) VALUES (?)', (path_imagem,))
    conn.commit()
    global ultima_imagem_id
    ultima_imagem_id = cursor.lastrowid
    has_selected_image = path_imagem is not None

# Função para exibir produtos


def exibir_produtos_existentes():
    cursor.execute('SELECT nome, registro, validade FROM produtos')
    produtos = cursor.fetchall()
    return produtos

# Função para localizar produtos


def localizar_produto(filtro):
    if filtro.isdigit():
        # Busca pelo registro
        query = 'SELECT nome, registro FROM produtos WHERE registro LIKE ?'
        params = ('%' + filtro + '%',)
    else:
        # Busca pelo nome
        query = 'SELECT nome, registro FROM produtos WHERE nome LIKE ?'
        params = ('%' + filtro + '%',)

    cursor.execute(query, params)
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
                guardar = f'R2 X{eixo_x} Z{eixo_z}' + '\n'
                try:
                    ser.write(guardar.encode())
                    time.sleep(0.1)
                    print(guardar)
                    sg.popup(f"O produto foi guardado.", title='Produto guardado',
                             non_blocking=True, font=('Helvetica', 10), keep_on_top=True)
                    info_product_window.close()
                    products_table_window.close()
                    main_window.un_hide()
                except serial.serialutil.SerialTimeoutException:
                    print(
                        "Timeout ao tentar escrever na porta serial. Tentando novamente...")
            except Exception as e:
                sg.popup_error('Nenhuma porta serial conectada.\n\n Impossível fazer a comunicação.', title='Produtos Não Encontrados',
                               non_blocking=True, font=('Helvetica', 10), keep_on_top=True)
                print("Erro em Guardar: " + str(e))

        elif info_event == 'Limpar Produto':
            try:
                limpar = f'R3 X{eixo_x} Z{eixo_z}' + '\n'

                try:
                    ser.write(limpar.encode())
                    time.sleep(0.1)
                    print(limpar)
                    sg.popup(f"O produto foi limpo.", title='Produto limpo',
                             non_blocking=True, font=('Helvetica', 10), keep_on_top=True)
                    info_product_window.close()
                    products_table_window.close()
                    main_window.un_hide()
                except serial.serialutil.SerialTimeoutException:
                    print(
                        "Timeout ao tentar escrever na porta serial. Tentando novamente...")

            except Exception as e:
                sg.popup_error('Nenhuma porta serial conectada.\n\n Impossível fazer a comunicação.', title='Produtos Não Encontrados',
                               non_blocking=True, font=('Helvetica', 10), keep_on_top=True)
                print("Erro em Limpar: " + str(e))

        elif info_event == 'Retirar Produto':
            try:
                retirar = f'R0 X{eixo_x} Z{eixo_z}' + '\n'
                try:
                    ser.write(retirar.encode())
                    time.sleep(0.1)
                    print(retirar)
                    sg.popup(f"O produto foi retirado.", title='Produto retirado',
                             non_blocking=True, font=('Helvetica', 10), keep_on_top=True)
                    info_product_window.close()
                    products_table_window.close()
                    main_window.un_hide()
                except serial.serialutil.SerialTimeoutException:
                    print(
                        "Timeout ao tentar escrever na porta serial. Tentando novamente...")
            except Exception as e:
                sg.popup_error('Nenhuma porta serial conectada.\n\n Impossível fazer a comunicação.', title='Produtos Não Encontrados',
                               non_blocking=True, font=('Helvetica', 10), keep_on_top=True)
                print("Erro em Guardar: " + str(e))

# Função para leitura e comunicação serial


# def read_serial(ser):
#     global Temperatura, Umidade

#     buffer = ''  # Buffer para armazenar dados parciais
#     start_time = time.time()  # Tempo inicial

#     while True:
#         if serial_thread_stop_event.is_set():
#             break  # Sai do loop se o evento de parada for sinalizado

#         try:
#             data = ser.readline().decode('utf-8')
#             if '\n' in data:
#                 buffer += data
#                 values = buffer.split('\n')
#                 if len(values) >= 2 and values[0] and values[1]:
#                     # Filtra valores vazios
#                     values = [str(value) for value in values if value]

#                     with lock_temp_umi:
#                         Temperatura = values[0]
#                         Umidade = float(values[1])

#                     # Atualiza a interface gráfica com os novos valores
#                     update_gui_window(Temperatura, Umidade)
#                     buffer = ''  # Limpa o buffer após processar os dados

#             # Verifica se passou 5 segundos
#             elapsed_time = time.time() - start_time
#             if elapsed_time >= 5:
#                 break

#         except Exception as e:
#             print(f"Erro na leitura serial1: {e}")
#             break
#     pass

def read_serial(ser):
    global temperatura, umidade

    buffer = ''  # Buffer para armazenar dados parciais
    start_time = time.time()  # Tempo inicial

    while True:
        if serial_thread_stop_event.is_set():
            break  # Sai do loop se o evento de parada for sinalizado

        try:
            data = ser.readline().decode('utf-8')
            buffer += data  # Adiciona ao buffer
            
            if '\n' in buffer:
                # Quando encontramos uma nova linha, processamos o buffer
                values = buffer.strip().split()
                
                # Procura por "T:" e "U:" no texto recebido
                temp_str = next((v[2:] for v in values if v.startswith("T:")), None)
                umi_str = next((v[2:] for v in values if v.startswith("U:")), None)
                
                if temp_str is not None and umi_str is not None:
                    with lock_temp_umi:
                        temperatura = temp_str
                        umidade = umi_str

                    # Atualiza a interface gráfica com os novos valores
                    update_gui_window(temperatura, umidade)
                    print(temperatura)
                    print(umidade)
                
                buffer = ''  # Limpa o buffer após processar os dados

            # Verifica se passou 5 segundos
            elapsed_time = time.time() - start_time
            if elapsed_time >= 5:
                break

        except Exception as e:
            print(f"Erro na leitura serial1: {e}")
            break

# Função para atualizar a interface gráfica


def update_gui_window(temperatura, umidade):
    global main_window  # Adicionando global window
    if main_window:
        main_window['-TEMPERATURA-'].update(f'Temperatura: {temperatura}°C')
        main_window['-UMIDADE-'].update(f'Umidade: {umidade}%')
        main_window.Refresh()  # Atualiza a janela

# Thread para leitura serial


def serial_thread(ser):
    global serial_thread_running
    while serial_thread_running:
        try:
            if serial_thread_stop_event.is_set():
                break  # Sai do loop se o evento de parada for sinalizado
            if ser and ser.is_open:
                enter = 'R1' + '\n'  # Envia o comando "R1 \n"
                try:
                    ser.write(enter.encode())
                    time.sleep(0.1)
                    read_serial(ser)
                except serial.serialutil.SerialTimeoutException:
                    print("Timeout ao tentar escrever na porta serial. Tentando novamente...")
        except Exception as e:
            print("Erro na leitura serial2:", str(e))
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


def view_selected_pdf_window(selected_nota_fiscal_pdf_path):
    pdf_document = fitz.open(selected_nota_fiscal_pdf_path)
    num_pages = pdf_document.page_count

    window_size = (500, 425)
    layout = [
        [sg.Text(
            f'Página 1 de {num_pages}', key='-PAGE_COUNTER-')],
        [sg.Button('Anterior'), sg.Button('Próxima')],
        [sg.Button('Abrir no Navegador'), sg.Button('Fechar')],
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
            webbrowser.open_new_tab(selected_nota_fiscal_pdf_path)

    pdf_document.close()
    window.close()


def view_pdf_window(nota_fiscal_pdf_path):
    pdf_document = fitz.open(nota_fiscal_pdf_path)
    num_pages = pdf_document.page_count

    window_size = (500, 425)
    layout = [
        [sg.Text(
            f'Página 1 de {num_pages}', key='-PAGE_COUNTER-')],
        [sg.Button('Anterior'), sg.Button('Próxima')],
        [sg.Button('Abrir no Navegador'), sg.Button('Fechar')],
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


def limpar_inputs(add_product_window, filepath):
    filepath = None
    add_product_window["path"].update(filepath)
    add_product_window['-IMAGE-'].update(data=None)
    add_product_window["nome"].update("")
    add_product_window["registro"].update("")
    add_product_window["eixo_x"].update("")
    add_product_window["-NOTA_FISCAL_PDF-"].update("")
    add_product_window["eixo_z"].update("")
    add_product_window["quantidade"].update("")
    add_product_window["medida"].update("")
    add_product_window["validade"].update("")
    add_product_window['-PDF_PREVIEW-'].update(data=None)
    add_product_window['text_pdf_info'].update(visible=False)

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


def extract_nome(add_product_window, conn, choose_window, attempt=1, timeout=5):
    global ultima_imagem_id
    stop_flag = [False]

    def run_extract_nome(cursor):
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

            nome = find_nome(text, medicine_keywords, timeout=5)

            if nome is not None and isinstance(nome, list) and len(nome) > 0:
                if len(nome) > 1:
                    choose_window = choose_layout(nome)

                    nome_medicamento = None

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
                    sg.popup_error("Nenhum medicamento encontrado. (01)")
                    return

                add_product_window["nome"].update(
                    nome_medicamento if nome_medicamento else "")

            else:
                print("Erro 01")
                return

        else:
            sg.popup("", "")
            return print("Erro (2)")

    def interrupcao_temporizada(tempo):
        for _ in range(tempo * 10):
            if stop_flag[0]:
                return
            for _ in range(3000000):
                pass
        stop_flag[0] = True

    thread = threading.Thread(target=interrupcao_temporizada, args=(timeout,))
    thread.start()

    while not stop_flag[0]:
        run_extract_nome(conn.cursor())
        if stop_flag[0]:
            print("Erro no extract_nome: tempo limite atingido")
            break

    thread.join()

# Função para extrair a unidade e medida da imagem


def extract_unidade_and_medida(add_product_window, conn, choose_window, attempt=1, timeout=5):
    global ultima_imagem_id
    stop_flag = [False]
    # Variável local para rastrear a execução
    find_quantidade_and_medida_called = False

    def run_extract_unidade_and_medida(cursor, find_quantidade_and_medida_called):
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
                    return print("Erro (3)")

                tool = tools[0]
                with Image.open(path) as img:
                    text = tool.image_to_string(
                        img, builder=pyocr.builders.TextBuilder())

            if not find_quantidade_and_medida_called:
                quantidade, medida = find_quantidade_and_medida(
                    text, timeout=5)
                find_quantidade_and_medida_called = True
            else:
                quantidade, medida = "", ""

            if quantidade == "" or medida == "":
                if attempt == 1:
                    return extract_unidade_and_medida(add_product_window, conn, choose_window, attempt=2)
                elif attempt == 2:
                    return extract_unidade_and_medida(add_product_window, conn, choose_window, attempt=3)
                else:
                    sg.popup(
                        "Não consegui extrair as informações desejadas. \n\n Por favor, insira as informações manualmente.")
                    return quantidade, medida
            else:
                add_product_window["quantidade"].update(
                    quantidade if quantidade else "")
                add_product_window["medida"].update(medida if medida else "")
        else:
            sg.popup("", "")
            return print("Erro (4)")

    def interrupcao_temporizada(tempo):
        for _ in range(tempo * 10):
            if stop_flag[0]:
                return
            for _ in range(2000000):
                pass
        stop_flag[0] = True

    thread = threading.Thread(target=interrupcao_temporizada, args=(timeout,))
    thread.start()

    while not stop_flag[0]:
        run_extract_unidade_and_medida(
            conn.cursor(), find_quantidade_and_medida_called)
        if stop_flag[0]:
            print("Erro no extract_unidade_and_medida: tempo limite atingido")
            break

    thread.join()

# Função para reconhecer o nome do medicamento


def find_nome(text, medicine_keywords, timeout=5):
    stop_flag = [False]

    def run_find_nome():
        resultados = []

        for palavra_chave in medicine_keywords:
            palavras = re.split(r'[\s\n]+', palavra_chave.lower())
            encontradas = all(p.lower() in text.lower() for p in palavras)
            if encontradas:
                resultados.append(palavra_chave.capitalize())

        return resultados if resultados else [""]

    def interrupcao_temporizada(tempo):
        for _ in range(tempo * 10):
            if stop_flag[0]:
                return
            for _ in range(5000000):
                pass
        stop_flag[0] = True

    thread = threading.Thread(target=interrupcao_temporizada, args=(timeout,))
    thread.start()

    resultados = []
    while not stop_flag[0]:
        resultados = run_find_nome()
        if resultados:
            stop_flag[0] = True

    thread.join()

    if stop_flag[0] and not resultados:
        print("Erro no find_nome: tempo limite atingido")
        return ["Erro no find_nome: tempo limite atingido"]

    return resultados
# Função para reconhecer a quantidade e medida e após isso separá-las


def find_quantidade_and_medida(text, timeout=5):
    stop_flag = [False]

    def run_find_quantidade_and_medida():
        # Expressão regular para encontrar a quantidade e medida
        padrao = r"(\d+\s*(" + "|".join(medida_keywords) + r")\b)"
        resultado = re.findall(padrao, text, flags=re.IGNORECASE)
        if resultado:
            # Extrair a primeira ocorrência de quantidade e medida
            quantidade_medida = resultado[0][0]
            # Dividir a quantidade da medida
            partes = re.split(r"\s*(" + "|".join(medida_keywords) +
                              r")\b", quantidade_medida, flags=re.IGNORECASE)
            quantidade = partes[0].strip() if len(partes) > 0 else ""
            medida = partes[1].strip().lower() if len(partes) > 1 else ""
            return quantidade, medida
        else:
            return "", ""

    def interrupcao_temporizada(tempo):
        for _ in range(tempo * 10):
            if stop_flag[0]:
                return
            for _ in range(2000000):
                pass
        stop_flag[0] = True

    # Cria uma thread que executará a função interrupcao_temporizada
    thread = threading.Thread(target=interrupcao_temporizada, args=(timeout,))
    thread.start()

    while not stop_flag[0]:
        quantidade, medida = run_find_quantidade_and_medida()
        if quantidade != "" and medida != "":
            break
        if stop_flag[0]:
            print("Erro no find_quantidade_and_medida: tempo limite atingido")
            return "", ""

    thread.join()
    return quantidade, medida

####### FUNÇÕES DE LAYOUT PARA INTERFCES GRÁFICAS (GUI) #######

# Janela de configurações


def config_layout():
    return [
        [sg.Combo(sg.theme_list(), default_value=sg.theme(), size=(15, 22), enable_events=True, readonly=True, key='-COR_DA_JANELA-'),
         sg.Combo(list(range(8, 25)), default_value=current_font_size, s=(5, 22), enable_events=True, readonly=True, key='-FONT-SIZE-')],
        [sg.HSep()],
        [sg.Text("Porta COM:"), sg.Combo(get_available_com_ports(), key="porta_COM", size=(10, 1)),
         sg.Text("Taxa Band:"), sg.Combo(get_baud_rates(), key="taxa_band", size=(10, 1))],
        [sg.Button("OK")]
    ]
# Janela principal


def main_layout():
    return [
        [sg.Button("Adicionar Produto"), sg.Button(
            "Exibir Produtos Existentes")], [sg.Button('Calibrar'), sg.Button("Cancelar")],
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
         sg.Combo(get_available_medida_keywords(medida_keywords), key="medida", size=(7, 1))],
        [sg.Button("Selecionar Imagem", key="selecionar_imagem"),
         sg.Button("Limpar Imagem", key="limpar_imagem"),
         sg.Button("Limpar Tudo", key="limpar_tudo")],
        [sg.Image(key='-IMAGE-', size=(0, 0), pad=(0, 0),)],
        [sg.Text("Nota Fiscal:"), sg.Input(key="-NOTA_FISCAL_PDF-"),
         sg.Button("Selecionar PDF", key="selecionar_pdf")],
        [sg.Text("Pré-visualização:"), sg.Image(key='-PDF_PREVIEW-', size=(0, 0), pad=(0, 0), enable_events=True),
         sg.StatusBar("← Selecione para melhor visualização!", text_color='black', background_color="yellow", visible=False, key="text_pdf_info")],
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
        [sg.Button("Guardar Produto"), sg.Button("Retirar Produto"),
         sg.Button("Limpar Produto")],
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
        [sg.Text("Estou analisando a imagem fornecida \n\nIsso pode demorar um pouco...",
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
            path TEXT
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
            path TEXT,
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

    elif event == '-COR_DA_JANELA-':
        if values['-COR_DA_JANELA-'] != sg.theme():
            sg.theme(values['-COR_DA_JANELA-'])
            config_window.close()
            config_window = sg.Window(
                "Configurações", config_layout(), finalize=True)

    elif event == '-FONT-SIZE-':
        current_font_size = values['-FONT-SIZE-']
        sg.set_options(font=('Arial', current_font_size))
        config_window.close()
        config_window = sg.Window(
            "Configurações", config_layout(), finalize=True)

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
                                filepath = None
                                add_product_window["path"].update(filepath)
                                add_product_window['-IMAGE-'].update(data=None)
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
                                elif not nota_fiscal_pdf_path.lower().endswith('.pdf'):
                                    sg.popup('Campo Nota Fiscal deve ser preenchido por arquivo PDF obrigatóriamente!', title='Campo Obrigatório', non_blocking=True, font=(
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
                                    if filepath:
                                        # Check if the file is a valid image file
                                        if os.path.exists(filepath):
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

                                                # If everything is fine, add the product with the image
                                                adicionar_produto(
                                                    nome, registro, eixo_x, nota_fiscal_pdf_path, eixo_z, quantidade, medida, validade, filepath)
                                                sg.popup(f"O produto {nome} foi adicionado.", title='Produto adicionado', non_blocking=True, font=(
                                                    'Helvetica', 10), keep_on_top=True)
                                                limpar_inputs(
                                                    add_product_window, filepath)
                                            else:
                                                sg.popup('Formato de imagem inválido!', title='Erro de Imagem', non_blocking=True, font=(
                                                    'Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                                        else:
                                            sg.popup('Arquivo de imagem não encontrado!', title='Erro de Imagem', non_blocking=True, font=(
                                                'Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                                    else:
                                        # If no image is selected, add the product without an image
                                        adicionar_produto(
                                            nome, registro, eixo_x, nota_fiscal_pdf_path, eixo_z, quantidade, medida, validade, None)
                                        sg.popup('Produto adicionado sem imagem.', title='Produto Adicionado', non_blocking=True, font=(
                                            'Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                                        limpar_inputs(
                                            add_product_window, filepath)

                            elif add_event == 'selecionar_imagem':
                                filepath = sg.popup_get_file("Selecionar Imagem", file_types=(
                                    ("Imagens", "*.png;*.jpg;*.jpeg"),))
                                if not filepath:
                                    continue
                                add_product_window["path"].update(filepath)
                                if filepath and os.path.exists(filepath):
                                    insert_image(conn, filepath)
                                    if os.path.exists(filepath) and os.path.isfile(filepath):

                                        loading_window = loading_layout()
                                        if ultima_imagem_id:

                                            choose_window = choose_layout([])

                                            extract_nome(add_product_window,
                                                         conn, choose_window, timeout=5)
                                            extract_unidade_and_medida(
                                                add_product_window, conn, choose_window, timeout=5)

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

                            elif add_event == 'limpar_tudo':
                                limpar_inputs(add_product_window, filepath)

                            elif add_event == 'selecionar_pdf':
                                selected_nota_fiscal_pdf_path = sg.popup_get_file(
                                    "Selecionar PDF", file_types=(("Arquivos PDF", "*.pdf"),))
                                add_product_window["-NOTA_FISCAL_PDF-"].update(
                                    selected_nota_fiscal_pdf_path)

                                if selected_nota_fiscal_pdf_path:
                                    pdf_document = None
                                    try:
                                        pdf_document = fitz.open(
                                            selected_nota_fiscal_pdf_path)
                                        page = pdf_document[0]
                                        pix = page.get_pixmap()
                                        image_bytes = pix.tobytes()

                                        # Redimensiona a imagem para caber dentro dos limites desejados
                                        pil_image = Image.open(
                                            BytesIO(image_bytes))
                                        pil_image = pil_image.resize((50, 50), Image.ANTIALIAS if hasattr(
                                            Image, 'ANTIALIAS') else Image.LANCZOS)

                                        # Converte a imagem redimensionada de volta para o formato bytes
                                        image_bytes_resized = BytesIO()
                                        pil_image.save(
                                            image_bytes_resized, format='PNG')
                                        tk_pdf_image = ImageTk.PhotoImage(
                                            data=image_bytes_resized.getvalue())
                                        add_product_window['-PDF_PREVIEW-'].update(
                                            data=tk_pdf_image)
                                        add_product_window['text_pdf_info'].update(
                                            visible=True)

                                    except Exception as e:
                                        # Em caso de erro, mostra uma mensagem ao usuário
                                        print(f"Erro ao abrir PDF: {str(e)}")
                                    finally:
                                        if pdf_document is not None:
                                            pdf_document.close()

                            elif add_event == '-PDF_PREVIEW-':
                                # Se a imagem do PDF for clicada, abre a janela separada com mais funcionalidades para o PDF
                                selected_nota_fiscal_pdf_path = add_values["-NOTA_FISCAL_PDF-"]
                                if selected_nota_fiscal_pdf_path:
                                    try:
                                        view_selected_pdf_window(
                                            selected_nota_fiscal_pdf_path)

                                    except Exception as e:
                                        # Em caso de erro, mostra uma mensagem ao usuário
                                        sg.popup(f"Erro ao abrir PDF: {str(e)}", title='Erro', non_blocking=True, font=(
                                            'Helvetica', 10), keep_on_top=True, auto_close_duration=3)

                    elif event == 'Cancelar':
                        try:
                            cancelar = f'M112' + '\n'
                            try:
                                ser.write(cancelar.encode())
                                time.sleep(0.1)
                                print(cancelar)
                                sg.popup("Ação cancelada")
                            except serial.serialutil.SerialTimeoutException:
                                print(
                                    "Timeout ao tentar escrever na porta serial. Tentando novamente...")
                        except Exception as e:
                            sg.popup_error('Nenhuma porta serial conectada.\n\n Impossível fazer a comunicação.', title='Produtos Não Encontrados',
                                        non_blocking=True, font=('Helvetica', 10), keep_on_top=True)
                            print("Erro em Guardar: " + str(e))
                    
                    elif event == 'Exibir Produtos Existentes':
                        produtos = exibir_produtos_existentes()
                        if produtos:
                            # main_window.hide()

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
                            calibrar = f'G28 Y \n G28 Z \n G28 X' + '\n'
                            try:
                                ser.write(calibrar.encode())
                                time.sleep(0.1)
                                print(calibrar)
                                sg.popup('calibrando...')
                            except serial.serialutil.SerialTimeoutException:
                                print(
                                    "Timeout ao tentar escrever na porta serial. Tentando novamente...")
                        except Exception as e:
                            sg.popup_error('Nenhuma porta serial conectada.\n\n Impossível fazer a comunicação.', title='Produtos Não Encontrados',
                                           non_blocking=True, font=('Helvetica', 10), keep_on_top=True)
                            print("Erro em Calibrar: " + str(e))

                    elif event == 'Localizar Produto':
                        filtro = values.get("filtro_nome", "").strip()  # Usamos apenas um input
                        if filtro:
                            produtos = localizar_produto(filtro)
                            if produtos:
                                if len(produtos) == 1:
                                    selected_product_name = produtos[0][0]
                                    product_info = get_product_info(selected_product_name)

                                    if product_info:
                                        products_info_loop()

                                    products_table_window = sg.Window(
                                        "Produtos Existentes", products_table_layout(produtos), finalize=True
                                    )

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

                                                if product_info:
                                                    products_info_loop()
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
            else:
                sg.popup_error(
                    "Erro ao configurar a porta serial. Certifique-se de que a porta e a taxa de banda estão corretas.")
                print('Erro critico')
                # sys.exit()
                continue

        except Exception as e:
            print("Erro ao configurar a porta serial: " + str(e))
            sg.popup_error("Valores inválidos, tente novamente")
    else:
        sg.popup("Valores inválidos, tente novamente")
