from pyevsim.definition import Infinite
import zmq
from codec import Codec
from zmq_socket import ZmqSocket
from pyevsim import BehaviorModelExecutor, SystemSimulator
from enum import Enum


class RemoteModel(BehaviorModelExecutor):
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
        self.insert_state(RemoteModel.__State.execute, 1000)
        self.init_state(RemoteModel.__State.terminate)

        self.insert_input_port(inputPort)
        self.init_state(RemoteModel.__State.terminate)

        self.__socket = socket

    # override method(BehaviorModelExecutor)
    def ext_trans(self, port, msg):
        print('model execute')
        self.init_state(RemoteModel.__State.execute)

    def int_trans(self):
        self.init_state(RemoteModel.__State.execute)

    def output(self):
        while True:
            reply = Codec.decode(self.__socket.recv_multipart())
            print(reply)
            

            # if command == Codec.Commands.run.value:
            #     ## TODO: 프로세스 실행 로직 구현
            #     print(f'running... ({datas[0]})')
            # elif command == Codec.Commands.stop.value:
            #     ## TODO: 프로세스 종료 로직 구현
            #     print(f'stop... ({datas[0]})')
            # else:
            #     pass



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
    model = RemoteModel(0, Infinite, "remote", engineName, 'start', socketManager.socket)

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


