import PySimpleGUI as sg
import sqlite3
from PIL import Image, ImageTk
from io import BytesIO
import os

# Exibir a janela de diálogo para selecionar um arquivo
imagem_path = sg.popup_get_file('Selecione uma imagem', file_types=(("Imagens", "*.png;*.jpg;*.jpeg"),))

# Crie a janela fora do bloco principal
layout = [
    [sg.Image(key='-IMAGE-', size=(300, 300), pad=(0, 0),)],
    [sg.Button('Fechar')]
]

window = sg.Window('Visualizador de Imagem', layout, finalize=True)

# Exiba a Imagem selecionada
if imagem_path:
    if os.path.exists(imagem_path) and os.path.isfile(imagem_path):
        # Check if the file is a valid image file
        valid_image_extensions = {".png", ".jpg", ".jpeg"}
        _, file_extension = os.path.splitext(imagem_path)
        if file_extension.lower() in valid_image_extensions:
            # Converte a imagem para bytes
            with open(imagem_path, 'rb') as image_file:
                image_data = image_file.read()

            # Conecta ao banco de dados SQLite (cria o banco se não existir)
            conn = sqlite3.connect('imagens.db')
            cursor = conn.cursor()

            # Cria uma tabela se não existir
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS imagens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    imagem BLOB
                )
            ''')

            # Insere a imagem na tabela
            cursor.execute('INSERT INTO imagens (imagem) VALUES (?)', (sqlite3.Binary(image_data),))
            conn.commit()

            # Recupera a imagem do banco de dados
            cursor.execute('SELECT imagem FROM imagens ORDER BY id DESC LIMIT 1')
            fetched_image_data = cursor.fetchone()[0]

            # Converte os dados da imagem de volta para o formato de imagem
            pil_image = Image.open(BytesIO(fetched_image_data))

            # Redimensiona a imagem para 300x300 pixels
            pil_image = pil_image.resize((300, 300), Image.ANTIALIAS if hasattr(Image, 'ANTIALIAS') else Image.LANCZOS)

            # Converte a imagem para o formato suportado pelo PySimpleGUI
            tk_image = ImageTk.PhotoImage(pil_image)

            # Atualiza a imagem no layout
            window['-IMAGE-'].update(data=tk_image)

            # Loop de eventos para manter a janela aberta
            while True:
                event, values = window.read()

                # Verifique se o botão Fechar foi pressionado ou se a janela foi fechada
                if event == sg.WINDOW_CLOSED or event == 'Fechar':
                    break

            # Feche a janela ao sair do loop
            window.close()

            # Fecha a conexão com o banco de dados
            conn.close()
        else:
            print(f'O arquivo "{imagem_path}" não é um formato de imagem suportado.')
    else:
        print(f'O arquivo "{imagem_path}" não existe ou não é um arquivo regular.')
else:
    print('Nenhum arquivo selecionado')
