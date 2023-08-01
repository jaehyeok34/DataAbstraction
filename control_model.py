import zmq
from codec import Codec
from enum import Enum
from pyevsim import SystemSimulator, BehaviorModelExecutor
from pyevsim.definition import *
from zmq_socket import ZmqSocket
import threading
import time

class ControlModel(BehaviorModelExecutor):
    class __State(Enum):
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

        self.insert_state(ControlModel.__State.execute, 1000)
        self.init_state(ControlModel.__State.terminate)

        self.insert_input_port(inputPort)
        self.init_state(ControlModel.__State.terminate)

        self.__socket = socket
        self.__remoteList: dict[str, str] = {}
        self._receiver = self.__generateRecieveThread()

    
    # method
    def __generateRecieveThread(self) -> threading.Thread:
        def recv():
            while True:
                reply = self.__socket.recv_multipart()
                dealerID = reply[0]
                datas = Codec.decode(reply[1:])
                print(f'reply: {datas[0]}')
                self.__remoteList[dealerID] = datas[0]

        receiver = threading.Thread(target = recv)
        receiver.start()
        return receiver
    
    def __sendCommand(self, command: list[bytes]) -> None:
        def isReadyAllRemote() -> bool:
            for remote in self.__remoteList:
                if self.__remoteList[remote] != ZmqSocket.Signal.readyToRecv:
                    return False
            
            return True
        
        if isReadyAllRemote():
            for remote in self.__remoteList:
                self.__socket.send_multipart([remote] + command)
        else:
            print('command failed: 아직 준비되지 않은 remote가 존재합니다.')


    # override method(BehaviorModelExecutor)
    def ext_trans(self, port, msg):
        print('model execute')
        self.init_state(ControlModel.__State.execute)

    def int_trans(self):
        self.init_state(ControlModel.__State.execute)

    def output(self):
        while True:
            command = Codec.encode(input('명령 입력 > '))
            if command:
                break

        self.__sendCommand(command)

        
def main():
    ## zmq socket 생성 및 바인딩
    socketManager = ZmqSocket(
        socketType = zmq.ROUTER,
        addr = 'tcp://127.0.0.1:3400'
    )

    ## simulation engine/model 생성
    engineName = 'first engine'
    engineInputPort = 'start'
    engine = SystemSimulator.register_engine(engineName, "VIRTUAL_TIME", 1)
    model = ControlModel(0, Infinite, "control", engineName, 'start', socketManager.socket)

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
    