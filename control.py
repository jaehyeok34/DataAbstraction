from pyevsim.definition import Infinite
import zmq
from codec import Codec
from enum import Enum
from pyevsim import SystemSimulator, BehaviorModelExecutor
from pyevsim.definition import *
from zmq_socket import ZmqSocket
import time

class ControlModel(BehaviorModelExecutor):
    class State(Enum):
        execute = 'execute'
        terminate = 'terminate'

    # constructor
    def __init__(
            self, 
            instanceTime    : float,   
            destructTime    : float,   
            modelName       : str, 
            engineName      : str, 
            inputPort       : str, 
            socket          : zmq.Socket
        ):
        super().__init__(instanceTime, destructTime, modelName, engineName)

        self.insert_state(ControlModel.State.execute, 1000)
        self.init_state(ControlModel.State.terminate)

        self.insert_input_port(inputPort)
        self.init_state(ControlModel.State.terminate)

        self.__socket = socket
        self.__remoteList = []

    
    # method


    # override method(BehaviorModelExecutor)
    def ext_trans(self, port, msg):
        print('model execute')
        self.init_state(ControlModel.State.execute)

    def int_trans(self):
        self.init_state(ControlModel.State.execute)

    def output(self):
        reply = Codec.decode(self.__socket.recv_multipart())
        dealerID = reply[0]
        command = reply[1]
        datas = reply[1:]

        if (dealerID not in self.__remoteList) and (command == ''):
            self.__remoteList.append(dealerID)

        pass
    
    

def main():
    ## zmq socket 생성 및 바인딩
    socket = ZmqSocket(
        socketType = zmq.ROUTER,
        addr = 'tcp://127.0.0.1:3400'
    )

    ## simulation engine/model 생성
    engineName = 'first engine'
    engineInputPort = 'start'
    engine = SystemSimulator.register_engine(engineName, "VIRTUAL_TIME", 1)
    model = ControlModel(0, Infinite, "control", engineName, 'start', socket.socket)

    ## engine 설정
    engine.insert_input_port(engineInputPort)
    engine.register_entity(model)
    engine.coupling_relation(
        None,   engineInputPort, 
        model,  model.get_name()
    )

    ## engine 실행
    engine.insert_external_event(engineInputPort, None)
    engine.simulate()


if __name__ == "__main__":
    main()
    