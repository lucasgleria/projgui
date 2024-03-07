import PySimpleGUI as sg
import sqlite3
from PIL import Image, ImageTk
import io
import re
import cv2
import easyocr
import pytesseract

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
    "bezafibrato", "atorvastatina", "tibolona", "desogestrel", "levonorgestrel", "gestodeno", "drospirenona",
    "etinilestradiol", "clormadinona", "medroxiprogesterona", "progesterona", "zolpidem", "buspirona",
    "zopiclona", "clonazepam", "risperidona", "quetiapina", "aripiprazol", "olanzapina", "trazodona",
    "venlafaxina", "mirtazapina", "fluoxetina", "paroxetina", "citalopram", "sertralina", "amitriptilina",
    "nortriptilina", "desvenlafaxina", "bupropiona", "duloxetina", "milnaciprano", "bromazepam", "lorazepam",
    "clorazepato", "alprazolam", "oxazepam", "temazepam", "diazepam", "gabapentina", "pregabalina",
    "ciclobenzaprina", "carisoprodol", "tizanidina", "diclofenaco", "ibuprofeno", "naproxeno",
    "celecoxibe", "etoricoxibe", "meloxicam", "codeína", "fentanila", "morfina", "oxicodona",
    "tramadol", "gabapentina", "pregabalina", "clonidina", "nortriptilina", "amitriptilina",
    "duloxetina", "venlafaxina", "oxcarbazepina", "carbamazepina", "fenitoína", "lamotrigina",
    "levetiracetam", "valproato", "topiramato", "primidona", "baclofeno", "tizanidina", "ciclobenzaprina",
    "ondansetrona", "prometazina", "dexametasona", "prednisona", "hidrocortisona", "betametasona",
    "cetoconazol", "terbinafina", "fluconazol", "clotrimazol", "miconazol", "acitretina", "adapaleno",
    "isotretinoína", "tretinoína", "bimatoprosta", "doramectina", "ivermectina", "spironolactona",
    "furosemida", "hidroclorotiazida", "clortalidona", "espironolactona", "indapamida", "bumetanida",
    "olmesartana", "losartana", "valsartana", "ramipril", "captopril", "enalapril", "benazepril",
    "lisinopril", "perindopril", "irbesartana", "labetalol", "clonidina", "hidralazina", "minoxidil",
    "nifedipina", "amlodipina", "felodipina", "nitrendipina", "lercanidipina", "diltiazem",
    "verapamil", "atenolol", "propranolol", "metoprolol", "bisoprolol", "carvedilol", "nebivolol",
    "digoxina", "amiodarona", "dronedarona", "sinvastatina", "atorvastatina", "rosuvastatina",
    "pravastatina", "fluvastatina", "pitavastatina", "ezetimiba", "fenofibrato", "fibrato",
    "fenofibrato", "gemfibrozil", "colesevelam", "bromocriptina", "cabergolina", "parlodel",
    "dostinex", "bromoprida", "metoclopramida", "domperidona", "ondansetrona", "granisetrona",
    "metilprednisolona", "prednisona", "hidrocortisona", "dexametasona", "betametasona", "fludrocortisona",
    "estradiol", "estrógeno", "progestágeno", "progesterona", "testosterona", "andrógeno",
    "estrogênio", "trieste", "estradiol", "valerato", "etinilestradiol", "medroxiprogesterona",
    "acetato", "nomegestrol", "gestodeno", "desogestrel", "levonorgestrel", "drospirenona",
    "noretisterona", "norelgestromina", "linestrenol", "etilestradiol", "cloprostenol", "mesilato",
    "cetoconazol", "tioconazol", "sulfato", "zolpidem", "cetoconazol", "tioconazol", "sulfato",
    "zolpidem", "zopiclona", "midazolam", "propofol", "dexmedetomidina", "lorazepam", "clonazepam",
    "alfentanila", "fentanila", "sufentanila", "remifentanila", "tramadol", "petidina", "meperidina",
    "bupivacaína", "lidocaína", "ropivacaína", "benzocaína", "tetracaína", "dibucaina", "prilocaína",
    "procaína", "adrenalina", "noradrenalina", "fenilefrina", "metoxamina", "dobutamina",
    "isoproterenol", "dopamina", "nitroglicerina", "nitroprussiato", "milrinona", "nesiritida",
    "hidralazina", "furosemida", "bumetanida", "espironolactona", "trometamol", "tris", "acetato",
    "borato", "carbonato", "cloridrato", "citrat", "fosfato", "gluconato", "hidrogenocarbonato",
    "lactato", "maleato", "orotato", "sulfato", "valerato", "veículo", "água", "óleo", "sorbitol",
    "propilenoglicol", "polietilenoglicol", "álcool", "glicerina", "creme", "unguento", "loção",
    "pomada", "solução", "colutório", "clorpromazina", "haloperidol", "perfenazina", "clozapina", "olanzapina", "aripiprazol",
    "ziprasidona", "quetiapina", "risperidona", "paliperidona", "lurasidona", "asenapina",
    "sulpirida", "levomepromazina", "trifluoperazina", "benzatropina", "biperideno", "trihexifenidilo",
    "quetamina", "memantina", "donepezila", "rivastigmina", "galantamina", "escopolamina", 
    "cinarizina", "betahistina", "flunarizina", "dimenidrinato", "metoclopramida", "ondansetrona",
    "droperidol", "difenidramina", "prometazina", "meclizina", "metilfenidato", "atomoxetina",
    "lisdexanfetamina", "modafinila", "dextroanfetamina", "mazindol", "sibutramina", "orlistat",
    "liraglutida", "exenatida", "sitagliptina", "vildagliptina", "saxagliptina", "linagliptina",
    "pioglitazona", "rosiglitazona", "acarbose", "miglitol", "tolbutamida", "glibenclamida",
    "glimepirida", "repaglinida", "nateglinida", "dapagliflozina", "empagliflozina", "canagliflozina",
    "insulina glargina", "insulina detemir", "insulina degludeca", "insulina lispro", "insulina aspart",
    "insulina glulisina", "insulina regular", "insulina NPH", "insulina Lente", "insulina Ultra Lente",
    "oxandrolona", "metiltestosterona", "testosterona em gel", "testosterona injetável", "estanozolol",
    "nandrolona", "boldenona", "primobolan", "trembolona", "hormônio do crescimento", "follitropina",
    "menotropina", "gonadotrofina coriônica", "clomifeno", "letrozol", "anastrozol", "tamoxifeno",
    "raloxifeno", "fulvestranto", "bicalutamida", "flutamida", "leuprorrelina", "goserrelina",
    "triptorrelina", "alendronato", "risedronato", "ibandronato", "zoledronato", "denosumabe",
    "teriparatida", "calcitonina", "vitamina D3", "colecalciferol", "calcitriol", "alfacalcidol",
    "carbonato de cálcio", "citrato de cálcio", "carbonato de magnésio", "sulfato de magnésio",
    "fosfato de potássio", "cloreto de potássio", "bicarbonato de potássio", "acetato de zinco",
    "sulfato de zinco", "óxido de zinco", "sulfato de cobre", "óxido de ferro", "sulfato de ferro",
    "gluconato de ferro", "carbonato de ferro", "sulfato de manganês", "óxido de manganês",
    "cloreto de cromo", "óxido de cromo", "iodeto de potássio", "iodeto de sódio", "iodeto de ferro",
    "cloreto de flúor", "fluoreto de sódio", "fluoreto de estanho", "benzidamina", "cloridrato de benzidamina",
    "maleato de dimetindeno", "cloreto de cetilpiridínio", "dicloridrato de cetirizina", "desloratadina",
    "fexofenadina", "cloridrato de pseudoefedrina", "bromidrato de fenoterol", "brometo de ipratrópio",
    "sulfato de salbutamol", "cloridrato de fenilefrina", "oximetazolina", "cloreto de sódio",
    "hidróxido de sódio", "borato de sódio", "borato de alumínio", "carbonato de cálcio",
    "ácido ascórbico", "vitamina C", "cianocobalamina", "vitamina B12", "colecalciferol", "vitamina D",
    "tiamina", "vitamina B1", "riboflavina", "vitamina B2", "piridoxina", "vitamina B6", "ácido fólico",
    "ácido pantotênico", "biotina", "nicotinamida", "vitamina B3", "vitamina E", "tocoferol",
    "acetato de tocoferol", "sulfato ferroso", "gluconato ferroso", "fumarato ferroso",
    "pantenol", "cloridrato de piridoxina", "betacaroteno", "polivitamínico", "multivitamínico",
    "fosfato de clindamicina", "fosfato de neomicina", "bacitracina", "gentamicina", "sulfato de polimixina B",
    "sulfadiazina de prata", "mupirocina", "ácido fusídico", "peróxido de benzoíla", "adapaleno",
    "tretinoína", "isotretinoína", "ácido azelaico", "ácido salicílico", "ácido glicólico",
    "hidroquinona", "melanina", "polidocanol", "dexpantenol", "óxido de zinco", "cetoconazol",
    "miconazol", "terbinafina", "butenafina", "sulfeto de selênio", "clotrimazol", "fluconazol"
]

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
    
    return binary

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

