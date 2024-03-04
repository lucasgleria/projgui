import PySimpleGUI as sg
import sqlite3
import fitz  # PyMuPDF

# Função para criar a tabela no banco de dados
def create_table():
    conn = sqlite3.connect('pdf_viewer.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pdfs (
            id INTEGER PRIMARY KEY,
            pdf_path TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Função para inserir o caminho do PDF no banco de dados
def insert_pdf(pdf_path):
    conn = sqlite3.connect('pdf_viewer.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO pdfs (pdf_path)
        VALUES (?)
    ''', (pdf_path,))
    conn.commit()
    conn.close()

# Função para obter o caminho do PDF do banco de dados
def get_pdf_path():
    conn = sqlite3.connect('pdf_viewer.db')
    cursor = conn.cursor()
    cursor.execute('SELECT pdf_path FROM pdfs ORDER BY id DESC LIMIT 1')
    pdf_path = cursor.fetchone()
    conn.close()
    if pdf_path:
        return pdf_path[0]
    else:
        return None

# Janela para adicionar o PDF
def add_pdf_window():
    layout = [
        [sg.Text('Selecione o arquivo PDF para adicionar:')],
        [sg.Input(key='-FILE-'), sg.FileBrowse()],
        [sg.Button('Adicionar'), sg.Button('Cancelar')]
    ]

    window = sg.Window('Adicionar PDF', layout)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == 'Cancelar':
            break
        elif event == 'Adicionar':
            pdf_file = values['-FILE-']
            if pdf_file:
                insert_pdf(pdf_file)
                sg.popup('PDF Adicionado com sucesso!')
            else:
                sg.popup('Por favor, selecione um arquivo PDF.')

    window.close()

# Janela para exibir o PDF
def view_pdf_window(pdf_path):
    pdf_document = fitz.open(pdf_path)
    num_pages = pdf_document.page_count

    layout = [
        [sg.Text(f'Página 1 de {num_pages}')],
        [sg.Image(key='-IMAGE-')],
        [sg.Button('Anterior'), sg.Button('Próxima'), sg.Button('Fechar')]
    ]

    window = sg.Window('Visualizar PDF', layout, finalize=True)
    image_elem = window['-IMAGE-']

    page_num = 0
    display_page(image_elem, pdf_document, page_num)

    while True:
        event, _ = window.read()

        if event == sg.WINDOW_CLOSED or event == 'Fechar':
            break
        elif event == 'Próxima' and page_num < num_pages - 1:
            page_num += 1
            display_page(image_elem, pdf_document, page_num)
        elif event == 'Anterior' and page_num > 0:
            page_num -= 1
            display_page(image_elem, pdf_document, page_num)

    pdf_document.close()
    window.close()

def display_page(image_elem, pdf_document, page_num):
    page = pdf_document[page_num]
    image_bytes = page.get_pixmap().tobytes()
    image_elem.update(data=image_bytes)

# Função principal
def main():
    create_table()

    menu_layout = [
        [sg.Button('Adicionar PDF')],
        [sg.Button('Visualizar PDF')]
    ]

    menu_window = sg.Window('PDF Viewer', menu_layout)

    while True:
        event, _ = menu_window.read()

        if event == sg.WINDOW_CLOSED:
            break
        elif event == 'Adicionar PDF':
            add_pdf_window()
        elif event == 'Visualizar PDF':
            pdf_path = get_pdf_path()
            if pdf_path:
                view_pdf_window(pdf_path)
            else:
                sg.popup('Nenhum PDF encontrado. Por favor, adicione um PDF primeiro.')

    menu_window.close()

if __name__ == '__main__':
    main()
