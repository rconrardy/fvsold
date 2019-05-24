import time
import fvs

def main():
    cap = fvs.FoveatedVisionSystem(0,2)
    cap.open()
    time.sleep(15)
    cap.close()

if __name__ == '__main__':
    main()