# Função para processar a imagem e extrair o texto
def extrair_texto_imagem(window_adicionar, conn):
    global ultima_imagem_id
    path = obter_imagem(conn, ultima_imagem_id)
    if path:
        image = cv2.imread(path)
        
        # Chamando a função para OCR com easyocr
        texto = ocr_with_easyocr(image)

        # Limpar os campos antes de preencher com novos dados
        limpar_campos(window_adicionar)

        # Extrair nome do medicamento, quantidade e medida
        nome_medicamento = encontrar_nome_medicamento(texto)
        quantidade, medida = encontrar_quantidade_e_medida(texto)

        # Se alguma informação não foi encontrada, chama a segunda função
        if quantidade == "Quantidade não encontrada." or medida == "Medida não encontrada.":
            extrair_texto_imagem_2(window_adicionar, conn)
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

def extrair_texto_imagem_2(window_adicionar, conn):
    global ultima_imagem_id
    path = obter_imagem(conn, ultima_imagem_id)
    if path:
        image = Image.open(path)
        texto = pytesseract.image_to_string(image)

        # Extrair nome do medicamento, quantidade e medida
        nome_medicamento = encontrar_nome_medicamento(texto)
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

# Função para encontrar o nome do medicamento
def encontrar_nome_medicamento(texto):
    # Expressão regular para encontrar o nome do medicamento
    padrao = r"\b(" + "|".join(palavras_chave) + r")\b"
    resultado = re.search(padrao, texto, flags=re.IGNORECASE)
    if resultado:
        return resultado.group(0).capitalize()  # Retorna o primeiro nome de medicamento encontrado
    else:
        return "Medicamento não encontrado."

