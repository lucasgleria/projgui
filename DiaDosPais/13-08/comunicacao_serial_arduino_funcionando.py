import serial

ser = serial.Serial('COM6',
                    9600,
                    timeout=2,)


while True:
    try:
      cmd = input('Digite 1 para conectar...\n')

    except Exception as e:
      print('Erro', e)
      exit(1)

    while True:
        if cmd == "1":
          
          ##
          ser.write(input('''
                          Estou Conectado!
                          \n
                          \n
                          Escreva o Angulo aqui: 
                          ''').encode('utf-8'))
          ##

          # read = str(ser.read(size=80), encoding='utf-8')
          # print(read)

        elif cmd == "quit":
          break
        
        else:
          print('''
            Por favor, escolha uma das opções disponíveis.
            ''')
          break
        break
    break