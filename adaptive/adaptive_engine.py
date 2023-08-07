from pyevsim.definition import Infinite
import zmq
from pyevsim import SystemSimulator
from pyevsim.system_executor import SysExecutor, BehaviorModelExecutor
import threading
from bootstreap import Bootstrap
from queue import Queue

class AdaptiveEngine:
    # 외부 패킷 수신 객체(multi-thread)
    class __Receiver:
        __SOCK_CONNECTED    =   'connected'
        __SOCK_DISCONNECTED =   'disconnected'

        def __init__(self, queue: Queue) -> None:
            self.__context  =   zmq.Context()
            self.__socket   =   self.__context.socket(zmq.ROUTER)
            self.__users    =   set()
            self.__queue    =   queue

            self.__socket.bind('tcp://127.0.0.1:3401')
            print('소켓 준비완료')

        @property
        def users(self) -> list:
            return self.__users
        
        def recv(self):
              while True:
                receive = self.__socket.recv_multipart()
                if AdaptiveEngine.__Receiver.__SOCK_CONNECTED in receive:
                    self.__users.add(receive[0])
                    pass
                elif AdaptiveEngine.__Receiver.__SOCK_DISCONNECTED in receive:
                    self.__users.remove(receive[0])
                else:
                    self.__queue.put(receive)
    
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
        self.__receiver     =   AdaptiveEngine.__Receiver(self.__bootstrap.queue)

    
    # property
    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def engine(self) -> SysExecutor:
        return self.__engine
    
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

        
def addParts():
    while True:
        parts = input('> ')
        if parts in adaptiveEngine.bootstrap.parts:
            print(f'{parts}에 데이터 전송됨')
            adaptiveEngine.engine.insert_external_event(parts, None)
        else:
            print('존재하지 않은 parts임.')

if __name__ == "__main__":
    adaptiveEngine = AdaptiveEngine()
    # adaptiveEngine.engine.insert_external_event(adaptiveEngine.partsPorts[0], None)
    t = threading.Thread(target=addParts)
    t.start()
    adaptiveEngine.run()


