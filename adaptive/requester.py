from adaptive_engine import AdaptiveEngine
from parts_management import PartsManagement
import zmq
import threading
import time

class Requester:
    def __init__(self) -> None:
        self.__socket = self.__initSocket()

    def __initSocket(self) -> zmq.Socket:
        context = zmq.Context()
        socket = context.socket(zmq.DEALER)
        socket.setsockopt_string(zmq.IDENTITY, 'requester')
        socket.connect(AdaptiveEngine.NET_INFO)
        socket.send_multipart([AdaptiveEngine.SOCK_CONNECTED])
        # print('소켓 준비 완료')

        return socket
    
    def __send(self) -> None:
        datas = [
            [b'+', b'10', b'20', b'30', b'40', b'50'],
            [b'-', b'100', b'10', b'15', b'20', b'25', b'30'],
            [b'*', b'2', b'5', b'3', b'10'],
            [b'/', b'1000', b'2', b'5', b'100']
        ]
        
        for items in datas:
            self.__socket.send_multipart(items)
            result = self.__socket.recv_multipart()[0].decode()
            print(f'request({[item.decode() for item in items]}) result: {result}')
            print()
            time.sleep(1)
        
        time.sleep(15)
        self.__socket.send_multipart(datas[3])
        result = self.__socket.recv_multipart()[0].decode()
        print(f'request({[item.decode() for item in datas[3]]}) result: {result}')
        while True:
            pass

    def __recv(self) -> None:
        while True:
            reply = self.__socket.recv_multipart()

            if PartsManagement.UNPROCESSABLE in reply:
                print('처리 불가능')
            
    def run(self) -> None:
        # receiver = threading.Thread(target = self.__recv)
        # receiver.start()

        self.__send()


if __name__ == '__main__':
    req = Requester()
    req.run()