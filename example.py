import serial
import time
import fvs

def main():
    cap = fvs.FoveatedVisionSystem(0)
    cap.open()
    time.sleep(60)
    cap.close()

if __name__ == '__main__':
    main()
