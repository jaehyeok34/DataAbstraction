from pyevsim import BehaviorModelExecutor, SystemSimulator, Infinite, SysMessage
from process_monitor import ProcessMonitor
import subprocess

class ProcessHandler(BehaviorModelExecutor) :
    # 필요한 기능 :
        # 1. 시작할 때 프로세스의 정보를 알고 있음
        # 2. 리시버한테 신호 받으면(spawn) 프로세스의 개수만큼 모니터를 만듬 (근데 여기서 돌리지는 않을것)

    def __init__(self, instance_time, destruct_time, name, engine_name, process_list) :
        BehaviorModelExecutor.__init__(self, instance_time, destruct_time, name, engine_name)
        self.init_state("Wait")
        self.insert_state("Wait", Infinite)
        self.insert_state("Spawn", 1)

        # self.insert_input_port("recv_pinfo")
        # self.insert_output_port("ack")
        self.insert_input_port("recv2hand")
        self.insert_output_port("hand2mon")

        # 프로세스 정보 (2차원 배열)
        self.process_list = process_list

    def ext_trans(self, port, msg):
        if port == "recv2hand" : 
            self._cur_state = "Spawn"
            
    
    def output(self):
        # print(self.get_name()," : ", self.get_cur_state())
        # 모니터한테 정보 주기
        if self._cur_state == "Spawn" :
            engine = SystemSimulator.get_engine(self.get_engine_name())
            # print(self.process_list)
            process_pid_list = []
            i = 1
            for process in self.process_list :
                pm = ProcessMonitor(0, Infinite, f"process_monitor_{i}", self.engine_name, process)
                print(f"process_monitor_{i} registered in {self.get_engine_name()}")
                engine.register_entity(pm)
                receiver = engine.get_entity("remote_receiver")[0]
                engine.coupling_relation(self, "hand2mon", pm, "hand2mon")
                engine.coupling_relation(pm, "mon2recv", receiver, "mon2recv")
                engine.coupling_relation(receiver, "recv2mon", pm, "recv2mon")
                # engine.coupling_relation(receiver[0], 'start', pm, 'start')
                # engine.coupling_relation(pm, 'ack', receiver[0], 'recv')
                i += 1
            
            msg = SysMessage(self.get_name(), "hand2mon")
            msg.insert("make_process")
            return msg
            

    def int_trans(self):
        if self._cur_state == "Spawn" :
            self._cur_state = "Wait"
    
    