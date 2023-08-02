import zmq
from codec import Codec

class ReceiverModel:
    def __init__(self) -> None:
        self.__context = zmq.Context()
        self.__socket = self.__context.socket(zmq.DEALER)
        self.__socket.setsockopt_string(zmq.IDENTITY, 'jang')


    def startModel(self) -> None:
        self.__socket.connect("tcp://127.0.0.1:3400")
        self.__socket.send_multipart([b'connected'])
        print('-----Start receiver model-----')
        self.recv()
    
    def recv(self) -> None:
        while True:
            reply = self.__socket.recv_multipart()
            print(f"Before decoding: {reply}, type: {type(reply).__name__}[{type(reply[0]).__name__}]")   
            decoded = list(Codec.decode(reply))
            if len(decoded) == 1:
                decoded = decoded[0]
            print(f"After encoding: {decoded}, type: {type(decoded).__name__}")
            print()



def main():
    sender = ReceiverModel()
    sender.startModel()

if __name__ == '__main__':
    main()