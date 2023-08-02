import zmq
from codec import Codec
import time

class SenderModel:
    def __init__(self) -> None:
        self.__context = zmq.Context()
        self.__socket = self.__context.socket(zmq.ROUTER)
        self.__sendDatas = [
            'hello world',
            97,
            True,
            ['e', 'f', 1, 2, False]
        ]

    def startModel(self) -> None:
        self.__socket.bind("tcp://127.0.0.1:3400")
        print('-----Start sender model-----')
        self.send()
    
    def send(self) -> None:
        receiver, _ = self.__socket.recv_multipart()        
        for item in self.__sendDatas:
            print(f"Before encoding: {item}, type: {type(item).__name__}")
            encoded = Codec.encode(item)
            print(f"After encoding: {encoded}, type: {type(encoded).__name__}[{type(encoded[0]).__name__}]")
            print()
            self.__socket.send_multipart([receiver] + encoded)
        print('-----send done-----')
        time.sleep(600)



def main():
    sender = SenderModel()
    sender.startModel()

if __name__ == '__main__':
    main()