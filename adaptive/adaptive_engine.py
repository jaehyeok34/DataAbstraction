from pyevsim.definition import Infinite
import zmq
from pyevsim import SystemSimulator
from pyevsim.system_executor import SysExecutor, BehaviorModelExecutor
import threading
from bootstreap import Bootstrap
from queue import Queue
from typing import Callable, Tuple

class AdaptiveEngine:
    SOCK_CONNECTED      =   b'connected'
    SOCK_DISCONNECTED   =   b'disconnected'
    NET_INFO            =   'tcp://127.0.0.1:3401'

    # 외부 패킷 수신 클래스(multi-thread)
    class __Receiver:
        def __init__(
            self, 
            enqueue: Callable[
                [zmq.Socket, str, str, Tuple[int, int]],
                None
            ]
        ) -> None:
            self.__context  =   zmq.Context()
            self.__socket   =   self.__context.socket(zmq.ROUTER)
            self.__users    =   set()
            self.__enqueue  =   enqueue
            self.__socket.bind('tcp://127.0.0.1:3401')
            print('소켓 바인딩 완료')

        # property
        @property
        def users(self) -> list:
            return self.__users
        
        # method
        def recv(self):
              while True:
                receive = self.__socket.recv_multipart()
                # 외부에서 연결 요청
                if AdaptiveEngine.SOCK_CONNECTED in receive:
                    self.__users.add(receive[0])
                    print(f'유저 추가: {self.__users}')
                # 외부에서 종료 요청
                elif AdaptiveEngine.SOCK_DISCONNECTED in receive:
                    self.__users.remove(receive[0])
                # 외부에서 처리 요청
                else:
                    userID = receive[0]
                    partsName = receive[1].decode()
                    msg = [int(x.decode()) for x in receive[2:]]
                    self.__enqueue(self.__socket, userID, partsName, msg)
    
    # constructor
    def __init__(
        self,
        name        =   'default',
        receivePort =   'packet',
    ) -> None:
        self.__name         =   name
        self.__receivePort  =   receivePort
        self.__engine       =   self.__initEngine(self.__name, self.__receivePort)
        self.__bootstrap    =   Bootstrap(
            instantiate_time=   0,
            destruct_time   =   Infinite,
            engine_name     =   self.__engine.get_name()
        )
        self.__receiver     =   AdaptiveEngine.__Receiver(self.__bootstrap.enqueue)

    
    # property
    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def engine(self) -> SysExecutor:
        return self.__engine
    
    # for test
    @property
    def bootstrap(self) -> Bootstrap:
        return self.__bootstrap
    
    # private method
    def __initEngine(self, name, port) -> SysExecutor:
        engine = SystemSimulator.register_engine(
                    name, 
                    'VIRTUAL_TIME', 
                    1
        )
        engine.insert_input_port(port)
        return engine
    
    def __recv(self):
        receiver = threading.Thread(target=self.__receiver.recv)
        receiver.start()
    
    # method
    def run(self):
        self.__engine.register_entity(self.__bootstrap)
        self.__engine.coupling_relation(
            None,               self.__receivePort,
            self.__bootstrap,   self.__bootstrap.inputPort  
        )
        self.__engine.insert_external_event(self.__receivePort, None)
        self.__recv()
        self.__engine.simulate()

# # for test
# def addParts():
#     while True:
#         parts = input('> ')
#         if parts in adaptiveEngine.bootstrap.parts:
#             print(f'{parts}에 데이터 전송됨')
#             adaptiveEngine.engine.insert_external_event(parts, [10, 20])
#         else:
#             adaptiveEngine.bootstrap.enqueue(
#                 None,
#                 None,
#                 parts,
#                 [10, 20],
#                 )

if __name__ == "__main__":
    adaptiveEngine = AdaptiveEngine()
    # # for test
    # t = threading.Thread(target=addParts)
    # t.start()
    # ##########
    adaptiveEngine.run()


