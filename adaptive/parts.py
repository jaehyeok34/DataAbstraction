from pyevsim import BehaviorModelExecutor
from pyevsim.definition import Infinite
import time

class Parts(BehaviorModelExecutor):
    # private static field
    __executed      =   'executed'
    __terminated    =   'terminated'

    def __init__(
        self, 
        inputPort,
        instantiate_time=..., 
        destruct_time=...,
        name=".",
        engine_name="default",
    ):
        super().__init__(
            instantiate_time, 
            destruct_time, 
            name, 
            engine_name
        )
        
        self.insert_state(Parts.__executed, 1000)
        self.insert_state(Parts.__terminated)
        self.insert_input_port(inputPort)

        self.init_state(Parts.__terminated)

    def int_trans(self):
        self.init_state(Parts.__terminated)

    def ext_trans(self, port, msg):
        self.init_state(Parts.__executed)

    def output(self):
        print(f'output of {self.get_name()} model')
        time.sleep(0.5)