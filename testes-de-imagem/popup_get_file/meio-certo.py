import PySimpleGUI as sg
import os
import shutil
from PIL import Image, ImageTk

# Exibir a janela de diálogo para selecionar um arquivo
imagem_path = sg.popup_get_file('Selecione uma imagem', file_types=(("Imagens", "*.png;*.jpg;*.jpeg"),))

# Exiba a Imagem selecionada
if imagem_path:
    if os.path.exists(imagem_path) and os.path.isfile(imagem_path):
        # Check if the file is a valid image file
        valid_image_extensions = {".png", ".jpg", ".jpeg"}
        _, file_extension = os.path.splitext(imagem_path)
        if file_extension.lower() in valid_image_extensions:
            # Move the image to the project's directory
            project_directory = os.path.dirname(os.path.abspath(__file__))
            new_image_path = os.path.join(project_directory, os.path.basename(imagem_path))

            shutil.copy(imagem_path, new_image_path)  # Copy the file to the project directory

            # Defina o layout da janela
            layout = [
                [sg.Canvas(key='-CANVAS-', background_color='white', size=(300, 300), pad=(0, 0),)],
                [sg.Button('Fechar')]
            ]

            # Crie a janela
            window = sg.Window('Visualizador de Imagem', layout, finalize=True)

            # Obtenha o elemento Canvas e o canvas tkinter
            canvas_elem = window['-CANVAS-']
            canvas = canvas_elem.Widget

            # Abra a imagem usando PIL e converta para Tkinter.PhotoImage
            pil_image = Image.open(new_image_path)
            tk_image = ImageTk.PhotoImage(pil_image)

            # Adicione a imagem ao canvas
            canvas.create_image(0, 0, anchor='nw', image=tk_image)

            # Loop de eventos para manter a janela aberta
            while True:
                event, values = window.read()

                # Verifique se o botão Fechar foi pressionado ou se a janela foi fechada
                if event == sg.WINDOW_CLOSED or event == 'Fechar':
                    break

            # Feche a janela ao sair do loop
            window.close()
        else:
            print(f'O arquivo "{imagem_path}" não é um formato de imagem suportado.')
    else:
        print(f'O arquivo "{imagem_path}" não existe ou não é um arquivo regular.')
else:
    print('Nenhum arquivo selecionado')
