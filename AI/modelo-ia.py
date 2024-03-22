import PySimpleGUI as sg
import sqlite3
from PIL import Image, ImageTk
import io
import re
import cv2
import easyocr
import pytesseract
from easyocr import Reader
import pyocr
import pyocr.builders

# Configurando o caminho para o executável do Tesseract-OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Lista de palavras-chave para identificar o nome do medicamento
palavras_chave = [
    'abacavir', 'abiraterona', 'acetaminofeno', 'acetato de tocoferol', 'acetato de zinco', 'aciclovir', 'ácido ascórbico', 'ácido azelaico', 'ácido fólico', 'ácido fusídico', 'ácido glicólico', 
    'ácido pantotênico', 'ácido salicílico', 'ácido zoledrônico', 'acitretina', 'adapaleno', 'adrenalina', 'água', 'álcool', 'alendronato', 'alfacalcidol', 'alfentanila', 'alprazolam', 'amiodarona', 
    'amitriptilina', 'amlodipina', 'amoxicilina', 'anastrozol', 'andrógeno', 'aripiprazol', 'asenapina', 'aspirina', 'atazanavir', 'atenolol', 'atomoxetina', 'atorvastatina', 'azitromicina', 'bacitracina', 
    'baclofeno', 'benazepril', 'benzatropina', 'benzidamina', 'benzocaína', 'betacaroteno', 'betahistina', 'betametasona', 'bezafibrato', 'bicalutamida', 'bicarbonato de potássio', 'bimatoprosta', 'biotina', 
    'biperideno', 'bisoprolol', 'boldenona', 'borato de alumínio', 'borato de sódio', 'borato', 'bromazepam', 'brometo de ipratrópio', 'bromidrato de fenoterol', 'bromocriptina', 'bromoprida', 'budesonida', 
    'bumetanida', 'bupivacaína', 'bupropiona', 'buspirona', 'butenafina', 'cabergolina', 'calcitonina', 'calcitriol', 'canagliflozina', 'candesartana', 'captopril', 'carbamazepina', 'carbonato de cálcio', 
    'carbonato de ferro', 'carbonato de magnésio', 'carbonato', 'carisoprodol', 'carvedilol', 'cefalexina', 'ceftriaxona', 'celecoxibe', 'cetoconazol', 'cetoprofeno', 'cianocobalamina', 'ciclobenzaprina', 
    'ciclopirox', 'ciclosporina', 'cinarizina', 'ciprofloxacino', 'ciproterona', 'citalopram', 'citrato de cálcio', 'citrato', 'claritromicina', 'clomifeno', 'clomipramina', 'clonazepam', 'clonidina', 
    'clopidogrel', 'cloprostenol', 'clorazepato', 'cloreto de cetilpiridínio', 'cloreto de cromo', 'cloreto de flúor', 'cloreto de potássio', 'cloreto de sódio', 'cloridrato de benzidamina', 
    'cloridrato de fenilefrina', 'cloridrato de fexofenadina', 'cloridrato de piridoxina', 'cloridrato de pseudoefedrina', 'clormadinona', 'clorpromazina', 'clortalidona', 
    'clotrimazol', 'clozapina', 'codeína', 'colecalciferol', 'colesevelam', 'colutório', 'dapagliflozina', 'darunavir', 'denosumabe', 'desipramina', 'desloratadina', 'desogestrel', 'desvenlafaxina', 
    'dexametasona', 'dexmedetomidina', 'dexpantenol', 'dextroanfetamina', 'diazepam', 'dibucaina', 'diclofenaco', 'dicloridrato de cetirizina', 'difenidramina', 'digoxina', 'diltiazem', 'dimenidrinato', 
    'dipirona', 'dipirona monoidratada', 'dobutamina', 'domperidona', 'donepezila', 'dopamina', 'doramectina', 'dorflex', 'dostinex', 'doxazosina', 'doxiciclina', 'doxorrubicina', 'dronedarona', 'droperidol', 'drospirenona', 'dulaglutida', 
    'duloxetina', 'dutasterida', 'efavirenz', 'empagliflozina', 'enalapril', 'entecavir', 'enzalutamida', 'ergotamina', 'eritromicina', 'escitalopram', 'escopolamina', 'esomeprazol', 'espironolactona', 
    'estanozolol', 'estradiol', 'estrogênio', 'estrógeno', 'etilestradiol', 'etinilestradiol', 'etoricoxibe', 'etravirina', 'exemestano', 'exenatida', 'ezetimiba', 'felodipina', 'fenilefrina', 'fenitoína', 
    'fenobarbital', 'fenofibrato', 'fentanila', 'fexofenadina', 'fibrato', 'finasterida', 'flecainida', 'fluconazol', 'fludrocortisona', 'flunarizina', 'flunitrazepam', 'fluoreto de estanho', 'fluoreto de sódio', 
    'fluoxetina', 'flutamida', 'fluticasona', 'fluvastatina', 'follitropina', 'fosfato de clindamicina', 'fosfato de neomicina', 'fosfato de potássio', 'fosfato', 'fosinopril', 'fulvestranto', 'fumarato ferroso', 
    'furosemida', 'gabapentina', 'galantamina', 'gemfibrozil', 'gentamicina', 'gestodeno', 'glibenclamida', 'glicerina', 'glimepirida', 'gluconato de ferro', 'gluconato ferroso', 'gluconato', 
    'gonadotrofina coriônica', 'goserrelina', 'granisetrona', 'haloperidol', 'hidralazina', 'hidroclorotiazida', 'hidrocortisona', 'hidrogenocarbonato', 'hidroquinona', 'hidróxido de sódio', 
    'hormônio do crescimento', 'ibandronato', 'ibuprofeno', 'imipramina', 'imiquimode', 'indapamida', 'insulina aspart', 'insulina degludeca', 'insulina detemir', 'insulina glargina', 'insulina glulisina', 
    'insulina Lente', 'insulina lispro', 'insulina NPH', 'insulina regular', 'insulina Ultra Lente', 'insulina', 'iodeto de ferro', 'iodeto de potássio', 'iodeto de sódio', 'irbesartana', 'isoproterenol', 
    'isotretinoína', 'itraconazol', 'ivermectina', 'labetalol', 'lactato', 'lamivudina', 'lamotrigina', 'lansoprazol', 'latanoprosta', 'leflunomida', 'lercanidipina', 'letrozol', 
    'leuprorrelina', 'levetiracetam', 'levofloxacino', 'levoitiroxina', 'levomepromazina', 'levonorgestrel', 'levotiroxina', 'lidocaína', 'linagliptina', 'linestrenol', 'liraglutida', 'lisdexanfetamina', 
    'lisinopril', 'lopinavir', 'loratadina', 'lorazepam', 'losartana', 'loção', 'lurasidona', 'maleato de dimetindeno', 'maleato', 'mazindol', 'meclizina', 'medroxiprogesterona', 'melanina', 'melatonina', 
    'meloxicam', 'memantina', 'menotropina', 'meperidina', 'mesalazina', 'mesilato', 'metformina', 'metilfenidato', 'metilprednisolona', 'metiltestosterona', 'metoclopramida', 'metoprolol', 'metoxamina', 
    'metronidazol', 'miconazol', 'midazolam', 'miglitol', 'milnaciprano', 'milrinona', 'minoxidil', 'mirtazapina', 'modafinila', 'montelucaste', 'morfina', 'multivitamínico', 'mupirocina', 'nandrolona', 
    'naproxeno', 'naratriptana', 'nateglinida', 'nebivolol', 'neossulfamida', 'nesiritida', 'nicotinamida', 'nifedipina', 'nimesulida', 'nitazoxanida', 'nitrendipina', 'nitroglicerina', 'nitroprussiato', 
    'nomegestrol', 'noradrenalina', 'norelgestromina', 'noretisterona', 'nortriptilina', 'olanzapina', 'óleo', 'olmesartana', 'omeprazol', 'ondansetrona', 'orlistat', 'orotato', 'oxandrolona', 'oxazepam', 
    'oxcarbazepina', 'oxicodona', 'óxido de cromo', 'óxido de ferro', 'óxido de manganês', 'óxido de zinco', 'oximetazolina', 'paliperidona', 'pantenol', 'pantoprazol', 'paracetamol', 'parlodel', 'paroxetina', 
    'perfenazina', 'perindopril', 'peróxido de benzoíla', 'petidina', 'pioglitazona', 'piridoxina', 'piroxicam', 'pitavastatina', 'polidocanol', 'polietilenoglicol', 'polivitamínico', 'pravastatina', 
    'prazosina', 'prednisona', 'pregabalina', 'prilocaína', 'primidona', 'primobolan', 'procaína', 'progestágeno', 'progesterona', 'prometazina', 'propafenona', 'propilenoglicol', 'propionato', 'propofol', 
    'propranolol', 'quetamina', 'quetiapina', 'raloxifeno', 'raltegravir', 'ramelteon', 'ramipril', 'ranitidina', 'remifentanila', 'repaglinida', 'riboflavina', 'risedronato', 'risperidona', 'ritonavir', 
    'rituximabe', 'rivastigmina', 'rizatriptana', 'ropivacaína', 'rosiglitazona', 'rosuvastatina', 'salbutamol', 'salmeterol', 'saxagliptina', 'selegilina', 'semaglutida', 'sertralina', 'sibutramina', 
    'sinvastatina', 'sitagliptina', 'solução', 'sorbitol', 'sotalol', 'spironolactona', 'stavudina', 'sufentanila', 'sulfadiazina de prata', 'sulfametoxazol', 'sulfato de cobre', 'sulfato de ferro', 
    'sulfato de magnésio', 'sulfato de manganês', 'sulfato de polimixina B', 'sulfato de salbutamol', 'sulfato de zinco', 'sulfato ferroso', 'sulfato', 'sulfeto de selênio', 'sulpirida', 'sumatriptana', 
    'tacrolimo', 'tadalafila', 'tamoxifeno', 'tamsulosina', 'telmisartana', 'temazepam', 'tenofovir', 'teofilina', 'terazosina', 'terbinafina', 'terbutalina', 'teriparatida', 'testosterona em gel', 
    'testosterona injetável', 'testosterona', 'tetracaína', 'tetraciclina', 'tiamina', 'tibolona', 'tioconazol', 'tiotrópio', 'tizanidina', 'tocoferol', 'tolbutamida', 'tolcapona', 'tolterodina', 
    'topiramato', 'tramadol', 'trazodona', 'trembolona', 'tretinoína', 'trieste', 'trifluoperazina', 'trihexifenidilo', 'trimetoprima', 'triptorrelina', 'tris', 'trometamol', 'unguento', 'valaciclovir', 
    'valerato', 'valproato', 'valsartana', 'venlafaxina', 'verapami', 'verapamil', 'vitamina B1', 'vitamina B12', 'vitamina B2', 'vitamina B3', 'vitamina B6', 'vitamina C', 'vitamina D', 'vitamina D3', 
    'vitamina E', 'voriconazol', 'warfarina', 'zalcitabina', 'zaleplon', 'zidovudina', 'ziprasidona', 'zoledronato', 'zolmitriptana', 'zolpidem', 'zopiclona'
]

