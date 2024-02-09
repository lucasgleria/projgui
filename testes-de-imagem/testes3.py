#captura da pasta 'pasta-de-imagem'

import sys
import PySimpleGUI as sg
import sqlite3
import datetime
import serial
import os
import shutil


# sg.theme('DarkBlue')
# sg.set_options(font=('Courier New', 20))

# Interface gráfica com PySimpleGUI
def config_layout():
    return [
        [sg.Text("Porta COM:"), sg.InputText(key="porta_COM")],
        [sg.Text("Taxa Band:"), sg.Combo(['300', '1200' , '2400', '4800', '9600', '19200', '38400', '57600', '74880', '115200', '230400', '250000', '500000'], tooltip="choose something", key="taxa_band", size=(10, 1))],
        [sg.Button("OK")]
    ]

def main_layout():
    return [
        [sg.Button("Adicionar Produto"), sg.Button("Exibir Produtos Existentes")],
        [sg.HSeparator("Separador")],
        [sg.Text("Localizar por Nome:"), sg.InputText(key="filtro_nome"), sg.Button("Localizar Produto")],
        [sg.Button('Voltar')]
]

def add_product_layout():
    return [
        [sg.Text("Nome:"), sg.InputText(key="nome", size=(40, 1), pad=(54, None))],
        [sg.Text("Registro:"), sg.InputText(key="registro", size=(40, 1), pad=(40, None))],
        [sg.Text("N° Nota Fiscal:"), sg.InputText(key="notaFiscal", size=(40, 1))],
        [sg.Text("Eixo X:"), sg.InputText(key="eixo_x", size=(40, 1), pad=(53, None))],
        [sg.Text("Eixo Z:"), sg.InputText(key="eixo_z", size=(40, 1), pad=(53, None))],
        [sg.Text("Quantidade:"), sg.InputText(key="quantidade", size=(20, 1), pad=(25, None)), sg.Combo(['unid' , 'mmg', 'mg', 'g', 'ml'], tooltip="choose something", key="medida_da_quantidade", size=(7, 1))],
        [sg.FileBrowse("Selecionar Imagem", key="imagem_path")],
        [sg.Button("Adicionar")],
        [sg.Button('Voltar')]
]

def info_product_layout():
    return [
        [sg.Text("Nome: "), sg.Text(key="nome")],
        [sg.Text("Nota Fiscal: "), sg.Text(key="notaFiscal")],
        [sg.Text("Registro: "), sg.Text(key="registro")],
        [sg.Text("Quantidade: "), sg.Text(key="quantidade")],
        [sg.Text("Medida da Quantidade: "), sg.Text(key="medida_da_quantidade")],
        [sg.Text("Eixo X: "), sg.Text(key="eixo_x")],
        [sg.Text("Eixo Z: "), sg.Text(key="eixo_z")],
        [sg.Image(key="imagem_produto", size=(300, 300))],
        [sg.Button("Guardar Produto"), sg.Button("Retirar Produto")],
        [sg.Button('Voltar')]
    ]


def takeOff_product_layout():
    return [
        [sg.Text("Deseja realizar limpeza?")],
        [sg.Button("Sim"), sg.Button("Não")]
]

# JANELA DE CONFIGURAÇÕES
config_window = sg.Window("Configurações", config_layout(), finalize=True)
main_window = None
nova_imagem_path = None

