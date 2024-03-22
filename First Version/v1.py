menu = '''

[ap] Adicionar Produto
[ep] Exibir Produto
[lp] Localizar Produto
[q] Sair

=> '''


produto = ""
nome, eixoX, eixoY, eixoZ= "", "", "", ""

while True:

    opcao = input(menu)

    if opcao == "ap":
        nome = str(input("Nome do produto: "))
        eixoX = int(input("Insira a posição X: "))
        eixoY = int(input("Insira a posição Y: "))
        eixoZ = int(input("Insira a posição Z: "))
        produto += f'\nProduto: {nome} - {eixoX} - {eixoY} - {eixoZ}'
        print('\n=== Produto adicionado com sucesso! ===')

    elif opcao == "ep":
        
        print("\n================== VIEW ONLY ================")
        print("Não foram adicionados produtos." if not produto else produto)
        print("=============================================")
        

    # elif opcao == "lp":


    elif opcao == "q":
        break

    else:
        print('''
            ---------------------------------------------------------
            Opção Inválida! Selecione novamente uma operação desejada
            ---------------------------------------------------------
            ''')