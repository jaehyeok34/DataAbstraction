import zmq
from codec import Codec
from enum import Enum

class ZmqSocket:
    class Signal:
        connected = 'connected'
        readyToRecv = 'readyToReceive'

    # constructor
    def __init__(self, socketType: int, addr: str, identity:str = None) -> None:
        self.__context = zmq.Context()
        self.__socket = self.__context.socket(socketType)

        if identity is not None:
            self.__identity = identity
            self.__socket.setsockopt_string(zmq.IDENTITY, self.__identity)

        if socketType == zmq.ROUTER:
            self.__socket.bind(addr)
            print('socket이 바인딩 되었습니다.')
        else:
            self.__socket.connect(addr)
            self.__socket.send_multipart([ZmqSocket.Signal.connected.encode()])
            self.__socket.send_multipart([ZmqSocket.Signal.readyToRecv.encode()])


    # property
    @property
    def context(self) -> zmq.Context:
        return self.__context
    
    @property
    def socket(self) -> zmq.Socket:
        return self.__socket
    
    @property
    def identity(self) -> str:
        return self.__identity
