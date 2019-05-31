import serial
import time
import fvs

def main():
    ser = serial.Serial('COM4', baudrate = 9600, timeout = 1)
    while(True):
        userInput = input('Enter input: ')
        ser.write(str.encode(userInput))
        arduinoData = ser.readline().decode('ascii')
        print(arduinoData)
        arduinoData = ser.readline().decode('ascii')
        print(arduinoData)

if __name__ == '__main__':
    main()
