import PySimpleGUI as sg
import sqlite3
import datetime
import serial


# Interface gráfica com PySimpleGUI
def config_layout():
    return [
        [sg.Text("Porta COM:"), sg.InputText(key="porta_COM")],
        [sg.Text("Taxa Band:"), sg.InputText(key="taxa_band")],
        [sg.Button("OK")]
    ]

def main_layout():
    return [
        [sg.Text("Nome:"), sg.InputText(key="nome")],
        [sg.Text("Eixo X:"), sg.InputText(key="eixo_x")],
        [sg.Text("Eixo Z:"), sg.InputText(key="eixo_z")],
        [sg.Text("Qntd:"), sg.InputText(key="qntd")],
        [sg.FileBrowse("Selecionar Imagem"), sg.InputText(key="imagem_path")],
        [sg.Button("Adicionar Produto")],
        [sg.HSeparator("Separador")],
        [sg.Text("Localizar por Nome:"), sg.InputText(key="filtro_nome"), sg.Button("Localizar Produto")],
        [sg.Listbox(values=[], size=(40, 10), key="produto_list")], 
        [sg.Button("Exibir Produtos")],
        [sg.Button("Arduino")],
        [sg.Button('Voltar')]
]

def arduino_layout():
    return [
        [sg.Text("Localizar por Nome:"), sg.InputText(key="filtro_nome"), sg.Button("Localizar Produto")],
        [sg.Button("Informações Produto", disabled=True)],
        [sg.Listbox(values=[], size=(100, 10), key="produto_list")], 
        [sg.Button("Exibir Produtos")],
        [sg.Button("Guardar Produto", disabled=True)],
        [sg.Button("Retirar Produto", disabled=True)],
        [sg.Button('Voltar')]
]

# JANELA DE CONFIGURAÇÕES
config_window = sg.Window("Configurações", config_layout())
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

    # Conexão com o Banco de Dados
    conn = sqlite3.connect("banco-de-dados-estoque.db")
    cursor = conn.cursor()

# Criando tabelas
cursor.execute('''
    CREATE TABLE IF NOT EXISTS produtos 
    (
        id INTEGER PRIMARY KEY,
        nome TEXT,
        eixo_x TEXT,
        eixo_z TEXT,
        qntd INT,
        imagem BLOB,
        data_entrada DATETIME
    )
''')

# Funções principais

def adicionar_produto(nome, eixo_x, eixo_z, qntd, imagem_path):
    data_entrada = datetime.datetime.now()
    imagem_binaria = None
    
    if imagem_path:
        with open(imagem_path, "rb") as img_file:
            imagem_binaria = img_file.read()

    cursor.execute('INSERT INTO produtos (nome, eixo_x, eixo_z, qntd, imagem, data_entrada) VALUES (?, ?, ?, ?, ?, ?)',
                (nome, eixo_x, eixo_z, qntd, imagem_binaria, data_entrada))
    conn.commit()


def localizar_produto(filtro_nome):
    cursor.execute('SELECT * FROM produtos WHERE nome LIKE ?', ('%' + filtro_nome + '%',))
    return cursor.fetchall()

def exibir_produtos():
    cursor.execute('SELECT * FROM produtos')
    return cursor.fetchall()

def atualizar_lista_produtos(window):
    produtos = exibir_produtos()
    window["produto_list"].update([f"{produto[1]} - Qntd: {produto[4]} - X: {produto[2]}, Z: {produto[3]} - Data: {produto[6]}" for produto in produtos])




# JANELA PRINCIPAL
main_window = sg.Window("Software de Estoque", main_layout())

