import sys
import os
import threading
import serial
import sqlite3
import datetime
from PySide6 import QtWidgets, QtGui
from PIL import Image, ImageQt
import fitz


# Lock para garantir acesso seguro às variáveis globais
data_lock = threading.Lock()

# Variáveis globais
nome = None
registro = None
eixo_x = None
nota_fiscal_pdf_path = None
eixo_z = None
quantidade = None
medida_da_quantidade = None
selected_image_path = None
has_selected_image = False
Temperatura = None
Umidade = None
main_window = None
ser = None


def connect_to_arduino(porta_COM, taxa_band):
    try:
        if not porta_COM:
            raise ValueError('Campo Porta COM obrigatório!')
        elif not taxa_band:
            raise ValueError('Campo Taxa Band obrigatório!')
        elif not taxa_band.isnumeric():
            raise ValueError('A Taxa Band deve ser um valor numérico!')

        ser = serial.Serial(porta_COM, int(taxa_band), timeout=2)
        return ser

    except ValueError as ve:
        QtWidgets.QMessageBox.critical(
            None, 'Erro de Conexão', str(ve))
        return None


def clear_serial_input(ser):
    while ser.in_waiting:
        ser.read(ser.in_waiting)


def adicionar_produto(nome, registro, eixo_x, nota_fiscal_pdf_path, eixo_z, quantidade, medida_da_quantidade, validade, image_path):
    global has_selected_image
    data_criada = datetime.datetime.now()
    cursor.execute('INSERT INTO produtos (nome, registro, eixo_x, nota_fiscal_pdf_path, eixo_z, quantidade, medida_da_quantidade, imagem_path, validade, data_criada) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   (nome, registro, eixo_x, nota_fiscal_pdf_path, eixo_z, quantidade, medida_da_quantidade, image_path, validade, data_criada))
    conn.commit()
    QtWidgets.QMessageBox.information(
        None, 'Produto adicionado', f"O produto {nome} foi adicionado.")
    has_selected_image = image_path is not None


def get_image_data(image_path):
    if os.path.exists(image_path) and os.path.isfile(image_path):
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
        return image_data
    return None


def exibir_produtos_existentes():
    cursor.execute('SELECT nome, registro, validade FROM produtos')
    produtos = cursor.fetchall()
    return produtos


def localizar_produto(filtro_nome):
    cursor.execute(
        'SELECT nome, registro FROM produtos WHERE nome LIKE ?', ('%' + filtro_nome + '%',))
    produtos = cursor.fetchall()
    return produtos


def get_product_info(product_name):
    cursor.execute(
        'SELECT nome, nota_fiscal_pdf_path, registro, quantidade, medida_da_quantidade, eixo_x, eixo_z, imagem_path, validade FROM produtos WHERE nome = ?', (product_name,))
    product_info = cursor.fetchone()

    if product_info:
        nome, nota_fiscal_pdf_path, registro, quantidade, medida_da_quantidade, eixo_x, eixo_z, image_path, validade = product_info

        # Verifica se há uma imagem associada
        if image_path and os.path.exists(image_path):
            return nome, nota_fiscal_pdf_path, registro, quantidade, medida_da_quantidade, eixo_x, eixo_z, image_path, validade
        else:
            return nome, nota_fiscal_pdf_path, registro, quantidade, medida_da_quantidade, eixo_x, eixo_z, None, validade
    else:
        return None


def products_table_layout(products):
    header = ["Nome", "Registro", "Validade"]
    data = [[product[0], product[1], get_product_info(product[0])[-1]]
            for product in products]

    layout = QtWidgets.QVBoxLayout()
    table = QtWidgets.QTableWidget()
    table.setRowCount(len(data))
    table.setColumnCount(len(header))
    table.setHorizontalHeaderLabels(header)

    for i, row in enumerate(data):
        for j, value in enumerate(row):
            item = QtWidgets.QTableWidgetItem(str(value))
            table.setItem(i, j, item)

    layout.addWidget(table)

    window = QtWidgets.QWidget()
    window.setLayout(layout)
    return window


def products_info_loop():
    global nome, registro, quantidade, medida_da_quantidade, eixo_x, eixo_z, validade, main_window

    nome, nota_fiscal_pdf_path, registro, quantidade, medida_da_quantidade, eixo_x, eixo_z, image_path, validade = get_product_info(
        nome)

    main_window.close()

    info_product_window = QtWidgets.QWidget()
    info_product_layout = QtWidgets.QVBoxLayout()

    label_nome = QtWidgets.QLabel(f"Nome: {nome}")
    info_product_layout.addWidget(label_nome)

    label_registro = QtWidgets.QLabel(f"Registro: {registro}")
    info_product_layout.addWidget(label_registro)

    label_quantidade = QtWidgets.QLabel(f"Quantidade: {quantidade}")
    info_product_layout.addWidget(label_quantidade)

    label_medida = QtWidgets.QLabel(
        f"Medida da Quantidade: {medida_da_quantidade}")
    info_product_layout.addWidget(label_medida)

    label_eixo_x = QtWidgets.QLabel(f"Eixo X: {eixo_x}")
    info_product_layout.addWidget(label_eixo_x)

    label_eixo_z = QtWidgets.QLabel(f"Eixo Z: {eixo_z}")
    info_product_layout.addWidget(label_eixo_z)

    if image_path:
        label_imagem = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(image_path)
        pixmap = pixmap.scaled(300, 300)
        label_imagem.setPixmap(pixmap)
        info_product_layout.addWidget(label_imagem)

    label_validade = QtWidgets.QLabel(f"Validade: {validade}")
    info_product_layout.addWidget(label_validade)

    button_guardar = QtWidgets.QPushButton("Guardar Produto")
    button_guardar.clicked.connect(guardar_produto)
    info_product_layout.addWidget(button_guardar)

    button_retirar = QtWidgets.QPushButton("Retirar Produto")
    button_retirar.clicked.connect(retirar_produto)
    info_product_layout.addWidget(button_retirar)

    button_voltar = QtWidgets.QPushButton("Voltar")
    button_voltar.clicked.connect(voltar_main_window)
    info_product_layout.addWidget(button_voltar)

    info_product_window.setLayout(info_product_layout)
    info_product_window.show()


def guardar_produto():
    global ser, info_product_window, main_window, eixo_x, eixo_z
    guardar = f'X{eixo_x}Z{eixo_z}GUARDAR' + '\n'
    ser.write(guardar.encode())
    QtWidgets.QMessageBox.information(
        None, 'Produto guardado', "O produto foi guardado.")
    info_product_window.close()
    main_window.show()


def retirar_produto():
    global ser, info_product_window, main_window, eixo_x, eixo_z

    dialog = QtWidgets.QInputDialog()
    dialog.setInputMode(QtWidgets.QInputDialog.TextInput)
    dialog.setWindowTitle("Retirar Produto")
    dialog.setLabelText("Digite a quantidade que deseja retirar:")
    dialog.resize(400, 100)
    dialog.exec_()

    quantity_to_remove = dialog.textValue()
    if quantity_to_remove:
        retirar = f'X{eixo_x}Z{eixo_z}RETIRAR{quantity_to_remove}' + '\n'
        ser.write(retirar.encode())
        QtWidgets.QMessageBox.information(
            None, 'Produto retirado', "O produto foi retirado.")

    main_window.show()


def voltar_main_window():
    global info_product_window, main_window
    info_product_window.close()
    main_window.show()


def show_image_dialog():
    global selected_image_path, has_selected_image
    image_path, _ = QtWidgets.QFileDialog.getOpenFileName(
        None, "Selecionar Imagem", "", "Image Files (*.png *.jpg *.jpeg)")
    if image_path:
        selected_image_path = image_path
        has_selected_image = True
        QtWidgets.QMessageBox.information(
            None, 'Imagem selecionada', "Imagem selecionada com sucesso.")


def show_pdf_dialog():
    global nota_fiscal_pdf_path
    pdf_path, _ = QtWidgets.QFileDialog.getOpenFileName(
        None, "Selecionar PDF", "", "PDF Files (*.pdf)")
    if pdf_path:
        nota_fiscal_pdf_path = pdf_path
        QtWidgets.QMessageBox.information(
            None, 'PDF selecionado', "PDF selecionado com sucesso.")


def create_database():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS produtos (id INTEGER PRIMARY KEY, nome TEXT, registro TEXT, eixo_x TEXT, nota_fiscal_pdf_path TEXT, eixo_z TEXT, quantidade TEXT, medida_da_quantidade TEXT, imagem_path TEXT, validade TEXT, data_criada TEXT)')
    conn.commit()
    conn.close()


def main_window_layout():
    global stacked_widget

    layout = QtWidgets.QVBoxLayout()

    products = exibir_produtos_existentes()
    products_window = products_table_layout(products)
    layout.addWidget(products_window)

    filtro_nome = QtWidgets.QLineEdit()
    filtro_nome.setPlaceholderText("Filtrar por nome...")
    layout.addWidget(filtro_nome)

    search_button = QtWidgets.QPushButton("Buscar")
    search_button.clicked.connect(
        lambda: show_search_results(filtro_nome.text()))
    layout.addWidget(search_button)

    adicionar_button = QtWidgets.QPushButton("Adicionar Produto")
    adicionar_button.clicked.connect(show_add_product_dialog)
    layout.addWidget(adicionar_button)

    sair_button = QtWidgets.QPushButton("Sair")
    sair_button.clicked.connect(sys.exit)
    layout.addWidget(sair_button)

    stacked_widget = QtWidgets.QStackedWidget()

    main_window_widget = QtWidgets.QWidget()
    main_window_widget.setLayout(layout)
    stacked_widget.addWidget(main_window_widget)

    return stacked_widget


def show_search_results(filtro_nome):
    if filtro_nome:
        produtos = localizar_produto(filtro_nome)
        products_window = products_table_layout(produtos)
        stacked_widget.addWidget(products_window)
        stacked_widget.setCurrentIndex(1)


def show_add_product_dialog():
    global nome, registro, eixo_x, nota_fiscal_pdf_path, eixo_z, quantidade, medida_da_quantidade, validade, selected_image_path

    dialog = QtWidgets.QDialog()
    dialog.setWindowTitle("Adicionar Produto")

    layout = QtWidgets.QFormLayout()

    nome_input = QtWidgets.QLineEdit()
    layout.addRow("Nome:", nome_input)

    registro_input = QtWidgets.QLineEdit()
    layout.addRow("Registro:", registro_input)

    eixo_x_input = QtWidgets.QLineEdit()
    layout.addRow("Eixo X:", eixo_x_input)

    nota_fiscal_pdf_button = QtWidgets.QPushButton("Selecionar PDF")
    nota_fiscal_pdf_button.clicked.connect(show_pdf_dialog)
    layout.addRow("Nota Fiscal PDF:", nota_fiscal_pdf_button)

    eixo_z_input = QtWidgets.QLineEdit()
    layout.addRow("Eixo Z:", eixo_z_input)

    quantidade_input = QtWidgets.QLineEdit()
    layout.addRow("Quantidade:", quantidade_input)

    medida_input = QtWidgets.QLineEdit()
    layout.addRow("Medida da Quantidade:", medida_input)

    validade_input = QtWidgets.QDateEdit()
    validade_input.setCalendarPopup(True)
    validade_input.setDate(datetime.date.today())
    layout.addRow("Validade:", validade_input)

    imagem_button = QtWidgets.QPushButton("Selecionar Imagem")
    imagem_button.clicked.connect(show_image_dialog)
    layout.addRow("Imagem:", imagem_button)

    salvar_button = QtWidgets.QPushButton("Salvar")
    salvar_button.clicked.connect(dialog.accept)
    layout.addWidget(salvar_button)

    dialog.setLayout(layout)

    if dialog.exec_():
        nome = nome_input.text()
        registro = registro_input.text()
        eixo_x = eixo_x_input.text()
        eixo_z = eixo_z_input.text()
        quantidade = quantidade_input.text()
        medida_da_quantidade = medida_input.text()
        validade = validade_input.date().toString("yyyy-MM-dd")

        if has_selected_image:
            selected_image_path = nome + ".png"
            convert_and_save_image(selected_image_path)

        adicionar_produto(nome, registro, eixo_x, nota_fiscal_pdf_path,
                          eixo_z, quantidade, medida_da_quantidade, validade, selected_image_path)


def convert_and_save_image(image_path):
    if os.path.exists(image_path):
        os.remove(image_path)
    image = Image.open(selected_image_path)
    image.save(image_path)


def main():
    global main_window, cursor, conn, ser

    # Inicializar a conexão com o banco de dados
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Criar a tabela se não existir
    create_database()

    # Conectar ao Arduino
    ser = connect_to_arduino('COM3', '9600')

    # Criar e exibir a janela principal
    app = QtWidgets.QApplication([])
    main_window = main_window_layout()
    main_window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()