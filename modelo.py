import PySimpleGUI as sg
import sqlite3
from PyPDF2 import PdfReader
from io import BytesIO
import os

# Conecta ao banco de dados SQLite (cria o banco se não existir)
conn = sqlite3.connect('banco-de-dados-pdf.db')
cursor = conn.cursor()

# Cria uma tabela se não existir
cursor.execute('''
    CREATE TABLE IF NOT EXISTS banco_de_dados_pdf (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        pdf BLOB
    )
''')

# Obtém todos os nomes de PDFs no banco de dados
cursor.execute('SELECT nome FROM banco_de_dados_pdf')
pdf_names = [row[0] for row in cursor.fetchall()]

# Fecha a conexão com o banco de dados
conn.close()

# Exibir a janela de diálogo para selecionar um arquivo PDF
pdf_path = sg.popup_get_file('Selecione um PDF', file_types=(("PDF Files", "*.pdf"),))

if pdf_path:
    if os.path.exists(pdf_path) and os.path.isfile(pdf_path) and pdf_path.lower().endswith(".pdf"):
        # Converte o PDF para bytes
        with open(pdf_path, 'rb') as pdf_file:
            pdf_data = pdf_file.read()

        # Conecta ao banco de dados SQLite (cria o banco se não existir)
        conn = sqlite3.connect('banco-de-dados-pdf.db')
        cursor = conn.cursor()

        # Cria uma tabela se não existir
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS banco_de_dados_pdf (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                pdf BLOB
            )
        ''')

        # Obtém o nome do arquivo
        pdf_name = os.path.basename(pdf_path)

        # Insere o PDF na tabela
        cursor.execute('INSERT INTO banco_de_dados_pdf (nome, pdf) VALUES (?, ?)', (pdf_name, sqlite3.Binary(pdf_data)))

        # Commit das alterações no banco de dados
        conn.commit()

        # Recupera o PDF do banco de dados antes de fechar a conexão
        cursor.execute('SELECT nome, pdf FROM banco_de_dados_pdf ORDER BY id DESC LIMIT 1')
        fetched_data = cursor.fetchone()
        fetched_pdf_name, fetched_pdf_data = fetched_data[0], fetched_data[1]

        # Atualiza a lista de nomes de PDFs
        cursor.execute('SELECT nome FROM banco_de_dados_pdf')
        pdf_names = [row[0] for row in cursor.fetchall()]

        # Fecha a conexão com o banco de dados
        conn.close()

        # Converte os dados do PDF de volta para o formato de PDF
        pdf_reader = PdfReader(BytesIO(fetched_pdf_data))

        # Crie a janela fora do bloco principal
        layout = [
            [sg.Text('Escolha um PDF para visualizar')],
            [sg.Listbox(pdf_names, size=(50, len(pdf_names)), key='-PDF-List-', enable_events=True)],
            [sg.Text('Pré-visualização do PDF')],
            [sg.Image(key='-PDF-', size=(300, 300), pad=(0, 0))],
            [sg.Text('', key='-PDF-Name-', size=(30, 1))],
            [sg.Button('Abrir PDF Completo'), sg.Button('Fechar')]
        ]

        window = sg.Window('Visualizador de PDF', layout, finalize=True)        
    else:
        print(f'O arquivo "{pdf_path}" não é um formato de PDF suportado.')
else:
    print('Nenhum arquivo PDF selecionado')


# Exiba o PDF selecionado
selected_pdf_index = None

while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED or event == 'Fechar':
        break
    elif event == '-PDF-List-' and values['-PDF-List-']:
        # Atualiza o índice do PDF selecionado
        selected_pdf_name = values['-PDF-List-'][0]

        # Obtém o índice do PDF selecionado
        selected_pdf_index = pdf_names.index(selected_pdf_name)

        # Obtém o PDF do banco de dados com base no índice selecionado
        conn = sqlite3.connect('banco-de-dados-pdf.db')
        cursor = conn.cursor()
        cursor.execute('SELECT nome, pdf FROM banco_de_dados_pdf WHERE nome = ?', (selected_pdf_name,))

        fetched_data = cursor.fetchone()
        fetched_pdf_name, fetched_pdf_data = fetched_data[0], fetched_data[1]
        conn.close()

        # Converte os dados do PDF de volta para o formato de PDF
        pdf_reader = PdfReader(BytesIO(fetched_pdf_data))

        # Atualiza a imagem e o nome do PDF na layout
        window['-PDF-'].update(data='')  # Atualize com a imagem da página do PDF
        window['-PDF-Name-'].update(value=f'Nome: {fetched_pdf_name}')



    elif event == 'Abrir PDF Completo' and selected_pdf_index is not None:
        # Salve o PDF em um arquivo temporário e abra-o
        temp_pdf_path = 'temp_pdf.pdf'
        with open(temp_pdf_path, 'wb') as temp_pdf_file:
            temp_pdf_file.write(fetched_pdf_data)

        os.system(temp_pdf_path)  # Abre o PDF no visualizador padrão

# Feche a janela ao sair do loop
window.close()