informacoes_extraidas = {'nome': None, 'quantidade': None, 'medida': None}

# Variável global para armazenar o último imagem_id selecionado
ultima_imagem_id = None

# Função para criar as tabelas no banco de dados se não existirem
def criar_tabelas(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS imagens (
            id INTEGER PRIMARY KEY,
            path TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY,
            nome_produto TEXT NOT NULL,
            quantidade TEXT NOT NULL,
            medida TEXT NOT NULL,
            imagem_id INTEGER,
            FOREIGN KEY (imagem_id) REFERENCES imagens(id)
        )
    ''')
    conn.commit()

# Função para inserir a imagem no banco de dados
def inserir_imagem(conn, path_imagem):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO imagens (path) VALUES (?)', (path_imagem,))
    conn.commit()
    global ultima_imagem_id
    ultima_imagem_id = cursor.lastrowid  # Obtém o ID da última imagem inserida

# Função para inserir o produto no banco de dados
def inserir_produto(conn, nome_produto, quantidade, medida, imagem_id):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO produtos (nome_produto, quantidade, medida, imagem_id) VALUES (?, ?, ?, ?)', (nome_produto, quantidade, medida, imagem_id))
    conn.commit()

# Função para obter o path da imagem do banco de dados
def obter_imagem(conn, imagem_id):
    cursor = conn.cursor()
    cursor.execute('SELECT path FROM imagens WHERE id = ?', (imagem_id,))
    path = cursor.fetchone()
    return path[0] if path else None

# Função para carregar a imagem e exibi-la na janela
def exibir_imagem(window_imagem, conn, imagem_id):
    path = obter_imagem(conn, imagem_id)
    if path:
        image = Image.open(path)
        image.thumbnail((400, 400))
        bio = io.BytesIO()
        image.save(bio, format="PNG")
        img_bytes = bio.getvalue()
        window_imagem['-IMAGE-'].update(data=img_bytes)

# Função para limpar os campos da segunda janela
def limpar_campos(window_adicionar):
    window_adicionar['-NOME-'].update('')
    window_adicionar['-QUANTIDADE-'].update('')
    window_adicionar['-MEDIDA-'].update('')

# Função para preprocessar a imagem
def preprocess_image(image):
    # Convertendo para escala de cinza
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Aplicando um filtro gaussiano para reduzir ruídos
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Binarização da imagem
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Unir linhas consecutivas
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 5))
    connected_lines = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    
    return connected_lines

# Função para redimensionar a imagem
def resize_image(image, width=None, height=None):
    if width is None and height is None:
        return image
    if width is None:
        aspect_ratio = height / float(image.shape[0])
        new_width = int(image.shape[1] * aspect_ratio)
        new_size = (new_width, height)
    else:
        aspect_ratio = width / float(image.shape[1])
        new_height = int(image.shape[0] * aspect_ratio)
        new_size = (width, new_height)
        
    resized = cv2.resize(image, new_size)
    return resized

# Função para realizar OCR com easyocr
def ocr_with_easyocr(image):
    reader = easyocr.Reader(['pt'])
    results = reader.readtext(image)
    extracted_text = [result[1] for result in results]
    return " ".join(extracted_text)

def extrair_texto_imagem_tentativa_1(window_adicionar, conn):
    global ultima_imagem_id
    path = obter_imagem(conn, ultima_imagem_id)
    if path:
        image = cv2.imread(path)

        # Chamando a função para OCR com easyocr
        texto = ocr_with_easyocr(image)

        limpar_campos(window_adicionar)

        nomes_medicamentos = encontrar_nome_medicamento(texto)

        if len(nomes_medicamentos) > 1:
            # Se houver mais de uma correspondência, abrir uma janela para escolha
            escolha_layout = [
                [sg.Text("Escolha o medicamento:")],
                [sg.Listbox(values=nomes_medicamentos, size=(30, len(nomes_medicamentos)), key="-MEDICAMENTO-")],
                [sg.Button("OK")]
            ]
            escolha_window = sg.Window("Escolha o Medicamento", escolha_layout)

            while True:
                event_escolha, values_escolha = escolha_window.read()

                if event_escolha == sg.WIN_CLOSED or event_escolha == "OK":
                    break

            escolha_window.close()

            if values_escolha["-MEDICAMENTO-"]:
                nome_medicamento = values_escolha["-MEDICAMENTO-"][0]
            else:
                sg.popup_error("Selecione um medicamento.")
                return

        elif len(nomes_medicamentos) == 1:
            # Se houver apenas uma correspondência, usar essa correspondência
            nome_medicamento = nomes_medicamentos[0]

        else:
            sg.popup_error("Nenhum medicamento encontrado.")
            return

        quantidade, medida = encontrar_quantidade_e_medida(texto)

        if quantidade == "Quantidade não encontrada." or medida == "Medida não encontrada.":
            extrair_texto_imagem_tentativa_2(window_adicionar, conn)
        else:
            # Exibir as informações extraídas
            sg.popup("Informações Extraídas:",
                    "Nome do Medicamento: " + nome_medicamento,
                    "Quantidade: " + quantidade,
                    "Medida: " + medida)

            # Preencher os inputs da segunda janela com as informações extraídas
            window_adicionar['-NOME-'].update(nome_medicamento)
            window_adicionar['-QUANTIDADE-'].update(quantidade)
            window_adicionar['-MEDIDA-'].update(medida)
    else:
        sg.popup("Nome do medicamento não encontrado.", "Informação não encontrada.")
        return None
    
def extrair_texto_imagem_tentativa_2(window_adicionar, conn):
    global ultima_imagem_id
    path = obter_imagem(conn, ultima_imagem_id)
    if path:
        image = Image.open(path)
        texto = pytesseract.image_to_string(image)

        # Extrair nome do medicamento, quantidade e medida
        nomes_medicamentos = encontrar_nome_medicamento(texto)

        if len(nomes_medicamentos) > 1:
            # Se houver mais de uma correspondência, abrir uma janela para escolha
            escolha_layout = [
                [sg.Text("Escolha o medicamento:")],
                [sg.Listbox(values=nomes_medicamentos, size=(30, len(nomes_medicamentos)), key="-MEDICAMENTO-")],
                [sg.Button("OK")]
            ]
            escolha_window = sg.Window("Escolha o Medicamento", escolha_layout)

            while True:
                event_escolha, values_escolha = escolha_window.read()

                if event_escolha == sg.WIN_CLOSED or event_escolha == "OK":
                    break

            escolha_window.close()

            if values_escolha["-MEDICAMENTO-"]:
                nome_medicamento = values_escolha["-MEDICAMENTO-"][0]
            else:
                sg.popup_error("Selecione um medicamento.")
                return

        elif len(nomes_medicamentos) == 1:
            # Se houver apenas uma correspondência, usar essa correspondência
            nome_medicamento = nomes_medicamentos[0]

        else:
            sg.popup_error("Nenhum medicamento encontrado.")
            return

        quantidade, medida = encontrar_quantidade_e_medida(texto)

        if quantidade == "Quantidade não encontrada." or medida == "Medida não encontrada.":
            extrair_texto_imagem_tentativa_3(window_adicionar, conn)
        else:
            # Exibir as informações extraídas
            sg.popup("Informações Extraídas:",
                    "Nome do Medicamento: " + nome_medicamento,
                    "Quantidade: " + quantidade,
                    "Medida: " + medida)

            # Preencher os inputs da segunda janela com as informações extraídas
            window_adicionar['-NOME-'].update(nome_medicamento)
            window_adicionar['-QUANTIDADE-'].update(quantidade)
            window_adicionar['-MEDIDA-'].update(medida)
    else:
        sg.popup("Nome do medicamento não encontrado.", "Informação não encontrada.")
        return None

def extrair_texto_imagem_tentativa_3(window_adicionar, conn):
    global ultima_imagem_id
    path = obter_imagem(conn, ultima_imagem_id)
    
    if path:
        # Inicialize o OCR com o Tesseract
        tools = pyocr.get_available_tools()
        if len(tools) == 0:
            sg.popup_error("Nenhum motor OCR disponível. Certifique-se de ter o Tesseract-OCR instalado.")
            return None

        tool = tools[0]  # Use o primeiro motor OCR disponível (normalmente Tesseract)

        # Abra a imagem com o Pillow
        with Image.open(path) as img:
            # Use o OCR para extrair o texto
            texto = tool.image_to_string(img, builder=pyocr.builders.TextBuilder())

            limpar_campos(window_adicionar)

            # Restante do código permanece inalterado
            nomes_medicamentos = encontrar_nome_medicamento(texto)

            if len(nomes_medicamentos) > 1:
                # Se houver mais de uma correspondência, abrir uma janela para escolha
                escolha_layout = [
                    [sg.Text("Escolha o medicamento:")],
                    [sg.Listbox(values=nomes_medicamentos, size=(30, len(nomes_medicamentos)), key="-MEDICAMENTO-")],
                    [sg.Button("OK")]
                ]
                escolha_window = sg.Window("Escolha o Medicamento", escolha_layout)

                while True:
                    event_escolha, values_escolha = escolha_window.read()

                    if event_escolha == sg.WIN_CLOSED or event_escolha == "OK":
                        break

                escolha_window.close()

                if values_escolha["-MEDICAMENTO-"]:
                    nome_medicamento = values_escolha["-MEDICAMENTO-"][0]
                else:
                    sg.popup_error("Selecione um medicamento.")
                    return

            elif len(nomes_medicamentos) == 1:
                # Se houver apenas uma correspondência, usar essa correspondência
                nome_medicamento = nomes_medicamentos[0]

            else:
                sg.popup_error("Nenhum medicamento encontrado.")
                return

            quantidade, medida = encontrar_quantidade_e_medida(texto)

            # Exibir as informações extraídas
            sg.popup("Informações Extraídas:",
                     "Nome do Medicamento: " + nome_medicamento,
                     "Quantidade: " + quantidade,
                     "Medida: " + medida)

            # Preencher os inputs da segunda janela com as informações extraídas
            window_adicionar['-NOME-'].update(nome_medicamento)
            window_adicionar['-QUANTIDADE-'].update(quantidade)
            window_adicionar['-MEDIDA-'].update(medida)

    else:
        sg.popup("Nome do medicamento não encontrado.", "Informação não encontrada.")
        return None

# Função para encontrar o nome do medicamento
def encontrar_nome_medicamento(texto):
    resultados = []
    
    for palavra_chave in palavras_chave:
        palavras = re.split(r'[\s\n]+', palavra_chave.lower())
        encontradas = all(p.lower() in texto.lower() for p in palavras)
        if encontradas:
            resultados.append(palavra_chave.capitalize())
    
    return resultados if resultados else ["Medicamento não encontrado."]


# CAPTURA A QUANTIDADE JUNTO COM A MEDIDA E DIVIDE 

# Lista de unidades de medida permitidas
palavras_medida = ["g", "mg", "mmg", "mcg", "L", "ml", "mml", "u"]

def encontrar_quantidade_e_medida(texto):
    # Expressão regular para encontrar a quantidade e medida
    padrao = r"(\d+\s*(" + "|".join(palavras_medida) + r")\b)"
    resultado = re.findall(padrao, texto, flags=re.IGNORECASE)
    if resultado:
        # Extrair a primeira ocorrência de quantidade e medida
        quantidade_medida = resultado[0][0]
        # Dividir a quantidade da medida
        partes = re.split(r"\s*(" + "|".join(palavras_medida) + r")\b", quantidade_medida, flags=re.IGNORECASE)
        quantidade = partes[0].strip() if len(partes) > 0 else "Quantidade não encontrada"
        medida = partes[1].strip().lower() if len(partes) > 1 else "Medida não encontrada"
        return quantidade, medida
    else:
        return "Quantidade não encontrada.", "Medida não encontrada."

# Layout da primeira janela
layout_principal = [
    [sg.Button("Image Upload", key='-UPLOAD-'), sg.Button("Visualizar Imagem", key='-VISUALIZAR-', disabled=True), sg.Button("Extrair Texto", key='-EXTRAIR-', disabled=True), sg.Button("Close Window", key="close_window")]
]

# Criando a conexão com o banco de dados
conn = sqlite3.connect('implementando_ia.db')
criar_tabelas(conn)

# Criando a primeira janela
window_principal = sg.Window("Principal", layout_principal)

# Loop principal
while True:
    event, values = window_principal.read()

    if event == sg.WIN_CLOSED or event == "close_window":
        break
    elif event == '-UPLOAD-':
        filepath = sg.popup_get_file("Selecione uma imagem")
        if filepath:
            inserir_imagem(conn, filepath)
            window_principal['-VISUALIZAR-'].update(disabled=False)
            window_principal['-EXTRAIR-'].update(disabled=False)
    elif event == '-VISUALIZAR-':
        imagem_id = ultima_imagem_id
        if imagem_id:
            window_imagem = sg.Window("Visualizar Imagem", [[sg.Image(key='-IMAGE-')]], finalize=True)
            exibir_imagem(window_imagem, conn, imagem_id)
            event_imagem, values_imagem = window_imagem.read()
            window_imagem.close()
    if event == '-EXTRAIR-':
        if ultima_imagem_id:
            # Abrir a segunda janela de adicionar produto com as informações extraídas
            layout_adicionar = [
                [sg.Text('Nome do Produto:'), sg.InputText(key='-NOME-', size=(30, 1))],
                [sg.Text('Quantidade:'), sg.InputText(key='-QUANTIDADE-', size=(30, 1))],
                [sg.Text('Medida:'), sg.InputText(key='-MEDIDA-', size=(30, 1))],
                [sg.Button('Adicionar')]
            ]
            window_adicionar = sg.Window("Adicionar Produto", layout_adicionar, finalize=True)

            # Tentativa de extrair e preencher as informações na segunda janela
            extrair_texto_imagem_tentativa_1(window_adicionar, conn)

            # Loop da segunda janela de adicionar produto
            while True:
                event_adicionar, values_adicionar = window_adicionar.read()

                if event_adicionar == sg.WIN_CLOSED:
                    break
                elif event_adicionar == 'Adicionar':
                    if values_adicionar['-NOME-'] and values_adicionar['-QUANTIDADE-'] and values_adicionar['-MEDIDA-']:
                        inserir_produto(conn, values_adicionar['-NOME-'], values_adicionar['-QUANTIDADE-'], values_adicionar['-MEDIDA-'], ultima_imagem_id)
                        sg.popup("Produto adicionado com sucesso!")
                        
                        # Exibir as informações extraídas na janela de adição
                        window_adicionar['-NOME-'].update(informacoes_extraidas['nome'])
                        window_adicionar['-QUANTIDADE-'].update(informacoes_extraidas['quantidade'])
                        window_adicionar['-MEDIDA-'].update(informacoes_extraidas['medida'])
                        
                        break
                    else:
                        sg.popup_error("Por favor, preencha todas as informações do medicamento.")


# Fechando as janelas ao sair dos loops
window_principal.close()
# Fechando a conexão com o banco de dados ao final do programa
conn.close()



# preprocess imagem fnciont

#resize image funciont