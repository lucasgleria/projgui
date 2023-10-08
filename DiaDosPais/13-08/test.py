import serial
import time
# ser = serial.Serial(3)
ser = serial.Serial('COM3', 9600)



while True:
    cmd = input('Conectado! Digite 1 para continuar...\n')
    while True:
        if cmd == "1":
          ser.write(input('Escreva o Angulo aqui: ').encode('utf-8'))
        else:
          break

