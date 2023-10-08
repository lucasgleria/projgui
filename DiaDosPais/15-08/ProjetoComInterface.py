import PySimpleGUI as sg
import sqlite3
import datetime

# Interface gráfica com PySimpleGUI
# config_layout = []

def main_layout():
    return [
        [sg.Text("Nome:"), sg.InputText(key="nome")],
        [sg.Text("Eixo X:"), sg.InputText(key="eixo_x")],
        [sg.Text("Eixo Y:"), sg.InputText(key="eixo_y")],
        [sg.Text("Eixo Z:"), sg.InputText(key="eixo_z")],
        [sg.FileBrowse("Selecionar Imagem"), sg.InputText(key="imagem_path")],
        [sg.Button("Adicionar Produto")],
        [sg.HSeparator("Separador")],
        [sg.Text("Localizar por Nome:"), sg.InputText(key="filtro_nome"), sg.Button("Localizar Produto")],
        [sg.Listbox(values=[], size=(40, 10), key="produto_list")], 
        [sg.Button("Exibir Produtos")],
        [sg.Button("Arduino")]
        # [sg.Button('Voltar')]
]

def arduino_layout():
    return [
        [sg.Text("Localizar por Nome:"), sg.InputText(key="filtro_nome"), sg.Button("Localizar Produto")],
        [sg.Button("Informações Produto")],
        [sg.Listbox(values=[], size=(40, 10), key="produto_list")], 
        [sg.Button("Exibir Produtos")],
        [sg.Button("Guardar Produto")],
        [sg.Button("Retirar Produto")],
        [sg.Button('Voltar')]
]

# Primeira tela
main_window = sg.Window("Software de Estoque", main_layout())

# Conexão com Banco de Dados
conn = sqlite3.connect("banco-de-dados-estoque.db")
cursor = conn.cursor()
# Criando tabelas
cursor.execute('''
    CREATE TABLE IF NOT EXISTS produtos 
    (
        id INTEGER PRIMARY KEY,
        nome TEXT,
        eixo_x TEXT,
        eixo_y TEXT,
        eixo_z TEXT,
        imagem BLOB,
        data_entrada DATETIME
    )
''')

def adicionar_produto(nome, eixo_x, eixo_y, eixo_z, imagem_path):
    data_entrada = datetime.datetime.now()
    
    with open(imagem_path, "rb") as img_file:
        imagem_binaria = img_file.read()

    cursor.execute('INSERT INTO produtos (nome, eixo_x, eixo_y, eixo_z, data_entrada, imagem) VALUES (?, ?, ?, ?, ?, ?)',
                (nome, eixo_x, eixo_y, eixo_z, data_entrada, imagem_binaria))
    conn.commit()

def localizar_produto(filtro_nome):
    cursor.execute('SELECT * FROM produtos WHERE nome LIKE ?', ('%' + filtro_nome + '%',))
    return cursor.fetchall()

def exibir_produtos():
    cursor.execute('SELECT * FROM produtos')
    return cursor.fetchall()





while True:
    event, values = main_window.read()

    if event == sg.WINDOW_CLOSED or event == 'Sair':
        break
    elif event == 'Adicionar Produto':
        NOME = values['nome']
        EIXO_X = values['eixo_x']
        EIXO_Y = values['eixo_y']
        EIXO_Z = values['eixo_z']
        imagem_path = values['imagem_path']
        
        if not NOME:
            sg.popup('Campo Nome obrigatório!', title='Campo Obrigatório', non_blocking=True, font=('Helvetica', 15), keep_on_top=True, auto_close_duration=3)
        elif not EIXO_X:
            sg.popup('Campo Eixo X obrigatório!', title='Campo Obrigatório', non_blocking=True, font=('Helvetica', 15), keep_on_top=True, auto_close_duration=3)
        elif not EIXO_Y:
            sg.popup('Campo Eixo Y obrigatório!', title='Campo Obrigatório', non_blocking=True, font=('Helvetica', 15), keep_on_top=True, auto_close_duration=3)
        elif not EIXO_Z:
            sg.popup('Campo Eixo Z obrigatório!', title='Campo Obrigatório', non_blocking=True, font=('Helvetica', 15), keep_on_top=True, auto_close_duration=3)
        elif not imagem_path:
            sg.popup('Campo Imagem obrigatório!', title='Campo Obrigatório', non_blocking=True, font=('Helvetica', 15), keep_on_top=True, auto_close_duration=3)
        else:
            adicionar_produto(NOME, EIXO_X, EIXO_Y, EIXO_Z, imagem_path)
            produtos = exibir_produtos()
            main_window["produto_list"].update([f"{produto[1]} - X: {produto[2]}, Y: {produto[3]}, Z: {produto[4]}, Data: {produto[5]}" for produto in produtos])


    elif event == 'Localizar Produto':
        filtro_nome = values["filtro_nome"]
        produtos_encontrados = localizar_produto(filtro_nome)
        main_window["produto_list"].update([f"{produto[1]} - X: {produto[2]}, Y: {produto[3]}, Z: {produto[4]}" for produto in produtos_encontrados])


    elif event == 'Exibir Produtos':
        produtos = exibir_produtos()
        main_window["produto_list"].update([f"{produto[1]} - X: {produto[2]}, Y: {produto[3]}, Z: {produto[4]}" for produto in produtos])

    elif event == 'Arduino':
        main_window.hide()  # Oculta a janela principal

        # JANELA DO ARDUINO
        arduino_window = sg.Window("Modo Arduino", arduino_layout())

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

            elif event == 'Localizar Produto':
                filtro_nome = values["filtro_nome"]
                produtos_encontrados = localizar_produto(filtro_nome)
                arduino_window["produto_list"].update([f"{produto[1]} - X: {produto[2]}, Y: {produto[3]}, Z: {produto[4]}" for produto in produtos_encontrados])
            # Outros eventos e códigos para a janela do Arduino

        arduino_window.close()  # Fecha a janela do Arduino
        main_window.un_hide()  # Exibe novamente a janela principal

if main_window:
    main_window.close()

if conn:
    conn.close()

main_window.close()