import serial
import PySimpleGUI as sg
import mysql.connector

# Configurações do banco de dados MySQL
db_config = {
    'user': 'seu_usuario',
    'password': 'sua_senha',
    'host': 'localhost',
    'database': 'seu_banco_de_dados'
}

# Função para adicionar um novo produto ao banco de dados
def adicionar_produto(nome, eixox, eixoy, eixoz):
    # Conectando ao banco de dados
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Inserindo o novo produto
    query = "INSERT INTO produtos (nome, eixox, eixoy, eixoz) VALUES (%s, %s, %s, %s)"
    data = (nome, eixox, eixoy, eixoz)
    cursor.execute(query, data)

    # Commit das mudanças e fechamento da conexão
    connection.commit()
    cursor.close()
    connection.close()

# Função para localizar produtos no banco de dados
def localizar_produto(valor):
    # Conectando ao banco de dados
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Buscando produtos com base no valor
    query = "SELECT * FROM produtos WHERE nome LIKE %s"
    data = ('%' + valor + '%',)
    cursor.execute(query, data)
    results = cursor.fetchall()

    # Fechamento da conexão
    cursor.close()
    connection.close()

    return results

# Função para exibir todos os produtos do banco de dados
def exibir_produtos():
    # Conectando ao banco de dados
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Buscando todos os produtos
    query = "SELECT * FROM produtos"
    cursor.execute(query)
    results = cursor.fetchall()

    # Fechamento da conexão
    cursor.close()
    connection.close()

    return results

# Função para iniciar a comunicação com o Arduino
def iniciar_comunicacao_arduino(porta):
    ser = serial.Serial(porta, baudrate=9600, timeout=1)
    return ser

# Interface gráfica com PySimpleGUI
layout = [
    [sg.Text('Nome:'), sg.InputText(key='nome')],
    [sg.Text('EIXOX:'), sg.InputText(key='eixox')],
    [sg.Text('EIXOY:'), sg.InputText(key='eixoy')],
    [sg.Text('EIXOZ:'), sg.InputText(key='eixoz')],
    [sg.Button('Adicionar Produto')],
    [sg.Text('Buscar Produto:'), sg.InputText(key='busca_valor'), sg.Button('Localizar')],
    [sg.Listbox(values=[], size=(40, 10), key='resultado')],
    [sg.Button('Exibir Produtos')],
    [sg.Button('Sair')]
]

window = sg.Window('Software de Estoque', layout)

# Loop principal da interface
arduino_port = 'COM5'
ser = iniciar_comunicacao_arduino(arduino_port)

while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED or event == 'Sair':
        break
    elif event == 'Adicionar Produto':
        adicionar_produto(values['nome'], values['eixox'], values['eixoy'], values['eixoz'])
    elif event == 'Localizar':
        busca_valor = values['busca_valor']
        resultados = localizar_produto(busca_valor)
        window['resultado'].update(resultados)
    elif event == 'Exibir Produtos':
        produtos = exibir_produtos()
        window['resultado'].update(produtos)

window.close()
ser.close()