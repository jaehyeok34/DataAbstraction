import threading
import time


def generateRecieveThread():
    def recv():
        while True:
            print('hello world')
            time.sleep(3)
            

    receiver = threading.Thread(target = recv)
    receiver.start()
    print('end')
    return receiver

thread = generateRecieveThread()
print(thread.is_alive())