while True:
    event, values = main_window.read()

    if event == sg.WINDOW_CLOSED or event == 'Sair':
        break

    elif event == 'Voltar':  
        main_window.close()  # Fecha a janela principal

        # Reabre a janela de configurações
        config_window = sg.Window("Configurações", config_layout())
        while True:
            event, values = config_window.read()

            if event == sg.WINDOW_CLOSED:
                break
            elif event == 'OK':
                # Seu código de configuração aqui
                break  # Sair do loop de configuração

        config_window.close()  # Fecha a janela de configurações

        # Reabre a janela principal
        main_window = sg.Window("Software de Estoque", main_layout())


    elif event == 'Adicionar Produto':
        NOME = values['nome']
        EIXO_X = values['eixo_x']
        EIXO_Z = values['eixo_z']
        QNTD = values['qntd']
        imagem_path = values['imagem_path']
        
        if not NOME:
            sg.popup('Campo Nome obrigatório!', title='Campo Obrigatório', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
        elif not EIXO_X.isdigit() or not EIXO_Z.isdigit() or not QNTD.isdigit():
            sg.popup('Preencha os campos:\n  Eixo X,\n  Eixo Z,\n  Qntd.\nCom um números inteiros', title='Campo Obrigatório', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
        # elif not imagem_path:
        #     sg.popup('Campo Imagem obrigatório!', title='Campo Obrigatório', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)
        else:
            adicionar_produto(NOME, int(EIXO_X), int(EIXO_Z), int(QNTD), imagem_path)
            produtos = exibir_produtos()
            main_window["produto_list"].update([f"{produto[1]} - Qntd: {produto[4]} - X: {produto[2]}, Z: {produto[3]} - Data: {produto[6]}" for produto in produtos])



    elif event == 'Localizar Produto':
        filtro_nome = values["filtro_nome"]
        produtos_encontrados = localizar_produto(filtro_nome)
        main_window["produto_list"].update([f"{produto[1]} - Qntd: {produto[4]} - X: {produto[2]}, Z: {produto[3]}" for produto in produtos_encontrados])


    elif event == 'Exibir Produtos':
        produtos = exibir_produtos()
        main_window["produto_list"].update([f"{produto[1]} - Qntd: {produto[4]} - X: {produto[2]}, Z: {produto[3]}" for produto in produtos])

    elif event == 'Arduino':
        main_window.hide()  # Oculta a janela principal

        # JANELA DO ARDUINO
        arduino_window = sg.Window("Modo Arduino", arduino_layout())
        filtro_realizado = False
        produto_selecionado = None

        

        while True:
            arduino_event, arduino_values = arduino_window.read()

            if arduino_event == sg.WINDOW_CLOSED:
                break
            elif arduino_event == 'Voltar':
                break
            elif arduino_event == 'Sair':
                main_window.close()  # Fecha a janela principal
                arduino_window.close()  # Fecha a janela do Arduino
                break  # Sai do loop interno, retornando à janela principal

            elif arduino_event == 'Localizar Produto':
                filtro_nome = arduino_values["filtro_nome"]  
                produtos_encontrados = localizar_produto(filtro_nome)
                arduino_window['produto_list'].update([f"Nome: {produto[1]} - Eixo X: {produto[2]}, Eixo Z: {produto[3]}" for produto in produtos_encontrados])
                if len(produtos_encontrados) == 1:
                    produto_selecionado = produtos_encontrados[0]
                    filtro_realizado = True
                    arduino_window['Informações Produto'].update(disabled=False)
                    arduino_window['Retirar Produto'].update(disabled=False)
                    arduino_window['Guardar Produto'].update(disabled=False)
                else:
                    sg.popup('A pesquisa deve retornar um único produto para a retirada.', title='Seleção de Produto', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)

            elif arduino_event == 'Informações Produto':
                if filtro_realizado:
                    filtro_nome = arduino_values["filtro_nome"]  
                    produtos_encontrados = localizar_produto(filtro_nome)
                    arduino_window['produto_list'].update([f"Nome: {produto[1]} - Eixo X: {produto[2]}, Eixo Z: {produto[3]} - Quantidade: {produto[4]} - Data de Entrada: {produto[7]} - Imagem: {produto[6]}" for produto in produtos_encontrados])
                else:
                    sg.popup('Realize uma pesquisa antes de visualizar as informações do produto!', title='Pesquisa Necessária', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)

            elif arduino_event == 'Exibir Produtos':
                produtos = exibir_produtos()
                arduino_window["produto_list"].update([f"{produto[1]} - Qntd: {produto[4]} - X: {produto[2]}, Z: {produto[3]}" for produto in produtos])

            elif arduino_event == 'Retirar Produto':
                if filtro_realizado and produto_selecionado is not None:
                    pos_x = produto_selecionado[2]
                    pos_z = produto_selecionado[3]
                    retirada_string = f"X{pos_x}Z{pos_z}RETIRAR" + '\n'
                    ser.write(retirada_string.encode())

                    # Atualize a lista de produtos após a retirada
                    atualizar_lista_produtos(arduino_window)

                    # Redefina filtro_realizado para False após a retirada
                    filtro_realizado = False
                else:
                    sg.popup('Selecione um único produto antes de fazer a retirada.', title='Seleção de Produto', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)

            elif arduino_event == 'Guardar Produto':
                if filtro_realizado and produto_selecionado is not None:
                    pos_x = produto_selecionado[2]
                    pos_z = produto_selecionado[3]
                    guarda_string = f"X{pos_x}Z{pos_z}GUARDAR"+'\n'
                    ser.write(guarda_string.encode())

                # Atualize a lista de produtos após a retirada
                atualizar_lista_produtos(arduino_window)

                # Redefina filtro_realizado para False após a retirada
                filtro_realizado = False
            else:
                sg.popup('Selecione um único produto antes de guardar.', title='Seleção de Produto', non_blocking=True, font=('Helvetica', 10), keep_on_top=True, auto_close_duration=3)

        arduino_window.close()  # Fecha a janela do Arduino
        main_window.un_hide()  # Exibe novamente a janela principal

if main_window:
    main_window.close()

if conn:
    conn.close()