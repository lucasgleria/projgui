
# faça com que ao filtrar mais de um produto pelo botão localizar produto, exiba o resultado da busca no popup, se encontrar apenas um resultado correspondente siga para a janela de informações do produto, exibindo todas as informações possiveis do produto de forma dinamica:

import sys
import PySimpleGUI as sg
import sqlite3
import datetime
import serial


# sg.theme('DarkBlue')
# sg.set_options(font=('Courier New', 20))

# Interface gráfica com PySimpleGUI
def config_layout():
    return [
        [sg.Text("Porta COM:"), sg.InputText(key="porta_COM")],
        [sg.Text("Taxa Band:"), sg.InputText(key="taxa_band")],
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
        [sg.Text("Quantidade:"), sg.InputText(key="quantidade", size=(20, 1), pad=(25, None)), sg.Combo(['', 'u' , 'mmg', 'mg', 'g', 'ml'], tooltip="choose something", key="medida_da_quantidade", size=(7, 1))],
        [sg.FileBrowse("Selecionar Imagem", key="imagem_path"), sg.Text(key="imagem_path")],
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
        conn = sqlite3.connect("banco-de-dados-estoque.db")
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
                imagem BLOB,
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
    data_criada = datetime.datetime.now()
    imagem_binaria = None
    
    if imagem_path:
        with open(imagem_path, "rb") as img_file:
            imagem_binaria = img_file.read()

    cursor.execute('INSERT INTO produtos (nome, registro, eixo_x, eixo_z, quantidade, notaFiscal, medida_da_quantidade, imagem, data_criada) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (nome, registro, eixo_x, eixo_z, quantidade, notaFiscal, medida_da_quantidade, imagem_binaria, data_criada))
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
    cursor.execute('SELECT nome, notaFiscal, registro, quantidade, medida_da_quantidade, eixo_x, eixo_z FROM produtos WHERE nome = ?', (product_name,))
    product_info = cursor.fetchone()
    
    if product_info:
        nome, notaFiscal, registro, quantidade, medida_da_quantidade, eixo_x, eixo_z = product_info
        return nome, notaFiscal, registro, quantidade, medida_da_quantidade, eixo_x, eixo_z
    else:
        return None



# JANELA PRINCIPAL
main_window = sg.Window("Software de Estoque", main_layout())

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

        config_window.close()  # Fecha a janela de configurações

        # Reabre a janela principal
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
                imagem_path = add_values['imagem_path']
                
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
                # elif not imagem_path:
                #     sg.popup('Campo Imagem obrigatório!', title='Campo Obrigatório', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
                
                else:  
                    adicionar_produto(NOME, REGISTRO, EIXO_X, EIXO_Z, QUANTIDADE, NOTAFISCAL, MEDIDADAQUANTIDADE, imagem_path)                    
                    sg.popup(f"O produto {NOME} foi adicionado.", title='Produto adicionado', non_blocking=True, font=('Helvetica', 10), keep_on_top=True)
                
            elif add_event == 'Voltar':
                add_product_window.close()
                main_window.un_hide()

    elif event == 'Exibir Produtos Existentes':
        produtos = exibir_produtos_existentes()
        listagem_dos_produtos = "\n".join([f"{product[0]} - {product[1]}" for product in produtos])
        sg.popup(f"Produtos Existentes:\nNome do Produto - Registro do Produto\n {listagem_dos_produtos}", title='Produtos Existentes', non_blocking=True, font=('Helvetica', 10), keep_on_top=True)

    elif event == 'Localizar Produto':
        # MAIS DE UM RESULTADO EXIBA O POPUP, APENAS UM RESULTADO, EXIBIR JANELA DE INFORMAÇÕES DO PRODUTO
        filtro_nome = values["filtro_nome"]
        if filtro_nome:
            produtos = localizar_produto(filtro_nome)
            if produtos:
                if len(produtos) == 1:
                    main_window.hide()

                    info_product_window = sg.Window("Informações do Produto", info_product_layout(), finalize=True)  # Adicione finalize=True aqui

                    product_info = get_product_info(produtos[0][0])

                    if product_info:
                        nome, notaFiscal, registro, quantidade, medida_da_quantidade, eixo_x, eixo_z = product_info

                        # Atualiza os elementos de texto na janela de informações do produto
                        info_product_window["nome"].update(nome)
                        info_product_window["notaFiscal"].update(notaFiscal)
                        info_product_window["registro"].update(registro)
                        info_product_window["quantidade"].update(quantidade)
                        info_product_window["medida_da_quantidade"].update(medida_da_quantidade)
                        info_product_window["eixo_x"].update(eixo_x)
                        info_product_window["eixo_z"].update(eixo_z)
                    
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
                                        takeOff_product_window.close()
                                        info_product_window.un_hide()
                else:
                    listagem_dos_produtos = "\n".join([f"{product[0]} - {product[1]}" for product in produtos])
                    sg.popup(f"Produtos encontrados:\nNome do Produto - Registro do Produto\n {listagem_dos_produtos}", title='Produtos Encontrados', non_blocking=True, font=('Helvetica', 10), keep_on_top=True)
            
            else:
                sg.popup('Nenhum produto encontrado para o filtro fornecido.', title='Produtos não encontrados', non_blocking=True, font=('Helvetica', 10), keep_on_top=True)


if main_window:
    main_window.close()

if conn:
    conn.close()