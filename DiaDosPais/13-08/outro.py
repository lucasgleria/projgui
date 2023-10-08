import serial
import time
import io

ser = serial.Serial('COM3', 9600)


while True:
    cmd = input('Digite 1 para conectar...\n')
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

          read = str(ser.read(size=20), encoding='utf-8') # Deixar size de bytes dinamico
          print(read)
        else:
          break