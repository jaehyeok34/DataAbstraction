from pyevsim.system_executor import SysExecutor
from parts import Parts
from pyevsim import BehaviorModelExecutor, SystemSimulator
from pyevsim.definition import Infinite
from queue import Queue, Empty
from parts_function import PartsFunction
from parts_db import PartsDB
import zmq
from typing import Tuple


class PartsManagement(BehaviorModelExecutor):
    UNPROCESSABLE   =   b'unprocessable'
    __baseParts     =   {
        # model name & engine input port    :   [input port,    function]
        '+'                            :   ['ADD',           PartsFunction.add],
        '-'                            :   ['SUB',           PartsFunction.sub],
    }
    __executed      =   'executed'
    
    #constructor
    def __init__(
            self,
            inputPort               =   'bootstrap',
            instantiate_time        =   ..., 
            destruct_time           =   ..., 
            name                    =   "bootstrap", 
            engine_name             =   "default"
    ) -> None:
        super().__init__(
            instantiate_time, 
            destruct_time, 
            name, 
            engine_name
        )
        self.__engine: SysExecutor  =   SystemSimulator.get_engine(engine_name)
        self.__parts                =   []
        self.__queue                =   Queue()
        self.__inputPort            =   inputPort
        self.__dbSocket             =   self.__initSocket()

        self.initBaseParts()
        self.insert_state(PartsManagement.__executed, 1000)
        self.insert_input_port(inputPort)

        self.init_state(PartsManagement.__executed)

    # property
    @property
    def parts(self) -> list:
        return self.__parts
    
    @property
    def inputPort(self) -> str:
        return self.__inputPort
    
    # override method
    def int_trans(self) -> None:
        pass

    def ext_trans(self, port, msg) -> None:
        pass

    def output(self) -> None:
        try:
            datas = self.__dequeue()
            socket, userID, partsName, msg = datas

            if partsName in self.__parts:       # base parts에 있을 경우
                self.__engine.insert_external_event(partsName, datas)
            else:                               # base parts에 없을 경우(DB에 요청)
                # DB에 있을 경우
                try:
                    key, info = PartsDB.getParts(self.__dbSocket, partsName)

                    print(f'system: no "{partsName}" in current engine')
                    print(f'system: added "{partsName}" parts from parts DB')
                    self.__addParts(
                        key = key, 
                        info = info
                    )
                    self.__engine.insert_external_event(partsName, datas)

                # DB에 없을 경우(None이 반환된 경우, TypeError)
                except:
                    # TODO: DB에 조차 없음, 유저에게 처리 불가능 전달
                    print(f'system: "{partsName}" parts not even in the parts DB')
                    print()
                    socket.send_multipart([userID, PartsManagement.UNPROCESSABLE])
                    pass
        # queue에 요청 사항이 없는 경우
        except Empty:
            pass

    # private method    
    def __initSocket(self) -> zmq.Socket:
        context = zmq.Context()
        socket = context.socket(zmq.DEALER)
        socket.setsockopt_string(zmq.IDENTITY, 'bootstrap')
        socket.connect(PartsDB.NET_INFO)

        return socket
    
    def __addParts(self, key: str, info: list) -> None:
        INPUT_PORT  =   0
        CALLBACK    =   1
        parts = Parts(
            info[INPUT_PORT],
            info[CALLBACK],
            0,
            Infinite,
            key,
            self.__engine.get_name()
        )
        self.__engine.insert_input_port(key)
        self.__engine.register_entity(parts)
        self.__engine.coupling_relation(
            None,   key,
            parts,  info[1]
        )
        self.__parts.append(key)

    def __dequeue(self) -> Tuple[zmq.Socket, bytes, str, list]:
        result = self.__queue.get(block = False)
        return tuple(result)

    # method
    def initBaseParts(self) -> None:
        for key in PartsManagement.__baseParts:
            self.__addParts(
                key, 
                [
                    PartsManagement.__baseParts[key][0],
                    PartsManagement.__baseParts[key][1]
                ]
            )
    
    def enqueue(
            self, 
            socket      :   zmq.Socket,
            userID      :   bytes,
            partsName   :   str,
            msg         :   Tuple[int, int]
    ) -> None:
        self.__queue.put([socket, userID, partsName, msg])