# CAPTURA A QUANTIDADE JUNTO COM A MEDIDA E DIVIDE 

# Lista de unidades de medida permitidas
palavras_medida = ["g", "mg", "mmg", "L", "ml", "mml", "u"]

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
    elif event == '-EXTRAIR-':
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
            tentativa_1 = extrair_texto_imagem(window_adicionar, conn)
            if "não encontrado" in tentativa_1[0] or "não encontrado" in tentativa_1[1]:
                tentativa_2 = extrair_texto_imagem_2(window_adicionar, conn)
                if "não encontrado" in tentativa_2[0] or "não encontrado" in tentativa_2[1]:
                    # Preencher com "Quantidade não encontrada" e "Medida não encontrada"
                    window_adicionar['-QUANTIDADE-'].update('Quantidade não encontrada')
                    window_adicionar['-MEDIDA-'].update('Medida não encontrada')
                else:
                    window_adicionar['-QUANTIDADE-'].update(tentativa_2[0])
                    window_adicionar['-MEDIDA-'].update(tentativa_2[1])
            else:
                window_adicionar['-QUANTIDADE-'].update(tentativa_1[0])
                window_adicionar['-MEDIDA-'].update(tentativa_1[1])

            # Loop da segunda janela de adicionar produto
            while True:
                event_adicionar, values_adicionar = window_adicionar.read()

                if event_adicionar == sg.WIN_CLOSED:
                    break
                elif event_adicionar == 'Adicionar':
                    if values_adicionar['-NOME-'] and values_adicionar['-QUANTIDADE-'] and values_adicionar['-MEDIDA-']:
                        inserir_produto(conn, values_adicionar['-NOME-'], values_adicionar['-QUANTIDADE-'], values_adicionar['-MEDIDA-'], ultima_imagem_id)
                        sg.popup("Produto adicionado com sucesso!")
                        break
                    else:
                        sg.popup_error("Por favor, preencha todas as informações do medicamento.")
            window_adicionar.close()

# Fechando as janelas ao sair dos loops
window_principal.close()
# Fechando a conexão com o banco de dados ao final do programa
conn.close()
