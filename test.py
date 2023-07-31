from codec import Codec
import zmq
import threading
import time

def router():
    context = zmq.Context()
    socket = context.socket(zmq.ROUTER)
    socket.bind('tcp://127.0.0.1:3400')

    while True:
        data: list = socket.recv_multipart()
        print(int.from_bytes(data[1]))


def dealer():
    context = zmq.Context()
    socket = context.socket(zmq.DEALER)
    socket.setsockopt(zmq.IDENTITY, 'dealer'.encode())
    socket.connect('tcp://127.0.0.1:3400')
    
    data = 10
    while True:
        socket.send_multipart([data.to_bytes()])
        time.sleep(10)



# thread = threading.Thread(target = dealer)
# thread.start()

# router()

# Codec.test([10, 20, 'string'])

# import pyautogui
# import pyperclip

# pyperclip.copy('ㅋㅋㅋㅋㅋㅋ')
# for _ in range(30):
#     pyautogui.hotkey('ctrl', 'v')
#     pyautogui.press('enter')



print(Codec.encode(10))
print(Codec.encode(False))
print(Codec.encode('hello'))
print(Codec.encode([10, 20, 30]))
print(Codec.encode([10, '20', True]))
print(Codec.encode(1.3))
