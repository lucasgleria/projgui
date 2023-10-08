import serial

while True:
    try:
        arduino = serial.Serial('COM3', 9600)
        print('Arduino conectado')
        break

    except:
        pass

while True:
    cmd = input('Digite "1" para VIRAR PARA 0 e "2" para VIRAR A 180\n')

    if cmd == "1":
        serial.Serial.write("x0".encode('utf-8'))

    elif cmd == "2":
        serial.Serial.write("x180".encode('utf-8'))

    serial.Serial.flush()