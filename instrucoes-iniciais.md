## 1. [Baixar](https://code.visualstudio.com/download) Visual Studio Code
![Imagem](pasta-imagens-instrucoes/baixar-vscode.png)
#
## 2. Baixar [Python 3.9.9](https://www.python.org/downloads/release/python-399) e adicionar  ao caminho do sistema.
![Imagem](pasta-imagens-instrucoes/python399.png)
### Pesquise por Meu computador no Windows e vá em propriedades
![Imagem](pasta-imagens-instrucoes/meu-computador.png)
### Vá em configurações avançadas do sistema na direita superior da tela
![Imagem](pasta-imagens-instrucoes/configuracoes-avancadas.png)
### Em propriedades do sistema, clique na aba "Avançado" e no último botão "Variáveis de ambiente"
![Imagem](pasta-imagens-instrucoes/variaveis.png)
### Em variáveis de ambiente clique em PATH e depois no botão "Editar"
![Imagem](pasta-imagens-instrucoes/editar-path.png)
### Em editar a variável de ambiente clique em "Novo" e adicione o path do Python 3.9.9 (ex: C:\Python39\Scripts)
![Imagem](pasta-imagens-instrucoes/novo-path.png)
#
## 3. Abrir o VSCode (com uma pasta vazia)
#
## 4. Criar Venv: Rodar no terminal: "python -m venv venv" (retire as aspas)
### Clique Cntrl + J para abrir o terminal
### Rode o comando no terminal
![Imagem](pasta-imagens-instrucoes/terminal-venv.png)
### Uma dessas duas pastas será criada (ou as duas)
![Imagem](pasta-imagens-instrucoes/pastas-venv.png)
### Não mexa nelas.
#
## 5. Rodar no terminal: "Git clone" (retire as aspas)
### Rode o comando no terminal: git clone https://github.com/lucasgleria/projgui.git
![Imagem](pasta-imagens-instrucoes/comando-clone.png)
### Todo o projeto que está no github será clonado para seu respoitório local.
#
## 6. Instale as extensões no Visual Studio Code: Intellicode, Pylance, Pylint, Python, SQLite Viewer.
### Vá no Ícone de extensões da barra lateral esquerda e instale todas as extensões citadas acima
![Imagem](pasta-imagens-instrucoes/extensoes.png)
#
## 7. Rodar no terminal: "pip install pyserial PySimpleGUI sqlite3 PyPDF2 PdfReader pillow shutil uuid pymupdf pdf2image easyocr opencv-python opencv-python-headless cv2 tensorflow pytesseract threading fitz qimage2ndarray" (retire as aspas)
### Rode o comando no terminal
![Imagem](pasta-imagens-instrucoes/comando-pip.png)
