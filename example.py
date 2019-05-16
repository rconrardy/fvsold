import time
import fvs

def main():
    cap = fvs.FoveatedVisionSystem(0, 1)
    cap.open()
    time.sleep(10)
    cap.close()

if __name__ == '__main__':
    main()
