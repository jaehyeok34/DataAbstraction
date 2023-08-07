from pyevsim.system_executor import SysExecutor
from parts import Parts
from pyevsim import BehaviorModelExecutor, SystemSimulator
from pyevsim.definition import Infinite
from queue import Queue
import time


class Bootstrap(BehaviorModelExecutor):
    __baseParts     =   {
        # model name & engine input port    :   input port
        'partsA'                            :   'A',
        'partsB'                            :   'B',
        'partsC'                            :   'C',
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
        self.__parts                =   self.initBaseParts()
        self.__queue                =   Queue()
        self.__inputPort            =   inputPort

        self.insert_state(Bootstrap.__executed, 1000)
        self.insert_input_port(inputPort)

        self.init_state(Bootstrap.__executed)

    # property
    @property
    def parts(self) -> list:
        return self.__parts
    
    @property
    def queue(self) -> Queue:
        return self.__queue
    
    @property
    def inputPort(self) -> str:
        return self.__inputPort
    
    # override method
    def int_trans(self):
        pass

    def ext_trans(self, port, msg):
        pass

    def output(self):
        print(f'output of {self.get_name()} model')
        time.sleep(2)

    # method
    def initBaseParts(self) -> list:
        for key in Bootstrap.__baseParts:
            parts = Parts(
                Bootstrap.__baseParts[key],
                0,
                Infinite, 
                key,
                self.__engine.get_name()
            )
            self.__engine.insert_input_port(key)
            self.__engine.register_entity(parts)
            self.__engine.coupling_relation(
                None,   key,
                parts,  Bootstrap.__baseParts[key]
            )
            # engine.insert_external_event(key, None)
        
        return list(Bootstrap.__baseParts.keys())
