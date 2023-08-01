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



# print(Codec.encode(10))
# print(Codec.encode(False))
# print(Codec.encode('hello'))
# print(Codec.encode([10, 20, 30]))
# print(Codec.encode([10, '20', True]))
# print(Codec.encode(1.3))

# def func(param: bytes):
#     return param.decode()

# datas = [b'jang', b'str', b'hello world']
# encodingDatas = []

# start = 0
# for i in range(len(datas)):
#     if 'str' == datas[i].decode():
#         encodingDatas = datas[i:]
#         datas = datas[:i]
#         break

# print(datas)
# print(encodingDatas)

# table = {
#     str.__name__        :       func
# }

# for i in range(0, len(encodingDatas), 2):
#     print(table[encodingDatas[i].decode()](encodingDatas[i + 1]))


temp = [1, 2, 3, 4, 5, 6]

for i in range(0, len(temp) - 1, 2):
    print(temp[i + 1])

data = [10, 20, 'hello World', False]

encoding = Codec.encode(data)
print(f'encoding: {encoding}')

decoding = Codec.decode(encoding)
print(f'decoding: {decoding}')

for item in decoding:
    print(f"type of '{item}': {type(item).__name__}")

e = Codec.encode(10)
d = Codec.decode(e)
print(e)
print(d)
