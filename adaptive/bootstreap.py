from pyevsim.system_executor import SysExecutor
from parts import Parts
from pyevsim import BehaviorModelExecutor, SystemSimulator
from pyevsim.definition import Infinite
from queue import Queue, Empty
from parts_function import PartsFunction
from parts_db import PartsDB
import time
import zmq
import pickle
from typing import Tuple


class Bootstrap(BehaviorModelExecutor):
    UNPROCESSABLE   =   b'unprocessable'
    __baseParts     =   {
        # model name & engine input port    :   [input port,    function]
        'partsA'                            :   ['A',           PartsFunction.funcA],
        'partsB'                            :   ['B',           PartsFunction.funcB],
        'partsC'                            :   ['C',           PartsFunction.funcC],
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
    ):
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
        self.insert_state(Bootstrap.__executed, 1000)
        self.insert_input_port(inputPort)

        self.init_state(Bootstrap.__executed)

    # property
    @property
    def parts(self) -> list:
        return self.__parts
    
    @property
    def inputPort(self) -> str:
        return self.__inputPort
    
    # override method
    def int_trans(self):
        pass

    def ext_trans(self, port, msg):
        pass

    def output(self):
        try:
            socket, userID, partsName, msg = self.__dequeue()

            if partsName in self.__parts:       # base parts에 있을 경우
                self.__engine.insert_external_event(partsName, msg)
            else:                               # base parts에 없을 경우(DB에 요청)
                # DB에 있을 경우
                try:
                    key, info = PartsDB.getParts(self.__dbSocket, partsName)

                    print('DB에서 추가함')
                    self.__addParts(
                        key = key, 
                        info = info
                    )
                    self.__engine.insert_external_event(partsName, msg)

                # DB에 없을 경우(None이 반환된 경우, TypeError)
                except:
                    # TODO: DB에 조차 없음, 유저에게 처리 불가능 전달
                    print('db에도 없네유~')
                    socket.send_multipart([userID, Bootstrap.UNPROCESSABLE])
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
    
    def __addParts(self, key: str, info: list):
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
    def initBaseParts(self):
        for key in Bootstrap.__baseParts:
            self.__addParts(
                key, 
                [
                    Bootstrap.__baseParts[key][0],
                    Bootstrap.__baseParts[key][1]
                ]
            )
    
    def enqueue(
            self, 
            socket      :   zmq.Socket,
            userID      :   bytes,
            partsName   :   str,
            msg         :   Tuple[int, int]
    ):
        self.__queue.put([socket, userID, partsName, msg])