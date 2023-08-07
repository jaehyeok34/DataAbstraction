from adaptive_engine import AdaptiveEngine
from bootstreap import Bootstrap
import zmq
import threading

class Requester:
    def __init__(self) -> None:
        self.__socket = self.__initSocket()

    def __initSocket(self) -> zmq.Socket:
        context = zmq.Context()
        socket = context.socket(zmq.DEALER)
        socket.setsockopt_string(zmq.IDENTITY, input('ID > '))
        socket.connect(AdaptiveEngine.NET_INFO)
        socket.send_multipart([AdaptiveEngine.SOCK_CONNECTED])
        print('소켓 준비 완료')

        return socket
    
    def __send(self) -> None:
        while True:
            msg = input('msg("partsA 10 20") > ').split()

            self.__socket.send_multipart([item.encode() for item in msg])

    def __recv(self) -> None:
        while True:
            reply = self.__socket.recv_multipart()

            if Bootstrap.UNPROCESSABLE in reply:
                print('처리 불가능')
            
    def run(self) -> None:
        receiver = threading.Thread(target = self.__recv)
        receiver.start()

        self.__send()


if __name__ == '__main__':
    req = Requester()
    req.run()