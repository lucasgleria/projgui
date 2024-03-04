import PySimpleGUI as sg
import sqlite3
from PIL import Image, ImageTk
import io
import pytesseract
import re

# Configurando o caminho para o executável do Tesseract-OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Lista de palavras-chave para identificar o nome do medicamento
palavras_chave = [
    "acetaminofeno", "dipirona", "ibuprofeno", "paracetamol", "aspirina", "dorflex",
    "amoxicilina", "diclofenaco", "omeprazol", "dexametasona", "ranitidina", "metformina",
    "loratadina", "cetoprofeno", "betametasona", "captopril", "losartana", "atenolol",
    "ciclosporina", "tramadol", "claritromicina", "fluoxetina", "sertralina", "furosemida",
    "sinvastatina", "rosuvastatina", "pantoprazol", "clonazepam", "venlafaxina", "escitalopram",
    "risperidona", "insulina", "warfarina", "metronidazol", "levotiroxina", "fexofenadina",
    "metoclopramida", "valproato", "bromoprida", "cefalexina", "fluconazol", "paroxetina",
    "levoitiroxina", "ramipril", "carbamazepina", "alprazolam", "ondansetrona", "salbutamol",
    "citalopram", "ciprofloxacino", "duloxetina", "gabapentina", "pregabalina", "quetiapina",
    "metilprednisolona", "piroxicam", "terbinafina", "tiotrópio", "latanoprosta", "desogestrel",
    "tamoxifeno", "bimatoprosta", "neossulfamida", "clotrimazol", "propionato", "terbutalina",
    "polivitamínico", "omeprazol", "claritromicina", "lansoprazol", "amoxicilina", "tetraciclina",
    "eritromicina", "itraconazol", "miconazol", "sulfametoxazol", "trimetoprima", "cetoconazol",
    "fluconazol", "mirtazapina", "ciclobenzaprina", "naproxeno", "hidroclorotiazida", "doramectina",
    "ivermectina", "nitazoxanida", "teofilina", "atenolol", "propranolol", "indapamida", "candesartana",
    "hidroclorotiazida", "valsartana", "bisoprolol", "losartana", "flunarizina", "fenofibrato", "pitavastatina",
    "bezafibrato", "atorvastatina", "tibolona", "desogestrel", "levonorgestrel", "etinilestradiol", "drospirenona",
    "clormadinona", "acetato", "dienogest", "ulipristal", "anticoncepcional", "noretisterona", "ciproterona",
    "estriol", "estradiol", "tibolona", "esteroides", "conjugados", "progesterona", "testosterona", "decanoato",
    "vitamina", "suplemento"
]

# Lista de palavras-chave para identificar a quantidade
palavras_quantidade = ["g", "mg", "mmg", "L", "ml", "mml", "u"]

# Função para criar a tabela no banco de dados se não existir
def criar_tabela():
    conn = sqlite3.connect('imagens.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS imagens (
            id INTEGER PRIMARY KEY,
            path TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Função para inserir o path da imagem no banco de dados
def inserir_imagem(path):
    conn = sqlite3.connect('imagens.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO imagens (path) VALUES (?)', (path,))
    conn.commit()
    conn.close()

# Função para obter o path da imagem do banco de dados
def obter_imagem():
    conn = sqlite3.connect('imagens.db')
    cursor = conn.cursor()
    cursor.execute('SELECT path FROM imagens ORDER BY id DESC LIMIT 1')
    path = cursor.fetchone()
    conn.close()
    return path[0] if path else None

# Função para carregar a imagem e exibi-la na janela
def exibir_imagem():
    path = obter_imagem()
    if path:
        image = Image.open(path)
        image.thumbnail((400, 400))
        bio = io.BytesIO()
        image.save(bio, format="PNG")
        img_bytes = bio.getvalue()
        window['-IMAGE-'].update(data=img_bytes)

# Função para processar a imagem e extrair o texto
def extrair_texto_imagem():
    path = obter_imagem()
    if path:
        image = Image.open(path)
        texto = pytesseract.image_to_string(image)

        # Extrair nome do medicamento, quantidade e medida
        nome_medicamento = encontrar_nome_medicamento(texto)
        quantidade, medida = encontrar_quantidade_e_medida(texto)

        # Exibir as informações extraídas
        print("Nome do Medicamento:", nome_medicamento)
        print("Quantidade:", quantidade)
        print("Medida:", medida)

def encontrar_nome_medicamento(texto):
    # Expressão regular para encontrar o nome do medicamento
    padrao = r"\b(" + "|".join(palavras_chave) + r")\b"
    resultado = re.search(padrao, texto, flags=re.IGNORECASE)
    if resultado:
        return resultado.group(0).capitalize()  # Retorna o primeiro nome de medicamento encontrado
    else:
        return "Medicamento não encontrado."

def encontrar_quantidade_e_medida(texto):
    # Expressão regular para encontrar a quantidade e medida
    padrao = r"(\d+\s*(" + "|".join(palavras_quantidade) + r")\b)"
    resultado = re.findall(padrao, texto, flags=re.IGNORECASE)
    if resultado:
        # Extrair a primeira ocorrência de quantidade e medida
        quantidade_medida = resultado[0][0]
        # Dividir a quantidade da medida
        partes = re.split(r"\s*(" + "|".join(palavras_quantidade) + r")\b", quantidade_medida, flags=re.IGNORECASE)
        quantidade = partes[0].strip() if len(partes) > 0 else "Quantidade não encontrada"
        medida = partes[1].strip().lower() if len(partes) > 1 else "Medida não encontrada"
        return quantidade, medida
    else:
        return "Quantidade não encontrada.", "Medida não encontrada."



# Layout da janela principal
layout = [
    [sg.Button("Image Upload"), sg.Button("Visualizar Imagem"), sg.Button("Extrair Texto")],
    [sg.Image(key='-IMAGE-')],
]

# Criando a janela
window = sg.Window("Upload de Imagem", layout)

# Criando a tabela no banco de dados
criar_tabela()

# Loop de eventos da janela
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break
    elif event == "Image Upload":
        filepath = sg.popup_get_file("Selecione uma imagem")
        if filepath:
            inserir_imagem(filepath)
    elif event == "Visualizar Imagem":
        exibir_imagem()
    elif event == "Extrair Texto":
        extrair_texto_imagem()

# Fechando a janela ao sair do loop
window.close()