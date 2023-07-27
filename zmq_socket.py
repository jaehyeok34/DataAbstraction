import zmq
from codec import Codec

class ZmqSocket:
    class Signal:
        connected = 'connected'.encode()

    # constructor
    def __init__(self, socketType: int, addr: str, identity:str = None) -> None:
        self.__context = zmq.Context()
        self.__socket = self.__context.socket(socketType)
        self.__identity = identity

        if socketType == zmq.ROUTER:
            self.__socket.bind(addr)
            print('socket이 바인딩 되었습니다.')
        else:
            self.__socket.connect(addr)
            self.__socket.send_multipart([f'{ZmqSocket.Signal.connected} {identity}'])

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
