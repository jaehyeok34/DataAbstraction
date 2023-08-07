from pyevsim import BehaviorModelExecutor, SysMessage
from pyevsim.definition import Infinite
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
    ):
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

    def int_trans(self):
        self.init_state(Parts.__terminated)

    def ext_trans(self, port, msg: SysMessage):
        msg = msg.retrieve()[0]
        print(f'{msg} 처리 결과: {self.__callback(msg)}')
        self.init_state(Parts.__executed)

    def output(self):
        print(f'{self.get_name()} parts 종료')