# Loop para a janela de configurações
while True:
    event, values = config_window.read()

    if event == sg.WINDOW_CLOSED:
        break
    elif event == 'OK':
        porta_COM = values["porta_COM"]
        taxa_band = values["taxa_band"]

        if not porta_COM:
            sg.popup('Campo Porta COM obrigatório!', title='Campo Obrigatório', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
        elif not taxa_band:
            sg.popup('Campo Taxa Band obrigatório!', title='Campo Obrigatório', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
        elif not taxa_band.isnumeric():
            sg.popup('A Taxa Band deve ser um valor numérico!', title='Campo Inválido', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
        else:
            # Conectando ao Arduino
            ser = serial.Serial(porta_COM, int(taxa_band), timeout=2)
            break

config_window.close()

if not values["porta_COM"] or not values["taxa_band"]:
    sg.popup('Campos obrigatórios não preenchidos!', title='Campos Obrigatórios', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
else:
    try:
        # Conexão com o Banco de Dados
        conn = sqlite3.connect("banco-de-dados-estoque-teste-imagem.db")
        cursor = conn.cursor()

        # Criando tabelas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produtos 
            (
                id INTEGER PRIMARY KEY,
                nome TEXT,
                registro TEXT,
                eixo_x TEXT,
                notaFiscal TEXT,
                eixo_z TEXT,
                quantidade INT,
                medida_da_quantidade TEXT,
                imagem_path TEXT,
                data_criada DATETIME,
                data_guardada DATETIME,
                data_retirada DATETIME
            )
        ''')
    except sqlite3.Error as e:
        sg.popup('Erro ao conectar ao banco de dados: ' + str(e), title='Erro', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
        sys.exit(1)

# Funções globais
def reset_config_values(window):
    window['porta_COM'].update('')
    window['taxa_band'].update('')

# Função para limpar a entrada serial
def clear_serial_input(ser):
    while ser.in_waiting:
        ser.read(ser.in_waiting)

# Função para adicionar produtos
def adicionar_produto(nome, registro, eixo_x, eixo_z, quantidade, notaFiscal, medida_da_quantidade, imagem_path):
    global nova_imagem_path  # Add this line to indicate that you want to use the global variable
    data_criada = datetime.datetime.now()

    # Verifica se a pasta "Pasta-de-Imagens" existe, senão cria
    if not os.path.exists("Pasta-de-Imagens"):
        os.makedirs("Pasta-de-Imagens")

    nova_imagem_path = None

    # Se a imagem_path estiver preenchida, copie a imagem para a nova localização
    if imagem_path:
        # Obtém o nome do arquivo da imagem
        imagem_filename = os.path.basename(imagem_path)

        # Define o caminho para a nova localização da imagem
        nova_imagem_path = os.path.join("Pasta-de-Imagens", imagem_filename)

        # Copia a imagem para a nova localização
        shutil.copy(imagem_path, nova_imagem_path)

    # Insere os dados no banco de dados, utilizando o novo caminho da imagem
    cursor.execute('''
        INSERT INTO produtos 
        (nome, registro, eixo_x, eixo_z, quantidade, notaFiscal, medida_da_quantidade, imagem_path, data_criada) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (nome, registro, eixo_x, eixo_z, quantidade, notaFiscal, medida_da_quantidade, nova_imagem_path, data_criada))
    conn.commit()


# Função para exibir produtos
def exibir_produtos_existentes():
    cursor.execute('SELECT nome, registro FROM produtos')
    produtos = cursor.fetchall()
    return produtos

# Função para localizar produtos
def localizar_produto(filtro_nome):
    cursor.execute('SELECT nome, registro FROM produtos WHERE nome LIKE ?', ('%' + filtro_nome + '%',))
    produtos = cursor.fetchall()
    return produtos

# Função para pegar as informações do produto
def get_product_info(product_name):
    cursor.execute('SELECT nome, notaFiscal, registro, quantidade, medida_da_quantidade, eixo_x, eixo_z, imagem_path FROM produtos WHERE nome = ?', (product_name,))
    product_info = cursor.fetchone()

    return product_info



def products_table_layout(products):
    header = ["Nome", "Registro"]
    data = [[product[0], product[1]] for product in products]

    return [
        [sg.Table(values=data, headings=header, auto_size_columns=False, justification='left',
                  display_row_numbers=False, hide_vertical_scroll=True, num_rows=min(25, len(data)),
                  col_widths=[20, 20], key="table", enable_events=True)]
]


# JANELA PRINCIPAL
main_window = sg.Window("Software de Estoque", main_layout())


while True:
    event, values = main_window.read()

    if event == sg.WINDOW_CLOSED:
        break

    elif event == 'Voltar':  
        main_window.close()  
        clear_serial_input(ser)
        ser.close()  

        config_window = sg.Window("Configurações", config_layout(), finalize=True)

        reset_config_values(config_window)
        while True:
            event, values = config_window.read()

            if event == sg.WINDOW_CLOSED:
                break

            elif event == 'OK':
                porta_COM = values["porta_COM"]
                taxa_band = values["taxa_band"]

                if not porta_COM:
                    sg.popup('Campo Porta COM obrigatório!', title='Campo Obrigatório', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                elif not taxa_band:
                    sg.popup('Campo Taxa Band obrigatório!', title='Campo Obrigatório', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                elif not taxa_band.isnumeric():
                    sg.popup('A Taxa Band deve ser um valor numérico!', title='Campo Inválido', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                else:
                    
                    ser = serial.Serial(porta_COM, int(taxa_band), timeout=2)
                    break 

        config_window.close()  

        main_window = sg.Window("Software de Estoque", main_layout())


    elif event == 'Adicionar Produto':
        main_window.hide()

        add_product_window = sg.Window("Adicione Produtos", add_product_layout())

        while True:
            add_event, add_values = add_product_window.read()

            if add_event == sg.WINDOW_CLOSED:
                break

            elif add_event == 'Adicionar':
                NOME = add_values['nome']
                REGISTRO = add_values['registro']
                EIXO_X = add_values['eixo_x']
                EIXO_Z = add_values['eixo_z']
                QUANTIDADE = add_values['quantidade']
                NOTAFISCAL = add_values['notaFiscal']
                MEDIDADAQUANTIDADE = add_values['medida_da_quantidade']
                IMAGEM_PATH = add_values['imagem_path']
                
                if not NOME:
                    sg.popup('Campo Nome obrigatório!', title='Campo Obrigatório', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                elif not REGISTRO:
                    sg.popup('Campo Registro obrigatório!', title='Campo Obrigatório', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                elif not NOTAFISCAL:
                    sg.popup('Campo Nota Fiscal obrigatório!', title='Campo Obrigatório', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                elif not EIXO_X.isdigit():
                    sg.popup('Campo Eixo X é obrigatório!\n\nPreencha com números inteiros.', title='Campo Obrigatório', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                elif not EIXO_Z.isdigit():
                    sg.popup('Campo Eixo Z é obrigatório!\n\nPreencha com números inteiros.', title='Campo Obrigatório', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                elif not QUANTIDADE.isdigit():
                    sg.popup('Campo Quantidade é obrigatório!\n\nPreencha com números inteiros', title='Campo Obrigatório', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                elif not MEDIDADAQUANTIDADE:
                    sg.popup('Campo Medida da Quantidade obrigatório!', title='Campo Obrigatório', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                # elif not IMAGEM_PATH:
                #     sg.popup('Selecione uma imagem!', title='Campo Obrigatório', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
    
                else:  
                    adicionar_produto(NOME, REGISTRO, EIXO_X, EIXO_Z, QUANTIDADE, NOTAFISCAL, MEDIDADAQUANTIDADE,IMAGEM_PATH)                    
                    sg.popup(f"O produto {NOME} foi adicionado.", title='Produto adicionado', non_blocking=True, font=('Helvetica', 10), keep_on_top=True)
                
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
                        main_window.hide()

                        info_product_window = sg.Window("Informações do Produto", info_product_layout(), finalize=True)

                        product_info = get_product_info(selected_product_name)

                        if product_info:
                            nome, notaFiscal, registro, quantidade, medida_da_quantidade, eixo_x, eixo_z, imagem_path = product_info


                            # Atualiza os elementos de texto na janela de informações do produto
                            info_product_window["nome"].update(product_info[0])
                            info_product_window["notaFiscal"].update(product_info[1])
                            info_product_window["registro"].update(product_info[2])
                            info_product_window["quantidade"].update(product_info[3])
                            info_product_window["medida_da_quantidade"].update(product_info[4])
                            info_product_window["eixo_x"].update(product_info[5])
                            info_product_window["eixo_z"].update(product_info[6])

                            if imagem_path:
                                info_product_window["imagem_produto"].update(filename=imagem_path)
                            else:
                                # Caso não haja imagem, exibir uma imagem padrão ou uma mensagem
                                info_product_window["imagem_produto"].update(filename=r'C:\Users\Lucas\Desktop\Fichario\Projetos\PESSOAIS\Proj Guilherme\transparente2.png', size=(50, 50))

                            while True:
                                info_event, info_values = info_product_window.read()

                                if info_event == sg.WINDOW_CLOSED:
                                    break

                                elif info_event == 'Voltar':
                                    info_product_window.close()
                                    products_table_window.un_hide()

                                elif info_event == 'Guardar Produto':
                                    sg.popup(f"O produto {selected_product_name} foi guardado.", title='Produto Guardado', non_blocking=True, font=('Helvetica', 10), keep_on_top=True)

                                elif info_event == 'Retirar Produto':
                                    info_product_window.hide()

                                    takeOff_product_window = sg.Window("Retirada do Produto", takeOff_product_layout(), finalize=True)

                                    while True:
                                        takeOff_event, takeOff_values = takeOff_product_window.read()

                                        if takeOff_event == sg.WINDOW_CLOSED:
                                            break

                                        elif takeOff_event == 'Sim':
                                            sg.popup(f"O produto foi retirado.", title='Produto retirado', non_blocking=True, font=('Helvetica', 10), keep_on_top=True)
                                            takeOff_product_window.close()
                                            info_product_window.close()
                                            products_table_window.close()
                                            main_window.un_hide()

                                        elif takeOff_event == 'Não':
                                            sg.popup(f"O produto foi retirado.", title='Produto retirado', non_blocking=True, font=('Helvetica', 10), keep_on_top=True)
                                            takeOff_product_window.close()
                                            info_product_window.close()
                                            products_table_window.close()
                                            main_window.un_hide()
                    
        else:
            sg.popup('Nenhum produto cadastrado.', title='Produtos Não Encontrados', non_blocking=True, font=('Helvetica', 10), keep_on_top=True)

    elif event == 'Localizar Produto':
        filtro_nome = values["filtro_nome"]
        if filtro_nome:
            produtos = localizar_produto(filtro_nome)
            if produtos:
                if len(produtos) == 1:
                    main_window.hide()

                    info_product_window = sg.Window("Informações do Produto", info_product_layout(), finalize=True)  # Adicione finalize=True aqui

                    product_info = get_product_info(produtos[0][0])

                    if product_info:
                        nome, notaFiscal, registro, quantidade, medida_da_quantidade, eixo_x, eixo_z, imagem_path = product_info


                        # Atualiza os elementos de texto na janela de informações do produto
                        info_product_window["nome"].update(product_info[0])
                        info_product_window["notaFiscal"].update(product_info[1])
                        info_product_window["registro"].update(product_info[2])
                        info_product_window["quantidade"].update(product_info[3])
                        info_product_window["medida_da_quantidade"].update(product_info[4])
                        info_product_window["eixo_x"].update(product_info[5])
                        info_product_window["eixo_z"].update(product_info[6])

                        if imagem_path:
                            info_product_window["imagem_produto"].update(filename=imagem_path)
                        else:
                            # Caso não haja imagem, exibir uma imagem padrão ou uma mensagem
                            info_product_window["imagem_produto"].update(filename=r'C:\Users\Lucas\Desktop\Fichario\Projetos\PESSOAIS\Proj Guilherme\transparente2.png', size=(50, 50))
                    
                        while True:
                            info_event, info_values = info_product_window.read()

                            if info_event == sg.WINDOW_CLOSED:
                                break

                            elif info_event == 'Voltar':
                                info_product_window.close()
                                main_window.un_hide()

                            elif info_event == 'Guardar Produto':
                                sg.popup(f"O produto {NOME} foi guardado.", title='Produto Guardado', non_blocking=True, font=('Helvetica', 10), keep_on_top=True)

                            elif info_event == 'Retirar Produto':
                                info_product_window.hide()

                                takeOff_product_window = sg.Window("Retirada do Produto", takeOff_product_layout())

                                while True:
                                    takeOff_event, takeOff_values = takeOff_product_window.read()

                                    if takeOff_event == sg.WINDOW_CLOSED:
                                        break

                                    elif takeOff_event == 'Sim':
                                        sg.popup(f"O produto foi retirado.", title='Produto retirado', non_blocking=True, font=('Helvetica', 10), keep_on_top=True)
                                        takeOff_product_window.close()
                                        info_product_window.close()
                                        main_window.un_hide()

                                    elif takeOff_event == 'Não':
                                        sg.popup(f"O produto foi retirado.", title='Produto retirado', non_blocking=True, font=('Helvetica', 10), keep_on_top=True)
                                        takeOff_product_window.close()
                                        info_product_window.close()
                                        main_window.un_hide()
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
                                main_window.hide()

                                info_product_window = sg.Window("Informações do Produto", info_product_layout(), finalize=True)

                                product_info = get_product_info(selected_product_name)

                                if product_info:
                                    nome, notaFiscal, registro, quantidade, medida_da_quantidade, eixo_x, eixo_z, imagem_path = product_info


                                    # Atualiza os elementos de texto na janela de informações do produto
                                    info_product_window["nome"].update(product_info[0])
                                    info_product_window["notaFiscal"].update(product_info[1])
                                    info_product_window["registro"].update(product_info[2])
                                    info_product_window["quantidade"].update(product_info[3])
                                    info_product_window["medida_da_quantidade"].update(product_info[4])
                                    info_product_window["eixo_x"].update(product_info[5])
                                    info_product_window["eixo_z"].update(product_info[6])

                                    if imagem_path:
                                        info_product_window["imagem_produto"].update(filename=imagem_path)
                                    else:
                                        # Caso não haja imagem, exibir uma imagem padrão ou uma mensagem
                                        info_product_window["imagem_produto"].update(filename=r'C:\Users\Lucas\Desktop\Fichario\Projetos\PESSOAIS\Proj Guilherme\transparente2.png', size=(50, 50))

                                    while True:
                                        info_event, info_values = info_product_window.read()

                                        if info_event == sg.WINDOW_CLOSED:
                                            break

                                        elif info_event == 'Voltar':
                                            info_product_window.close()
                                            products_table_window.un_hide()

                                        elif info_event == 'Guardar Produto':
                                            sg.popup(f"O produto {selected_product_name} foi guardado.", title='Produto Guardado', non_blocking=True, font=('Helvetica', 10), keep_on_top=True)

                                        elif info_event == 'Retirar Produto':
                                            info_product_window.hide()

                                            takeOff_product_window = sg.Window("Retirada do Produto", takeOff_product_layout(), finalize=True)

                                            while True:
                                                takeOff_event, takeOff_values = takeOff_product_window.read()

                                                if takeOff_event == sg.WINDOW_CLOSED:
                                                    break

                                                elif takeOff_event == 'Sim':
                                                    sg.popup(f"O produto foi retirado.", title='Produto retirado', non_blocking=True, font=('Helvetica', 10), keep_on_top=True)
                                                    takeOff_product_window.close()
                                                    info_product_window.close()
                                                    products_table_window.close()
                                                    main_window.un_hide()

                                                elif takeOff_event == 'Não':
                                                    sg.popup(f"O produto foi retirado.", title='Produto retirado', non_blocking=True, font=('Helvetica', 10), keep_on_top=True)
                                                    takeOff_product_window.close()
                                                    info_product_window.close()
                                                    products_table_window.close()
                                                    main_window.un_hide()
            else:
                sg.popup('Nenhum produto encontrado para o filtro fornecido.', title='Produtos não encontrados', non_blocking=True, font=('Helvetica', 10), keep_on_top=True)


if main_window:
    main_window.close()

if conn:
    conn.close()   