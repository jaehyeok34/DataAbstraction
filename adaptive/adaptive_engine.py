from pyevsim.definition import Infinite
import zmq
from codec import Codec
from zmq_socket import ZmqSocket
from pyevsim import BehaviorModelExecutor, SystemSimulator
from pyevsim.system_executor import SysExecutor
from enum import Enum


class AdaptiveEngine:
    # constructor
    def __init__(
        self,
        name = 'default',
        inPort = 'start',

    ) -> None:
        self.__name = name
        self.__inPort = inPort
        self.__engine = self.__initEngine(self.__name, self.__inPort)
    
    # property
    @property
    def name(self):
        return self.__name
    
    @property
    def inPort(self):
        return self.__inPort
    
    @property
    def engine(self):
        return self.__engine
    
    # method
    def __initEngine(self, name, inPort) -> SysExecutor:
        engine = SystemSimulator.register_engine(
                    name, 
                    'VIRTUAL_TIME', 
                    1
        )
        engine.insert_input_port(inPort)
        return engine
    
    def registerModel(self, model: BehaviorModelExecutor, inPort: str):
        self.__engine.register_entity(model)
        self.__engine.coupling_relation(
            None, self.__inPort,
            model, inPort
        )


def main():
    ## zmq socket 생성 및 바인딩
    socketManager = ZmqSocket(
        socketType = zmq.DEALER,
        addr = 'tcp://127.0.0.1:3400',
        identity = input('input ID > ')
    )

    ## simulation engine/model 생성
    engineName = 'second engine'
    engineInputPort = 'start'
    engine = SystemSimulator.register_engine(engineName, "VIRTUAL_TIME", 1)
    model:BehaviorModelExecutor = RemoteModel(0, Infinite, "remote", engineName, 'start', socketManager.socket)

    ## engine 설정
    engine.insert_input_port(engineInputPort)
    # engine.register_entity(model)
    engine.coupling_relation(
        None,   engineInputPort, 
        model,  model.get_name()
    )

    ## engine 실행
    engine.insert_external_event(engineInputPort, None)
    engine.simulate()
        
        
if __name__ == "__main__":
    main()


