from pyevsim import BehaviorModelExecutor, SysMessage
from pyevsim.definition import Infinite
import zmq
import time

class Parts(BehaviorModelExecutor):
    # private static field
    __executed      =   'executed'
    __terminated    =   'terminated'

    def __init__(
        self, 
        inputPort   :   str,
        callback    :   callable,
        instantiate_time        =   ..., 
        destruct_time           =   ...,
        name                    =   ".",
        engine_name             =   "default",
    ) -> None:
        super().__init__(
            instantiate_time, 
            destruct_time, 
            name, 
            engine_name
        )
        self.__callback = callback
        
        self.insert_state(Parts.__executed, 1000)
        self.insert_state(Parts.__terminated)
        self.insert_input_port(inputPort)

        self.init_state(Parts.__terminated)

    def int_trans(self) -> None:
        self.init_state(Parts.__terminated)

    def ext_trans(self, port, msg: SysMessage) -> None:
        msg: tuple[zmq.Socket, bytes, str, list] = msg.retrieve()[0]
        socket, userID, partsName, msg = msg
        result: int = self.__callback(msg)
        print(f'"{partsName}" processing complete: {result}')
        socket.send_multipart([userID, str(result).encode()])
        self.init_state(Parts.__executed)

    def output(self) -> None:
        print(f'end "{self.get_name()}" parts')
        print()