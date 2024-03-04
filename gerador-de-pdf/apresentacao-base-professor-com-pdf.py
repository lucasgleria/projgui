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

sg.theme('lightblue7')
# sg.set_options(font=('Courier New', 20))


# Lock para garantir acesso seguro às variáveis globais
data_lock = threading.Lock()


# ...
imagem_path = None
nome = None  # Initialize these variables outside the loop
registro = None
eixo_x = None
nota_fiscal_pdf_path = None
eixo_z = None
quantidade = None
validade = None
medida_da_quantidade = None
selected_image_path = None
has_selected_image = False
Temperatura = None
Umidade = None
main_window = None

# ...


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
        sg.popup(ve, title='Erro de Conexão', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
        return None

# Funções globais
def reset_config_values(window):
    window['porta_COM'].update('')
    window['taxa_band'].update('')

# Função para limpar a entrada serial
def clear_serial_input(ser):
    while ser.in_waiting:
        ser.read(ser.in_waiting)

# Função para adicionar produtos
def adicionar_produto(nome, registro, eixo_x, nota_fiscal_pdf_path, eixo_z, quantidade, medida_da_quantidade, validade, image_path):
    global has_selected_image
    data_criada = datetime.datetime.now()
    cursor.execute('INSERT INTO produtos (nome, registro, eixo_x, nota_fiscal_pdf_path, eixo_z, quantidade, medida_da_quantidade, imagem_path, validade, data_criada) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   (nome, registro, eixo_x, nota_fiscal_pdf_path, eixo_z, quantidade, medida_da_quantidade, image_path, validade, data_criada))
    conn.commit()    
    sg.popup(f"O produto {nome} foi adicionado.", title='Produto adicionado', non_blocking=True, font=('Helvetica', 10), keep_on_top=True)
    has_selected_image = image_path is not None

# Função para converter a imagem em dados binários
def get_image_data(image_path):
    if os.path.exists(image_path) and os.path.isfile(image_path):
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
        return image_data
    return None

# Função para exibir produtos
def exibir_produtos_existentes():
    cursor.execute('SELECT nome, registro, validade FROM produtos')
    produtos = cursor.fetchall()
    return produtos
    

# Função para localizar produtos
def localizar_produto(filtro_nome):
    cursor.execute('SELECT nome, registro FROM produtos WHERE nome LIKE ?', ('%' + filtro_nome + '%',))
    produtos = cursor.fetchall()
    return produtos

# Função para pegar as informações do produto
def get_product_info(product_name):
    cursor.execute('SELECT nome, nota_fiscal_pdf_path, registro, quantidade, medida_da_quantidade, eixo_x, eixo_z, imagem_path, validade FROM produtos WHERE nome = ?', (product_name,))
    product_info = cursor.fetchone()

    if product_info:
        nome, nota_fiscal_pdf_path, registro, quantidade, medida_da_quantidade, eixo_x, eixo_z, image_path, validade = product_info

        # Verifica se há uma imagem associada
        if image_path and os.path.exists(image_path):
            return nome, nota_fiscal_pdf_path, registro, quantidade, medida_da_quantidade, eixo_x, eixo_z, image_path, validade
        else:
            return nome, nota_fiscal_pdf_path, registro, quantidade, medida_da_quantidade, eixo_x, eixo_z, None, validade
    else:
        return None


# Função para exibir em tabela
def products_table_layout(products):
    header = ["Nome", "Registro", "Validade"]
    data = [[product[0], product[1], get_product_info(product[0])[-1]] for product in products]

    return [
        [sg.Table(values=data, headings=header, auto_size_columns=False, justification='left',
                  display_row_numbers=False, hide_vertical_scroll=True, num_rows=min(25, len(data)),
                  col_widths=[20, 20, 20], key="table", enable_events=True)]
    ]

def display_image(image_path):
    if image_path:
        pil_image = Image.open(image_path)
        pil_image = pil_image.resize((300, 300), Image.ANTIALIAS if hasattr(Image, 'ANTIALIAS') else Image.LANCZOS)
        tk_image = ImageTk.PhotoImage(pil_image)
        info_product_window['-PRODUCT_IMAGE-'].update(data=tk_image, visible=True)

def products_info_loop():
    nome, nota_fiscal_pdf_path, registro, quantidade, medida_da_quantidade, eixo_x, eixo_z, image_path, validade = product_info
    main_window.hide()
    
    info_product_window = sg.Window("Informações do Produto", info_product_layout(has_selected_image=(image_path is not None), image_path=image_path), finalize=True)

    # Atualiza os elementos de texto na janela de informações do produto
    info_product_window["nome"].update(nome)
    info_product_window["registro"].update(registro)
    info_product_window["quantidade"].update(quantidade)
    info_product_window["medida_da_quantidade"].update(medida_da_quantidade)
    info_product_window["eixo_x"].update(eixo_x)
    info_product_window["eixo_z"].update(eixo_z)
    info_product_window["validade"].update(validade)

    if image_path:
        pil_image = Image.open(image_path)
        pil_image = pil_image.resize((300, 300), Image.ANTIALIAS if hasattr(Image, 'ANTIALIAS') else Image.LANCZOS)
        tk_image = ImageTk.PhotoImage(pil_image)
        info_product_window['-PRODUCT_IMAGE-'].update(data=tk_image, visible=True)
    else:
        info_product_window['-PRODUCT_IMAGE-'].update(data=None, visible=False)

    while True:
        info_event, info_values = info_product_window.read()

        if info_event == sg.WINDOW_CLOSED:
            break
        
        elif info_event == 'Visualizar a Nota Fiscal':
            if nota_fiscal_pdf_path:
                try:
                    # Abre o PDF com o visualizador padrão do sistema
                    os.startfile(nota_fiscal_pdf_path)
                except Exception as e:
                    sg.popup_error(f"Erro ao abrir o PDF: {e}", title="Erro")
            else:
                sg.popup("Nenhum PDF associado a este produto.", title="Informação", keep_on_top=True)

        elif info_event == 'Voltar':
            info_product_window.close()
            products_table_window.un_hide()

        elif info_event == 'Guardar Produto':
            guardar = f'X{eixo_x}Z{eixo_z}GUARDAR' + '\n'
            ser.write(guardar.encode())
            sg.popup(f"O produto foi guardado.", title='Produto guardado', non_blocking=True, font=('Helvetica', 10), keep_on_top=True)
            info_product_window.close()
            products_table_window.close()
            main_window.un_hide()

        elif info_event == 'Retirar Produto':
            info_product_window.hide()

            takeOff_product_window = sg.Window("Retirada do Produto", takeOff_product_layout(), finalize=True)

            while True:
                takeOff_event, takeOff_values = takeOff_product_window.read()

                if takeOff_event == sg.WINDOW_CLOSED:
                    break

                elif takeOff_event == 'Sim':
                    teste_sim = f'X{eixo_x}Z{eixo_z}RETIRAR' + '\n'
                    ser.write(teste_sim.encode())
                    sg.popup(f"O produto foi retirado.", title='Produto retirado', non_blocking=True, font=('Helvetica', 10), keep_on_top=True)
                    takeOff_product_window.close()
                    info_product_window.close()
                    products_table_window.close()
                    main_window.un_hide()

                elif takeOff_event == 'Não':
                    teste_nao = f'X{eixo_x}Z{eixo_z}RETIRARN' + '\n'
                    ser.write(teste_nao.encode())
                    sg.popup(f"O produto foi retirado.", title='Produto retirado', non_blocking=True, font=('Helvetica', 10), keep_on_top=True)
                    takeOff_product_window.close()
                    info_product_window.close()
                    products_table_window.close()
                    main_window.un_hide()

                elif info_event == "Limpar":
                    limpar = f'X{eixo_x}Z{eixo_Z}LIMPAR' + '\n'
                    ser.write(limpar.encode())


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
        enter = f'\n'
        ser.write(enter.encode())
        read_serial(ser)



########

# Interface gráfica com PySimpleGUI
def config_layout():
    return [
        [sg.Text("Porta COM:"), sg.InputText(key="porta_COM")],
        [sg.Text("Taxa Band:"), sg.Combo(['300', '1200' , '2400', '4800', '9600', '19200', '38400', '57600', '74880', '115200', '230400', '250000', '500000'], tooltip="choose something", key="taxa_band", size=(10, 1))],
        [sg.Button("OK")]
    ]

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

def add_product_layout():
    return [
        [sg.Text("Nome:"), sg.InputText(key="nome", size=(40, 1), pad=(54, None))],
        [sg.Text("Registro:"), sg.InputText(key="registro", size=(40, 1), pad=(40, None))],
        [sg.Text("Eixo X:"), sg.InputText(key="eixo_x", size=(40, 1), pad=(53, None))],
        [sg.Text("Eixo Z:"), sg.InputText(key="eixo_z", size=(40, 1), pad=(53, None))],
        [sg.Text("Validade:"), sg.InputText(key="validade", size=(40, 1), pad=(53, None))],
        [sg.Text("Quantidade:"), sg.InputText(key="quantidade", size=(20, 1), pad=(25, None)), sg.Combo(['unid' , 'mmg', 'mg', 'g', 'ml'], tooltip="choose something", key="medida_da_quantidade", size=(7, 1))],
        [sg.Button("Selecionar Imagem", key="selecionar_imagem"), sg.Button("Limpar Imagem", key="limpar_imagem")],
        [sg.Image(key='-IMAGE-', size=(300, 300), pad=(0, 0),)],
        [sg.Text("Nota Fiscal:"), sg.Input(key="-NOTA_FISCAL_PDF-"), sg.FileBrowse(key="-BROWSE_PDF-", file_types=(("PDF Files", "*.pdf"),))],
        [sg.Button("Adicionar")],
        [sg.Button('Voltar')],
        [sg.Text("", visible=False, key="imagem_path")],
    ]

def info_product_layout(has_selected_image=False, image_path=None):
    layout = [
        [sg.Text("Nome:"), sg.Text(nome, key="nome", size=(40, 1), pad=(54, None))],
        [sg.Text("Registro:"), sg.Text(registro, key="registro", size=(40, 1), pad=(40, None))],
        [sg.Text("Validade:"), sg.Text(validade, key="validade", size=(40, 1))],
        [sg.Text("Quantidade:"), sg.Text(quantidade, key="quantidade", size=(20, 1), pad=(25, None))], 
        [sg.Text("Medida da Quantidade: "), sg.Text(medida_da_quantidade, key="medida_da_quantidade")],
        [sg.Text("Eixo X:"), sg.Text(eixo_x, key="eixo_x", size=(40, 1), pad=(53, None))],
        [sg.Text("Eixo Z:"), sg.Text(eixo_z, key="eixo_z", size=(40, 1), pad=(53, None))],
        [sg.Image(key='-PRODUCT_IMAGE-', size=(300, 300), pad=(0, 0), expand_y=False, expand_x=False, visible=False)],
        [sg.Button("Visualizar a Nota Fiscal")],
        [sg.Button('Voltar')]
    ]

    if has_selected_image:
        layout[-2].insert(0, sg.Image(key='-PRODUCT_IMAGE-', visible=True))

    return layout


def takeOff_product_layout():
    return [
        [sg.Text("Deseja realizar limpeza?")],
        [sg.Button("Sim"), sg.Button("Não")]
]

# JANELA DE CONFIGURAÇÕES
config_window = sg.Window("Configurações", config_layout(), finalize=True)
main_window = None

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
        CREATE TABLE IF NOT EXISTS produtos 
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            registro TEXT,
            eixo_x TEXT,
            nota_fiscal_pdf_path TEXT,  
            eixo_z TEXT,
            quantidade INT,
            medida_da_quantidade TEXT,
            imagem_path TEXT,
            validade TEXT,
            data_criada DATETIME,
            data_guardada DATETIME,
            data_retirada DATETIME
        )
    ''')

except sqlite3.Error as e:
    sg.popup('Erro ao conectar ao banco de dados: ' + str(e), title='Erro', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
    sys.exit(1)


# JANELA PRINCIPAL
main_window = sg.Window("Controle de Estoque Farmacêutico Automático", main_layout())

# Inicia a thread para leitura serial
serial_thread_instance = threading.Thread(target=serial_thread, args=(ser,), daemon=True)
serial_thread_instance.start()

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
                ser = connect_to_arduino(values["porta_COM"], values["taxa_band"])
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

            elif add_event == 'Adicionar':
                nome = add_values.get("nome")
                registro = add_values.get("registro")
                eixo_x = add_values.get("eixo_x")
                nota_fiscal_pdf_path = add_values.get("-NOTA_FISCAL_PDF-")
                eixo_z = add_values.get("eixo_z")
                quantidade = add_values.get("quantidade")
                medida_da_quantidade = add_values.get("medida_da_quantidade")
                validade = add_values.get("validade")

                if not nome:
                    sg.popup('Campo Nome obrigatório!', title='Campo Obrigatório', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                elif not registro:
                    sg.popup('Campo Registro obrigatório!', title='Campo Obrigatório', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                elif not nota_fiscal_pdf_path:
                    sg.popup('Campo Nota Fiscal obrigatório!', title='Campo Obrigatório', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                elif not eixo_x.isdigit():
                    sg.popup('Campo Eixo X é obrigatório!\n\nPreencha com números inteiros.', title='Campo Obrigatório', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                elif not eixo_z.isdigit():
                    sg.popup('Campo Eixo Z é obrigatório!\n\nPreencha com números inteiros.', title='Campo Obrigatório', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                elif not quantidade.isdigit():
                    sg.popup('Campo Quantidade é obrigatório!\n\nPreencha com números inteiros', title='Campo Obrigatório', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                elif not medida_da_quantidade:
                    sg.popup('Campo Medida da Quantidade obrigatório!', title='Campo Obrigatório', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                elif not validade:
                    sg.popup('Campo Validade obrigatório!', title='Campo Obrigatório', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                else:
                    if selected_image_path and os.path.exists(selected_image_path):
                        # Check if the file is a valid image file
                        valid_image_extensions = {".png", ".jpg", ".jpeg"}
                        _, file_extension = os.path.splitext(selected_image_path)
                        if file_extension.lower() in valid_image_extensions:
                            # Converting the image to bytes
                            with open(selected_image_path, 'rb') as image_file:
                                image_data = image_file.read()

                            # Resizing the image to 300x300 pixels
                            pil_image = Image.open(BytesIO(image_data))
                            pil_image = pil_image.resize((300, 300), Image.ANTIALIAS if hasattr(Image, 'ANTIALIAS') else Image.LANCZOS)

                            # Converting the image to the format supported by PySimpleGUI
                            tk_image = ImageTk.PhotoImage(pil_image)

                            # Updating the image in the layout
                            add_product_window['-IMAGE-'].update(data=tk_image)
                            
                            # If everything is fine, add the product
                            adicionar_produto(nome, registro, eixo_x, nota_fiscal_pdf_path, eixo_z, quantidade, medida_da_quantidade, validade, selected_image_path)

                    else:
                        # If no image is selected, add the product without an image
                        adicionar_produto(nome, registro, eixo_x, nota_fiscal_pdf_path, eixo_z, quantidade, medida_da_quantidade, validade, None)




            elif add_event == 'selecionar_imagem':
                selected_image_path = sg.popup_get_file("Selecionar Imagem", file_types=(("Imagens", "*.png;*.jpg;*.jpeg"),))
                add_product_window["imagem_path"].update(selected_image_path)
                if selected_image_path and os.path.exists(selected_image_path):
                    if os.path.exists(selected_image_path) and os.path.isfile(selected_image_path):

                        # Check if the file is a valid image file
                        valid_image_extensions = {".png", ".jpg", ".jpeg"}
                        _, file_extension = os.path.splitext(selected_image_path)
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
                    sg.popup('Imagem não selecionada ou caminho inválido!', title='Erro', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                    continue  # Continue para o próximo loop, não adicionando o produto
            
            elif add_event == 'limpar_imagem':
                selected_image_path = None
                add_product_window["imagem_path"].update(selected_image_path)
                add_product_window['-IMAGE-'].update(data=None)

            elif add_event == 'selecionar_pdf':
                selected_nota_fiscal_pdf_path = sg.popup_get_file("Selecionar PDF", file_types=(("Arquivos PDF", "*.pdf"),))
                add_product_window["nota_fiscal_pdf_path"].update(selected_nota_fiscal_pdf_path)

            elif add_event == 'Voltar':
                add_product_window.close()
                main_window.un_hide()

    elif event == 'Exibir Produtos Existentes':
        produtos = exibir_produtos_existentes()
        if produtos:
            main_window.hide()

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
                        product_info = get_product_info(selected_product_name)

                        # Ensure that product_info is not None before using it
                        if product_info:
                            products_info_loop()

                    
        else:
            sg.popup('Nenhum produto cadastrado.', title='Produtos Não Encontrados', non_blocking=True, font=('Helvetica', 10), keep_on_top=True)

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
                    products_table_window = sg.Window("Listagem de Produtos", products_table_layout(produtos), finalize=True)

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
                sg.popup('Nenhum produto encontrado para o filtro fornecido.', title='Produtos não encontrados', non_blocking=True, font=('Helvetica', 10), keep_on_top=True)

if main_window:
    main_window.close()

if conn:
    conn.close()

ser.close()